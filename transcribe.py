"""Transcribe CEO videos via ffmpeg stream + faster-whisper.
Extracts audio-only from each Dropbox share URL (not the full video),
transcribes locally, and writes SRT files to transcripts/.

Usage: python transcribe.py
"""
import os
import sys
import subprocess
import json
import time
from pathlib import Path

# Refresh PATH so ffmpeg from winget is found
def find_ffmpeg():
    for candidate in [
        "ffmpeg",
        r"C:\Program Files\Gyan FFmpeg\ffmpeg-full_build\bin\ffmpeg.exe",
        r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
    ]:
        try:
            r = subprocess.run([candidate, "-version"], capture_output=True, text=True)
            if r.returncode == 0:
                return candidate
        except FileNotFoundError:
            continue
    # Probe the winget install location
    import glob
    for pattern in [
        r"C:\Users\*\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg-*-full_build\bin\ffmpeg.exe",
        r"C:\ProgramData\Microsoft\WinGet\Packages\Gyan.FFmpeg*\ffmpeg-*-full_build\bin\ffmpeg.exe",
    ]:
        hits = glob.glob(pattern)
        if hits:
            return hits[0]
    return None

FFMPEG = find_ffmpeg()
if not FFMPEG:
    print("ERROR: ffmpeg not found. Restart terminal and try again (so PATH picks up winget install).")
    sys.exit(1)
print(f"Using ffmpeg: {FFMPEG}")

from faster_whisper import WhisperModel

BASE = Path(__file__).parent
TRANSCRIPTS = BASE / "transcripts"
AUDIO = BASE / "audio_temp"
TRANSCRIPTS.mkdir(exist_ok=True)
AUDIO.mkdir(exist_ok=True)

VIDEOS = [
    {"id": 1, "title": "Voter Registration",
     "url": "https://dl.dropboxusercontent.com/scl/fi/tx675r3bx1l1wgiyip6qk/CEO-Video-1-Voter-Reg-FNL.mp4?rlkey=6witza74r7qgh0a01ggj957jy&st=yapsif9p"},
    {"id": 2, "title": "L&A Testing",
     "url": "https://dl.dropboxusercontent.com/scl/fi/bhqit3dd4sy53q1ycp7ew/CEO-Video-2-L_A-FNL.mp4?rlkey=ewho3uiw76l2pg1x75q06x7tf&st=erocf2oo"},
    {"id": 3, "title": "Tour",
     "url": "https://dl.dropboxusercontent.com/scl/fi/9fo0nqqytpp5vmqzsq0b2/CEO-Video-3-Tour-FNL.mp4?rlkey=xvzabg6lqnq40mityg70dbuad&st=jzdbp2co"},
    {"id": 4, "title": "Poll Worker Training & In-Person Voting",
     "url": "https://dl.dropboxusercontent.com/scl/fi/99ttaryuxz0eg4rfg4am6/CEO-Video-4-PollWorkerTraining_Voting-v3.mp4?rlkey=qin10hau3eyt4rk2dtn03jfaw"},
    {"id": 5, "title": "Ballot Collection",
     "url": "https://dl.dropboxusercontent.com/scl/fi/v13jatr9hah4knnxmp4mz/CEO-Video-5-Ballot-Collection-FNL.mp4?rlkey=mq0djthx3snqi4r7imb7g6klp&st=8gwalojc"},
    {"id": 6, "title": "Vote By Mail Scanning",
     "url": "https://dl.dropboxusercontent.com/scl/fi/k9ezeflv0e7795ppy7p94/CEO-Video-6-VoteByMail-Scanning-FNL.mp4?rlkey=i0zyt8hixwoymzhc62prt7ujd&st=eesyv0oh"},
    {"id": 7, "title": "Signature Check",
     "url": "https://dl.dropboxusercontent.com/scl/fi/nbqgh8wjdca8sxq09mdwv/CEO-Video-7-Signature-Check-FNL.mp4?rlkey=077y9rwnidb7q8qcrpb60q1r8&st=00ql2r1f"},
    {"id": 8, "title": "Extraction",
     "url": "https://dl.dropboxusercontent.com/scl/fi/42fura9d9glnawgggyiqm/CEO-Video-8-Extraction-FNL.mp4?rlkey=fiv7u56tfks2pchkeri2wjnhx&st=rqble03w"},
    {"id": 11, "title": "Canvass",
     "url": "https://dl.dropboxusercontent.com/scl/fi/heoqmir921c9d0qkmn1i4/CEO-Video-11-Canvass-FNL.mp4?rlkey=7wajfdbeb395e3f620100y8iz&st=24xjo08o"},
]


def extract_audio(video_url, out_path):
    """Stream-extract mono 16kHz MP3 audio from video URL."""
    cmd = [
        FFMPEG, "-y", "-loglevel", "error",
        "-i", video_url,
        "-vn",              # no video
        "-ac", "1",          # mono
        "-ar", "16000",      # 16kHz (whisper's native rate)
        "-codec:a", "libmp3lame",
        "-b:a", "64k",
        str(out_path),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr}")


def fmt_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(segments, out_path):
    lines = []
    for i, seg in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{fmt_srt_time(seg.start)} --> {fmt_srt_time(seg.end)}")
        lines.append(seg.text.strip())
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    print("Loading faster-whisper model (base, int8 on CPU)...")
    t0 = time.time()
    model = WhisperModel("base", device="cpu", compute_type="int8")
    print(f"Model loaded in {time.time() - t0:.1f}s")

    for v in VIDEOS:
        srt_path = TRANSCRIPTS / f"video-{v['id']}.srt"
        if srt_path.exists():
            print(f"[{v['id']}] Already transcribed: {srt_path.name}")
            continue

        audio_path = AUDIO / f"video-{v['id']}.mp3"
        print(f"\n[{v['id']}] {v['title']}")

        # Extract audio
        if not audio_path.exists():
            print(f"  Extracting audio via ffmpeg...")
            t0 = time.time()
            try:
                extract_audio(v["url"], audio_path)
                print(f"  Audio: {audio_path.stat().st_size / 1024:.0f} KB in {time.time() - t0:.0f}s")
            except Exception as e:
                print(f"  FAILED audio extract: {e}")
                continue
        else:
            print(f"  Audio already cached: {audio_path.name}")

        # Transcribe
        print(f"  Transcribing...")
        t0 = time.time()
        try:
            segments, info = model.transcribe(str(audio_path), beam_size=1, vad_filter=True)
            segs = list(segments)  # force iteration
            write_srt(segs, srt_path)
            print(f"  {len(segs)} segments, duration={info.duration:.0f}s, wrote {srt_path.name} in {time.time() - t0:.0f}s")
        except Exception as e:
            print(f"  FAILED transcribe: {e}")
            continue

    print("\nDONE.")


if __name__ == "__main__":
    main()
