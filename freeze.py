import sys

from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
	base = "Win32GUI"

setup(
	name="GXS x264 Frontend",
	version="0.42",
	description="x264, ffmpeg, neroAacEnc, mkvmerge frontend",
	executables=[Executable("GXSx264Frontend.py", base=base)])
