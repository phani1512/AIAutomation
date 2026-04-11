@echo off
REM ============================================================
REM  Consolidate Test Folders
REM  Removes duplicates and moves uploads to resources/
REM ============================================================

echo.
echo ============================================================
echo  Consolidating Test Folders
echo ============================================================
echo.

cd /d "%~dp0"

echo Step 1: Moving uploads to resources/uploads/...
if exist "resources\test_data\uploads" (
    if not exist "resources\uploads" (
        mkdir "resources\uploads" 2>nul
    )
    xcopy "resources\test_data\uploads\*" "resources\uploads\" /E /I /Y >nul 2>&1
    echo   - Moved uploads from test_data to resources/
)

echo.
echo Step 2: Removing duplicate test_data folders...

REM Remove duplicate test_cases
if exist "resources\test_data\test_cases" (
    rmdir /S /Q "resources\test_data\test_cases" >nul 2>&1
    echo   - Removed resources/test_data/test_cases/ (using root test_cases/)
)

REM Remove duplicate test_sessions
if exist "resources\test_data\test_sessions" (
    rmdir /S /Q "resources\test_data\test_sessions" >nul 2>&1
    echo   - Removed resources/test_data/test_sessions/
)

REM Remove duplicate recorder_tests
if exist "resources\test_data\recorder_tests" (
    rmdir /S /Q "resources\test_data\recorder_tests" >nul 2>&1
    echo   - Removed resources/test_data/recorder_tests/ (using test_cases/recorder/)
)

REM Remove empty test_data folder
if exist "resources\test_data\uploads" (
    rmdir /S /Q "resources\test_data\uploads" >nul 2>&1
)
if exist "resources\test_data" (
    rmdir "resources\test_data" >nul 2>&1
    echo   - Removed empty resources/test_data/ folder
)

echo.
echo Step 3: Removing empty test_sessions from root...
if exist "test_sessions" (
    rmdir "test_sessions" >nul 2>&1
    echo   - Removed empty test_sessions/ folder from root
)

echo.
echo ============================================================
echo  Consolidation Complete!
echo ============================================================
echo.
echo New structure:
echo   test_cases/           - All test cases at project root
echo     ├─ builder/         - Test Builder tests
echo     └─ recorder/        - Recorder tests
echo   test_suites/          - Test suites at project root
echo   resources/uploads/    - File uploads
echo   resources/ml_data/    - ML and dataset files
echo.
echo IMPORTANT: Code paths will be updated automatically.
echo Please restart the server after running path update script.
echo.
pause
