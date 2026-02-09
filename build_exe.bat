@echo off
cd /d "%~dp0"
call .venv\Scripts\activate
pyinstaller --noconsole --onefile --add-data "NanumGothic.ttf;." --name "MarkdownToPDF" gui_converter.py
pause
