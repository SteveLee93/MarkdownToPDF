@echo off
cd /d "%~dp0"
call .venv\Scripts\activate

REM Try to convert user provided png (icon.png or app_icon.png) to ico
python create_ico.py

REM Check if icon.ico exists now
if not exist icon.ico (
    echo WARNING: No icon.ico found. Building without custom icon.
    goto :BUILD_NO_ICON
)

echo Building EXE with icon.ico...
pyinstaller --noconsole --onefile --add-data "NanumGothic.ttf;." --add-data "icon.ico;." --icon="icon.ico" --name "MarkdownToPDF" gui_converter.py
goto :END

:BUILD_NO_ICON
echo Building EXE without custom icon...
pyinstaller --noconsole --onefile --add-data "NanumGothic.ttf;." --name "MarkdownToPDF" gui_converter.py

:END
pause
