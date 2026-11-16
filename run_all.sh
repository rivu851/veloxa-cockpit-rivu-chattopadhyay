#!/usr/bin/env bash
# Veloxa CXO Cockpit — Single-Command Local Launch Script (Unix / macOS / WSL)
# Candidate: Rivu Chattopadhyay
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "=== Veloxa CXO Cockpit: Local Launch ==="

# 1. Backend setup
cd "$REPO_ROOT"
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r backend/requirements.txt --quiet

# 2. Automated test run
echo "Running automated test suite..."
python -m pytest backend/tests -v

# 3. Frontend setup
cd "$REPO_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "All verification checks passed!"
echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:3000"

# Start backend in background and frontend in foreground
cd "$REPO_ROOT"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd "$REPO_ROOT/frontend"
npm run dev

kill $BACKEND_PID
