@echo off
echo =========================================
echo   Exam Coach AI - Starting Up
echo =========================================
echo.

echo [1/2] Starting FastAPI backend on port 8000...
start "Exam Coach - Backend" cmd /k "uvicorn main_enhanced:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Streamlit frontend on port 8501...
start "Exam Coach - Frontend" cmd /k "streamlit run app_enhanced.py"

timeout /t 4 /nobreak >nul

echo.
echo =========================================
echo   App is running!
echo   Frontend: http://localhost:8501
echo   API Docs: http://127.0.0.1:8000/docs
echo =========================================
echo.
pause
