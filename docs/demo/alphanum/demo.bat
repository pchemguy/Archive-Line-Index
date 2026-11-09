@echo off
setlocal

for %%I in ("%~dp0..\..\..") do set "REPO=%%~fI"
set "PYTHONPATH=%REPO%\src;%PYTHONPATH%"
set "FORMATS=txt 7z zip tar tbz tgz"

for %%F in (%FORMATS%) do (
    python -m archive_line_index "%~dp0%%~F\demo.%%~F" || exit /b 1
)
