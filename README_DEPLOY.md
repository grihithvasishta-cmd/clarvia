# Clairvia AI - Deployment (Option A)

This repository contains the Clairvia AI backend and a minimal Next.js frontend example. The recommended deployment architecture is:

- Backend: Dockerized FastAPI app (runs heavy ML tasks). Deploy to Cloud Run, Render, Fly, AWS ECS, etc.
- Frontend: Next.js app deployed to Vercel which proxies requests to the backend.

Quickstart (local with Docker Compose)
1. Ensure you have Docker and Docker Compose installed.
2. Place your project's requirements.txt at repo root.
3. Build and run:
   ```bash
   docker compose up --build
