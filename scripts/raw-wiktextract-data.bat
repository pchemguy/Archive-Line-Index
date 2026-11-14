@echo off

set "REPO=H:\GitHub\Archive-Stream"
set "PYTHONPATH=%REPO%\src;%PYTHONPATH%"

python -m archive_stream "%~dpn0.7z"
