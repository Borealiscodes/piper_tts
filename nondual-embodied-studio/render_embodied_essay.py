import itertools
import json
import math
import random
import struct
import subprocess
import sys
import wave
from pathlib import Path

from anti_sycophancy_linter import lint_dialogue_script
from phonetic_guard import normalize_for_speech

def synthesize_stillness_bed(num_frames: int, sample_rate: int = 22050, gain: float = 0.03) -> list[int]:
    rng = random.Random(24393275)
    brown = 0.0
    lp = 0.0
    alpha = (2.0 * math.pi * 680.0) / (sample_rate + 2.0 * math.pi * 680.0)
    out = []
    for _ in range(num_frames):
        white = rng.uniform(-1.0, 1.0)
        brown = (brown + 0.03 * white) / 1.03
        lp = lp + alpha * (brown * 2.5 - lp)
        out.append(int(max(-32767, min(32767, lp * gain * 32767.0))))
    return out

def render_dialogue(script_path: Path, model_path: Path, out_wav: Path, length_scale: float = 1.12) -> Path:
    doc = json.loads(script_path.read_text(encoding="utf-8"))
    verdict = lint_dialogue_script(doc)
    if not verdict["valid"]:
        raise ValueError("Guardrail lint failed: " + "; ".join(verdict["errors"]))

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_wav.parent / "_tmp_turns"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    pcm_samples = []
    sample_rate = 22050

    for idx, turn in enumerate(doc["turns"]):
        turn_wav = tmp_dir / f"turn_{idx:02d}.wav"
        spoken_line = normalize_for_speech(turn["text"]).strip() + "\n"

        subprocess.run(
            [
                sys.executable, "-m", "piper",
                "--model", str(model_path),
                "--data-dir", ".",
                "--length-scale", str(length_scale),
                "--output_file", str(turn_wav),
            ],
            input=spoken_line.encode("utf-8"),
            check=True,
        )

        with wave.open(str(turn_wav), "rb") as wf:
            sample_rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
            pcm_samples.extend(struct.unpack(f"<{len(frames)//2}h", frames))

        pause_frames = int(sample_rate * (int(turn.get("pause_ms", 900)) / 1000.0))
        pcm_samples.extend(itertools.repeat(0, pause_frames))
        turn_wav.unlink(missing_ok=True)

    tmp_dir.rmdir()
    bed = synthesize_stillness_bed(len(pcm_samples), sample_rate=sample_rate)
    mixed = [max(-32767, min(32767, v + b)) for v, b in zip(pcm_samples, bed)]

    with wave.open(str(out_wav), "wb") as out_wf:
        out_wf.setnchannels(1)
        out_wf.setsampwidth(2)
        out_wf.setframerate(sample_rate)
        out_wf.writeframes(struct.pack(f"<{len(mixed)}h", *mixed))

    return out_wav

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 render_embodied_essay.py <script.json> <voice.onnx> <output.wav>")
        sys.exit(1)
    args = list(sys.argv)
    result = render_dialogue(Path(args.pop(1)), Path(args.pop(1)), Path(args.pop(1)))
    print(f"Rendered embodied audio essay: {result}")
