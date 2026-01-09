@echo off
setlocal ENABLEDELAYEDEXPANSION

REM ============================================
REM RP9 Recursive Cleanup Script
REM Removes: desktop.ini and *.py
REM Scope: current directory and all subfolders
REM ============================================

REM --- Resolve base directory (where script is) ---
set "BASE_DIR=%~dp0"
set "BASE_DIR=%BASE_DIR:~0,-1%"

REM --- Log file ---
set "LOG_FILE=%BASE_DIR%\RP9_cleanup.log"

echo ============================================ > "%LOG_FILE%"
echo RP9 Recursive Cleanup Started >> "%LOG_FILE%"
echo Base directory: "%BASE_DIR%" >> "%LOG_FILE%"
echo Timestamp: %DATE% %TIME% >> "%LOG_FILE%"
echo ============================================ >> "%LOG_FILE%"

echo.
echo Base directory:
echo "%BASE_DIR%"
echo.

REM ============================================
REM Remove desktop.ini files
REM ============================================
echo Removing desktop.ini files...
echo --- desktop.ini --- >> "%LOG_FILE%"

for /R "%BASE_DIR%" %%F in (desktop.ini) do (
    echo Deleting: "%%F"
    echo Deleted: "%%F" >> "%LOG_FILE%"
    del /F /Q "%%F" >nul 2>&1
)

REM ============================================
REM Remove *.py files
REM ============================================
echo Removing *.py files...
echo --- *.py --- >> "%LOG_FILE%"

for /R "%BASE_DIR%" %%F in (*.py) do (
    echo Deleting: "%%F"
    echo Deleted: "%%F" >> "%LOG_FILE%"
    del /F /Q "%%F" >nul 2>&1
)

REM ============================================
REM END
REM ============================================
echo.
echo ============================================
echo Cleanup completed.
echo Log written to:
echo "%LOG_FILE%"
echo ============================================

pause
END
