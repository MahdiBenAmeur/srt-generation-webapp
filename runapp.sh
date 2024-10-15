#!/bin/bash

# Start FastAPI in the background
cd backend
uvicorn backend:app --reload &
cd ..


# Start Vite
cd frontend
npm run dev