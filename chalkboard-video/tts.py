"""edge-tts with the session proxy CA; usage: tts.py OUT.mp3 TEXT [RATE]"""
import asyncio, ssl, sys
import edge_tts, edge_tts.communicate as c
c._SSL_CTX = ssl.create_default_context(cafile="/root/.ccr/ca-bundle.crt")
async def main(out, text, rate="+0%"):
    comm = edge_tts.Communicate(text, "zh-CN-YunjianNeural", rate=rate, boundary="WordBoundary")
    subs = []
    with open(out, "wb") as f:
        async for ch in comm.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] in ("WordBoundary", "SentenceBoundary"):
                subs.append((ch["offset"] / 1e7, ch["duration"] / 1e7, ch["text"]))
    with open(out + ".words.tsv", "w") as f:
        for o, d, t in subs: f.write(f"{o:.3f}\t{d:.3f}\t{t}\n")
asyncio.run(main(*sys.argv[1:]))
