#!/bin/bash

echo "========================================="
echo "  Exam Coach AI - Starting Up"
echo "========================================="
echo ""

# Start FastAPI backend in background
echo "[1/2] Starting FastAPI backend on port 8000..."
uvicorn main_enhanced:app --reload --port 8000 &
BACKEND_PID=$!
echo "      Backend PID: $BACKEND_PID"

# Wait for backend to be ready
sleep 3

# Start Streamlit frontend in background
echo "[2/2] Starting Streamlit frontend on port 8501..."
streamlit run app_enhanced.py &
FRONTEND_PID=$!
echo "      Frontend PID: $FRONTEND_PID"

sleep 2

echo ""
echo "========================================="
echo "  App is running!"
echo "  Frontend : http://localhost:8501"
echo "  API Docs : http://127.0.0.1:8000/docs"
echo "========================================="
echo ""
echo "Press Ctrl+C to stop both servers."

# Keep script alive and handle Ctrl+C
trap "echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
wait
