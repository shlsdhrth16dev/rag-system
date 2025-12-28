# AI Knowledge Base - Supercharged RAG System

![Project Banner](https://img.shields.io/badge/Status-Active-brightgreen)
![Tech Stack](https://img.shields.io/badge/Stack-Python%20|%20React%20|%20Docker-blue)
![License](https://img.shields.io/badge/License-MIT-orange)

## 🚀 Overview

The **AI Knowledge Base** is an advanced Retrieval-Augmented Generation (RAG) system designed to deliver precise, context-aware answers from large document repositories. It combines a robust **FastAPI** backend for vector similarity search with a high-performance, immersive **React** frontend featuring real-time 3D visualizations.

This system demonstrates the integration of modern AI workflows with cutting-edge web graphics to create a futuristic user experience.

---

## ✨ Key Features

- **🧠 Intelligent Retrieval**: Leverages `PGVector` and advanced embeddings (OpenAI/Gemini) to semantically search and retrieve relevant document chunks.
- **💬 Generative AI Responses**: Synthesizes retrieved context using State-of-the-Art LLMs to provide accurate, natural language answers.
- **👁️ Immersive 3D UI**: Features `GridScan`, a custom Three.js component with post-processing effects (Bloom, Chromatic Aberration) and real-time face tracking via `face-api.js`.
- **⚡ High Performance**: Built on `FastAPI` (Python) and `Vite` (React) for near-instant latency and hot module replacement.
- **🐳 Containerized Architecture**: Fully Dockerized environment ensuring consistent deployment and scalability.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18, TypeScript, Vite
- **Graphics**: Three.js, React-Three-Fiber, Postprocessing
- **AI/CV**: Face-api.js (Real-time face tracking)
- **Styling**: CSS Modules, Flexbox Layouts

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL with `pgvector` extension
- **AI Orchestration**: LangChain
- **LLM Integrations**: Google Generative AI (Gemini), OpenAI via OpenRouter
- **ORM**: SQLAlchemy (Async)

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Server**: Uvicorn (ASGI)

---

## 🏗️ Architecture

The system follows a microservices-inspired architecture managed via Docker Compose:

1.  **Frontend Service**: Serves the React SPA on port `5173`.
2.  **Backend Service**: Exposes REST API endpoints on port `8000` for RAG operations, stats, and health checks.
3.  **Database Service**: PostgreSQL container enabled with `pgvector` for high-speed vector storage and retrieval.

---

## 🚀 Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- [Git](https://git-scm.com/) installed.

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/rag-system.git
    cd rag-system
    ```

2.  **Configure Environment**
    Create a `.env` file in the `backend` directory (or root, depending on your setup) with your API keys:
    ```env
    OPENAI_API_KEY=your_key_here
    GEMINI_API_KEY=your_key_here
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=your_password
    POSTGRES_DB=postgres
    ```

3.  **Run with Docker**
    Start the entire stack with a single command:
    ```bash
    docker-compose up --build
    ```

4.  **Access the Application**
    - **Frontend**: [http://localhost:5173](http://localhost:5173)
    - **Backend API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📸 visual Preview

The application features a unique **GridScan** background that reacts to user interaction and camera input, providing a "Cyberpunk" aesthetic behind the chat interface.



---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Developed by Sidharth** | *Bringing AI to life with code.*
