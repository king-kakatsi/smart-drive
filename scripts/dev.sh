#!/bin/bash

# Smart-Drive Development Runner
echo "Starting Smart-Drive development servers..."

# Function to cleanup background processes
cleanup() {
    echo "Stopping servers..."
    kill $(jobs -p) 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start backend in background
echo "Starting FastAPI backend..."
cd backend
source venv/bin/activate
python run.py &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend in background
echo "Starting Vue frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Servers started!"
echo "Frontend: http://localhost:5173"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID


