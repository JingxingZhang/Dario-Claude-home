"""Beat / band-energy analysis -> audio.json (30 fps envelopes + beat times)."""
import librosa, numpy as np, json, sys
y, sr = librosa.load(sys.argv[1], sr=22050)
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units='time')
hop = int(sr / 30)
S = np.abs(librosa.stft(y, n_fft=2048, hop_length=hop)); f = librosa.fft_frequencies(sr=sr, n_fft=2048)
def band(a, b):
    v = S[(f >= a) & (f < b)].mean(0); return v / np.percentile(v, 98)
rms = librosa.feature.rms(y=y, hop_length=hop)[0]; rms = rms / np.percentile(rms, 98)
on = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop); on = on / np.percentile(on, 99)
n = len(rms); r = lambda a: [round(float(x), 3) for x in a[:n]]
json.dump(dict(fps=30, dur=len(y) / sr, tempo=float(np.atleast_1d(tempo)[0]), beats=[round(float(b), 3) for b in beats],
               rms=r(rms), low=r(band(20, 150)), mid=r(band(150, 2000)), high=r(band(2000, 9000)), onset=r(on)),
          open(sys.argv[2] if len(sys.argv) > 2 else 'audio.json', 'w'))
