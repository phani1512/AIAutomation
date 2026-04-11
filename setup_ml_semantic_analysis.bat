@echo off
REM ==================================================================
REM  ML Semantic Analysis - Quick Setup Script
REM ==================================================================
REM
REM  This script extracts training data and trains ML models
REM  Run this once to enable ML-powered semantic analysis
REM
REM ==================================================================

echo.
echo ============================================================
echo  ML Semantic Analysis - Quick Setup
echo ============================================================
echo.

cd /d "%~dp0\src\main\python\ml_models"

echo [1/2] Extracting training data from all sources...
echo.
python training_data_extractor.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Training data extraction failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo.
echo [2/2] Training ML models (this may take 2-5 minutes)...
echo.
python semantic_model_trainer.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Model training failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  SETUP COMPLETE!
echo ============================================================
echo.
echo  ML models have been trained and saved.
echo.
echo  Next steps:
echo    1. Restart the API server
echo    2. Look for: "[INIT] ML Semantic Analyzer loaded successfully"
echo    3. Use Semantic Analysis page to test
echo.
echo  For more information, see: ML_SEMANTIC_ANALYSIS_README.md
echo.
pause
