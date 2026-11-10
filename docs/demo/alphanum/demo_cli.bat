@echo off
setlocal

set "REPO=%~dp0..\..\.."
set "PYTHONPATH=%REPO%\src;%PYTHONPATH%"
set "FORMATS=txt 7z zip tar tbz tgz"

for %%F in (%FORMATS%) do (
    python -m archive_stream "%~dp0%%~F\demo.%%~F" || exit /b 1
)
