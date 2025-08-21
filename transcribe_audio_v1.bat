@REM python .\transcribe_audio_v1.py -i .\mp3-test --ffmpeg "..\apps\ffmpeg\bin\ffmpeg.exe"


@echo off
cd /d %~dp0
python transcribe_audio_v1.py -i .\mp3 --ffmpeg "..\apps\ffmpeg\bin\ffmpeg.exe"
pause
