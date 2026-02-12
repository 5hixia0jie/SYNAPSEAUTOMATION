from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
import glob
import sys


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def find_ffmpeg() -> str | None:
    """
    Prefer project-local full ffmpeg, then bundled Playwright ffmpeg, then user's Playwright ffmpeg, then fall back to PATH.
    """
    root = _repo_root()
    
    # 1. Check project-local full ffmpeg (preferred)
    full_ffmpeg_dir = root / "ffmpeg-8.0.1-essentials_build" / "bin"
    if full_ffmpeg_dir.exists():
        ffmpeg_exe = full_ffmpeg_dir / "ffmpeg.exe" if sys.platform == "win32" else full_ffmpeg_dir / "ffmpeg"
        if ffmpeg_exe.exists():
            print(f"Using project-local full ffmpeg: {ffmpeg_exe}")
            return str(ffmpeg_exe)

    # 2. Check repo-root bundled ffmpeg
    bundled = root / ".playwright-browsers"
    if bundled.exists():
        if sys.platform == "win32":
            patterns = [
                str(bundled / "ffmpeg-*" / "ffmpeg.exe"),
                str(bundled / "ffmpeg-*" / "ffmpeg-win64" / "ffmpeg.exe"),
            ]
        else:
            patterns = [
                str(bundled / "ffmpeg-*" / "ffmpeg"),
                str(bundled / "ffmpeg-*" / "ffmpeg-linux" / "ffmpeg"),
                str(bundled / "ffmpeg-*" / "ffmpeg-mac" / "ffmpeg"),
            ]
        for p in patterns:
            matches = sorted(glob.glob(p))
            if matches:
                exe = matches[-1]
                if Path(exe).exists():
                    print(f"Using bundled Playwright ffmpeg: {exe}")
                    return exe

    # 3. Check user's Playwright ffmpeg (Windows)
    if sys.platform == "win32":
        import os
        user_profile = os.environ.get("USERPROFILE")
        if user_profile:
            ms_playwright = Path(user_profile) / "AppData" / "Local" / "ms-playwright"
            if ms_playwright.exists():
                patterns = [
                    str(ms_playwright / "ffmpeg-*" / "ffmpeg-win64.exe"),
                    str(ms_playwright / "ffmpeg-*" / "ffmpeg.exe"),
                ]
                for p in patterns:
                    matches = sorted(glob.glob(p))
                    if matches:
                        exe = matches[-1]
                        if Path(exe).exists():
                            print(f"Using user's Playwright ffmpeg: {exe}")
                            return exe

    # 4. Fall back to PATH
    path_ffmpeg = shutil.which("ffmpeg")
    if path_ffmpeg:
        print(f"Using system PATH ffmpeg: {path_ffmpeg}")
    return path_ffmpeg


def extract_first_frame(video_path: str, out_path: str, *, overwrite: bool = True) -> None:
    """
    Extract the first representative frame from a video as a PNG.
    Uses full-featured ffmpeg for reliable video processing.
    """
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found (full ffmpeg required for video processing)")

    src = Path(video_path)
    dst = Path(out_path)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        return

    # Use full-featured ffmpeg to extract first frame
    # -ss 0.1 to avoid black first frame in some codecs
    cmd = [
        ffmpeg,
        "-y" if overwrite else "-n",
        "-ss",
        "0.1",
        "-i",
        str(src),
        "-frames:v",
        "1",
        "-vf",
        "scale=iw:ih",
        str(dst),
    ]
    
    print(f"Extracting first frame with ffmpeg: {cmd}")
    
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    if proc.returncode != 0 or not dst.exists():
        stderr = (proc.stderr or "").strip()
        stdout = (proc.stdout or "").strip()
        error_msg = f"ffmpeg extract_first_frame failed: {stderr[:1000]}"
        if stdout:
            error_msg += f"\nstdout: {stdout[:500]}"
        raise RuntimeError(error_msg)
    
    print(f"Successfully extracted first frame: {dst}")

