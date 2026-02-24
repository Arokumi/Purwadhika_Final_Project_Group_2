# SiapKerja: Agentic AI-Powered Career Preparation

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-LangGraph-orange.svg)](https://blog.langchain.dev/langgraph/)
[![AI-Voice](https://img.shields.io/badge/Voice-Whisper--1-green.svg)](https://openai.com/research/whisper)
[![UI](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Container-Docker-blue.svg)](https://www.docker.com/)

**SiapKerja** is an end-to-end career preparation platform designed to bridge the gap between Indonesian job seekers and their ideal roles. Developed as the final project for the **Purwadhika AI Engineering** program, this tool leverages an **Agentic AI Architecture** to provide highly personalized analysis, discovery, and high-fidelity interview simulation.

---

## 🚀 Key Features

### 🧠 Agentic CV Analysis & Insights
Utilizing **LangGraph** for multi-stage reasoning, the system performs a deep-dive into your professional profile to understand context rather than just matching keywords.

### 🔍 Natural Language Job Discovery
Interact with the job database using human language. The AI handles semantic search and intelligent filtering to find the most optimal matches based on your CV profile and natural language queries.

### 📋 Personalized AI Career Advisor
A 24/7 dedicated coach that generates custom study roadmaps and actionable checklists based on your specific skill gaps and target roles.

### 🎙️ Real-Time Voice Mock Interviews
A low-latency interview simulation built with **Whisper-1**, **Silero VAD**, and **LiveKit/WebRTC**. Practice with "Sarah," an AI interviewer that provides real-time follow-up questions and constructive performance feedback.

---

## 🏗️ Deployment Architecture

The project is designed to be fully containerized, separating the AI orchestration from the user interface for scalable deployment.

### 1. Backend Agent Service (Docker)
The core engine contains the LangGraph logic, RTC agents, and FastAPI endpoints. This is built into a Docker image to be hosted on services like Cloud Run, AWS EC2, or Railway.

### 2. Frontend Interface (Streamlit)
A lightweight Streamlit app that communicates with the hosted Docker container to handle CV uploads and establish the voice connection.

---

## 🛠️ Setup & Execution

### Step 1: Create the Docker Image
Build the backend service that contains your API logic and AI agents.
  ```bash
  # Build the image from your Dockerfile
  docker build -t siapkerja-backend:latest.
  ```

### Step 2: Hosting & Environment Variables
Run the container on your preferred host. Ensure you pass your API keys during the run or set them in your provider's environment settings.

  ```bash
  docker run -d \
    -p 8080:8080 \
    --env-file .env \
    --name siapkerja-instance \
    siapkerja-backend:latest
  ```

### Required Environment Variables:
| Variable | Description |
| :--- | :--- |
| OPENAI_API_KEY | Primary key for GPT-4o and Whisper-1 |
| LIVEKIT_API_KEY | Key for real-time voice sessions |
| LIVEKIT_API_SECRET | Secret for real-time voice sessions |
| LIVEKIT_URL | Your LiveKit instance URL |
| QDRANT_ENDPOINT | Endpoint/URL for Qdrant database|
| QDRANT_API_KEY | API key for QDrant |


### Step 3: Connect the Streamlit Frontend

Once the backend is hosted, configure your Streamlit app to point to the backend's public URL/IP to send CV data and receive interview tokens.
