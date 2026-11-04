#!/usr/bin/env python3
"""Assemble the 30s short from edl.json.

Each shot is resolved in this order:
  1. shot["file"] if given (e.g. "clips/S05_take3.mp4")
  2. clips/<ID>.mp4 / .mov / .webm      -> trimmed video clip
  3. stills/<ID>.png / .jpg / .webp     -> animatic frame with a slow push-in
  4. a grey slate with the shot id      -> placeholder

Cut points come from the EDL timeline (start/end, snapped to the music's
downbeats); "in" is the source in-point inside the generated clip.

Usage:  python3 tools/build_edit.py [edl.json] [-o out/name.mp4] [--preview]
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VIDEO_EXT = (".mp4", ".mov", ".webm", ".mkv")
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(" ".join(map(str, cmd)) + "\n" + r.stderr[-3000:])
        raise SystemExit(f"ffmpeg failed ({r.returncode})")


def probe_duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def has_audio(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                        "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    return bool(r.stdout.strip())


TARGET_MEAN_DB = -33.0


def level_gain(path, t_in, dur):
    """Gain that brings this shot's ambience to a common mean level (clamped)."""
    r = subprocess.run(["ffmpeg", "-v", "info", "-ss", f"{t_in:.3f}", "-t", f"{dur:.3f}", "-i", str(path),
                        "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True)
    for line in r.stderr.splitlines():
        if "mean_volume:" in line:
            try:
                mean = float(line.split("mean_volume:")[1].split("dB")[0])
            except ValueError:
                break
            return max(-12.0, min(8.0, TARGET_MEAN_DB - mean))
    return 0.0


def resolve(shot):
    if shot.get("file"):
        p = ROOT / shot["file"]
        if p.exists():
            return p
        print(f"  ! {shot['id']}: {shot['file']} not found, falling back")
    for folder, exts in (("clips", VIDEO_EXT), ("stills", IMAGE_EXT)):
        for ext in exts:
            p = ROOT / folder / f"{shot['id']}{ext}"
            if p.exists():
                return p
    return None


def render_shot(shot, src, nframes, fps, W, H, out):
    dur = nframes / fps
    fit = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
           f"crop={W}:{H},setsar=1")
    silent = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    enc = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-pix_fmt", "yuv420p",
           "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2",
           "-frames:v", str(nframes), "-t", f"{dur:.4f}", str(out)]

    if src is None:
        label = shot["id"]
        vf = (f"drawtext=text='{label}':fontcolor=0x555555:fontsize=120:"
              f"x=(w-tw)/2:y=(h-th)/2")
        run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
             "-i", f"color=c=0xd9dcd6:s={W}x{H}:r={fps}:d={dur:.4f}", *silent,
             "-vf", vf, "-map", "0:v", "-map", "1:a", *enc])
        return "slate"

    if src.suffix.lower() in IMAGE_EXT:
        # slow push-in so the animatic does not feel frozen
        z = f"zoompan=z='1+0.04*on/{max(nframes - 1, 1)}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nframes}:s={W}x{H}:fps={fps}"
        run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(src), *silent,
             "-vf", f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},{z},setsar=1",
             "-map", "0:v", "-map", "1:a", *enc])
        return "still"

    t_in = float(shot.get("in", 0.0))
    speed = float(shot.get("speed", 1.0))
    src_dur = probe_duration(src)
    need = dur * speed
    if t_in + need > src_dur + 0.01:
        print(f"  ! {shot['id']}: in={t_in:.2f}s + {need:.2f}s exceeds clip length "
              f"{src_dur:.2f}s; last frame will be held")
    vf = f"setpts=(PTS-STARTPTS)/{speed},fps={fps},{fit},tpad=stop_mode=clone:stop_duration=5"
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{t_in:.4f}", "-i", str(src)]
    if has_audio(src):
        gain = level_gain(src, t_in, need)
        af = (f"asetpts=PTS-STARTPTS,atempo={speed},volume={gain:.1f}dB,"
              f"afade=t=in:d=0.02,afade=t=out:st={max(dur - 0.04, 0):.3f}:d=0.04,apad")
        cmd += ["-vf", vf, "-af", af, "-map", "0:v", "-map", "0:a", *enc]
    else:
        cmd += [*silent, "-vf", vf, "-map", "0:v", "-map", "1:a", *enc]
    run(cmd)
    return "clip"


