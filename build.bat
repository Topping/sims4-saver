@echo off
echo Building Sims Saver executable...

REM Check if uv is available
uv --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: uv is not installed. Please install uv first.
    echo Visit: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
uv sync

REM Build the executable
echo Building executable...
uv run pyinstaller sims-saver.spec

REM Check if build was successful
if exist dist\Sims4-Save-Helper.exe (
    echo.
    echo Build successful! Executable created at: dist\Sims4-Save-Helper.exe
    echo.
    echo You can now run the executable or distribute it to other Windows machines.
) else (
    echo.
    echo Build failed. Please check the error messages above.
)

pause
