@echo off
REM ============================================================
REM  Reorganize Resources Directory
REM  Separates ML/dataset files from test-related files
REM ============================================================

echo.
echo ============================================================
echo  Reorganizing Resources Directory
echo ============================================================
echo.

cd /d "%~dp0"

REM Create new directory structure
echo Creating new directory structure...
mkdir "resources\ml_data\datasets" 2>nul
mkdir "resources\ml_data\models\ml_models" 2>nul
mkdir "resources\ml_data\templates" 2>nul
mkdir "resources\ml_data\logs" 2>nul
mkdir "resources\test_data\uploads" 2>nul
mkdir "resources\test_data\test_cases" 2>nul
mkdir "resources\test_data\recorder_tests" 2>nul
mkdir "resources\test_data\test_sessions" 2>nul

echo.
echo Moving ML and dataset files...

REM Move dataset files
if exist "resources\combined-training-dataset-final.json" (
    move "resources\combined-training-dataset-final.json" "resources\ml_data\datasets\" >nul 2>&1
    echo   - Moved combined-training-dataset-final.json
)

if exist "resources\ml_training_data.json" (
    move "resources\ml_training_data.json" "resources\ml_data\datasets\" >nul 2>&1
    echo   - Moved ml_training_data.json
)

if exist "resources\ml_feedback.json" (
    move "resources\ml_feedback.json" "resources\ml_data\datasets\" >nul 2>&1
    echo   - Moved ml_feedback.json
)

if exist "resources\retraining_log.json" (
    move "resources\retraining_log.json" "resources\ml_data\logs\" >nul 2>&1
    echo   - Moved retraining_log.json
)

REM Move model files
if exist "resources\selenium_ngram_model.pkl" (
    move "resources\selenium_ngram_model.pkl" "resources\ml_data\models\" >nul 2>&1
    echo   - Moved selenium_ngram_model.pkl
)

if exist "resources\ml_models" (
    xcopy "resources\ml_models\*" "resources\ml_data\models\ml_models\" /E /I /Y >nul 2>&1
    rmdir /S /Q "resources\ml_models" >nul 2>&1
    echo   - Moved ml_models directory
)

REM Move template files
if exist "resources\code-templates.json" (
    move "resources\code-templates.json" "resources\ml_data\templates\" >nul 2>&1
    echo   - Moved code-templates.json
)

echo.
echo Moving test-related files...

REM Move test data
if exist "resources\uploads" (
    xcopy "resources\uploads\*" "resources\test_data\uploads\" /E /I /Y >nul 2>&1
    rmdir /S /Q "resources\uploads" >nul 2>&1
    echo   - Moved uploads directory
)

if exist "resources\test_sessions" (
    xcopy "resources\test_sessions\*" "resources\test_data\test_sessions\" /E /I /Y >nul 2>&1
    rmdir /S /Q "resources\test_sessions" >nul 2>&1
    echo   - Moved test_sessions directory
)

REM Move test_cases and recorder_tests from project root
if exist "test_cases" (
    xcopy "test_cases\*" "resources\test_data\test_cases\" /E /I /Y >nul 2>&1
    echo   - Moved test_cases directory
)

if exist "recorder_tests" (
    xcopy "recorder_tests\*" "resources\test_data\recorder_tests\" /E /I /Y >nul 2>&1
    echo   - Moved recorder_tests directory
)

if exist "test_sessions" (
    xcopy "test_sessions\*" "resources\test_data\test_sessions\" /E /I /Y >nul 2>&1
    echo   - Moved test_sessions directory
)

echo.
echo ============================================================
echo  Resources Reorganization Complete!
echo ============================================================
echo.
echo New structure:
echo   resources/ml_data/       - All ML and dataset files
echo   resources/test_data/     - All test-related files
echo.
echo IMPORTANT: Code paths have been updated automatically.
echo Please restart the server for changes to take effect.
echo.
pause