def db(x):
    return f"{x}dB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("edl", nargs="?", default=str(ROOT / "edl.json"))
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--preview", action="store_true", help="960x540, faster")
    ap.add_argument("--keep", action="store_true", help="keep temp segments for debugging")
    args = ap.parse_args()

    edl = json.loads(Path(args.edl).read_text())
    fps = edl["fps"]
    W, H = (960, 540) if args.preview else (edl["width"], edl["height"])
    shots = edl["shots"]
    total = shots[-1]["end"]
    total_frames = round(total * fps)
    out = Path(args.out) if args.out else ROOT / "out" / ("preview.mp4" if args.preview else "red_scarf.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)

    tmp = Path(tempfile.mkdtemp(prefix=".edit_", dir=out.parent))
    try:
        listing = []
        print(f"Timeline {total:.2f}s @ {fps}fps, {len(shots)} shots")
        for s in shots:
            f0, f1 = round(s["start"] * fps), round(s["end"] * fps)
            n = f1 - f0
            src = resolve(s)
            seg = tmp / f"{s['id']}.mkv"
            kind = render_shot(s, src, n, fps, W, H, seg)
            print(f"  {s['id']}  {s['start']:6.2f}-{s['end']:6.2f}s  {n:3d}f  {kind:5s}  "
                  f"{src.relative_to(ROOT) if src else '-'}")
            listing.append(f"file '{seg}'")
        (tmp / "list.txt").write_text("\n".join(listing) + "\n")
        joined = tmp / "joined.mkv"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
             "-i", str(tmp / "list.txt"), "-c", "copy", str(joined)])

        g = edl.get("grade", {})
        vf = [f"eq=saturation={g.get('saturation', 1.0)}"]
        if g.get("grain"):
            vf.append(f"noise=alls={g['grain']}:allf=t")
        if g.get("vignette"):
            vf.append(f"vignette=angle={g['vignette']}")
        if g.get("fade_in"):
            vf.append(f"fade=t=in:st=0:d={g['fade_in']}")
        if g.get("fade_out_to_white"):
            d = g["fade_out_to_white"]
            vf.append(f"fade=t=out:st={total - d:.3f}:d={d}:color=white")
        vf.append("format=yuv420p")

        m = edl.get("music", {})
        mfile = ROOT / m.get("file", "")
        cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(joined)]
        mix_inputs = []
        if m.get("file") and mfile.exists():
            cmd += ["-ss", str(m.get("offset", 0.0)), "-t", f"{total:.3f}", "-i", str(mfile)]
            fo = m.get("fade_out", 1.0)
            mix_inputs.append(
                f"[1:a]aresample=48000,volume={db(m.get('gain_db', 0))},"
                f"afade=t=out:st={total - fo:.3f}:d={fo}[mus]")
        else:
            print(f"  ! music file {m.get('file')} missing -> silent score")
        lufs = edl.get("master_lufs")
        master = f"loudnorm=I={lufs}:TP=-1.5:LRA=11,aresample=48000" if lufs else "anull"
        cad = edl.get("clip_audio_db")
        af_parts, labels = list(mix_inputs), []
        if mix_inputs:
            labels.append("[mus]")
        if cad is not None:
            af_parts.append(f"[0:a]volume={db(cad)}[sfx]")
            labels.append("[sfx]")
        if labels:
            af_parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,"
                            f"{master},alimiter=limit=0.95,apad[aout]")
        else:
            af_parts.append("anullsrc=r=48000:cl=stereo[aout]")
        fc = f"[0:v]{','.join(vf)}[vout];" + ";".join(af_parts)
        cmd += ["-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
                "-frames:v", str(total_frames), "-t", f"{total:.3f}",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-maxrate", "16M", "-bufsize", "32M", "-profile:v", "high",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-r", str(fps), str(out)]
        run(cmd)
        print(f"-> {out}  ({probe_duration(out):.2f}s)")
    finally:
        if args.keep:
            print(f"  temp kept at {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
