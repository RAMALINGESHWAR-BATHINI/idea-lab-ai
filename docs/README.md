# IdeaLab AI Documentation

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Backend API](#backend-api)
- [Website Frontend](#website-frontend)
- [Voice Assistant](#voice-assistant)
- [Database Schema](#database-schema)
- [Security](#security)
- [Deployment](#deployment)
- [Development Guide](#development-guide)

## Overview

IdeaLab AI is a voice-first AI assistant for a college **IdeaLab** — helping students ask questions, research ideas, learn skills, and develop projects through the structured process:

> Problem/Idea → Understand → Define → Ideate → Discuss → Prototype → Test → Get Feedback → Improve → Build

The assistant supports students' thinking; it does not replace it. It asks *what problem are you solving, who for, what already exists* before jumping to "here's how to build it".

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, FastAPI, SQLAlchemy 2.x, asyncpg |
| Database | PostgreSQL 16 + pgvector |
| AI/LLM | Google Gemini (cloud), Ollama (local fallback) |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Voice | Web Speech API (browser-native) |
| Auth | JWT (HS256), bcrypt password hashing |
| Testing | pytest (56 passing tests) |
| Deployment | Docker Compose (optional) |

## Repository Layout

```
idea-lab-ai/
├── backend/          # FastAPI application
├── frontend/         # Public website + dashboards (port 5173)
├── voice/            # Voice assistant app (port 5174)
├── scripts/          # Utility scripts
├── docs/             # This documentation
└── docker-compose.yml # Optional containerized setup
```