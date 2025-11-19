# RAG Chatbot

A production-ready Retrieval Augmented Generation (RAG) chatbot with a modern React frontend and FastAPI backend, powered by Groq AI.

![RAG Chatbot](https://img.shields.io/badge/RAG-Chatbot-orange) ![Python](https://img.shields.io/badge/Python-3.13-blue) ![React](https://img.shields.io/badge/React-18.2-61DAFB) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)

## Features

- 🤖 **AI-Powered Chat**: Intelligent responses using Groq's Llama 3.3 model
- 📄 **Document Processing**: Upload and query PDF, DOCX, and TXT files
- 🔍 **Hybrid Search**: Combines vector similarity and keyword matching for accurate retrieval
- 🎨 **Modern UI**: Beautiful 3D shader background with glassmorphism design
- ⚡ **Fast Performance**: Optimized embeddings and efficient vector search
- 🎓 **University Branding**: Celebal Technologies and MBM University logos

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Groq API** - LLM inference (Llama 3.3-70B)
- **Custom RAG** - In-memory vector store with hybrid search
- **PyPDF2 & python-docx** - Document processing
- **NumPy** - Vector operations

### Frontend
- **React + TypeScript** - Component-based UI
- **Vite** - Fast build tool
- **Three.js** - 3D shader animations
- **Framer Motion** - Smooth animations
- **Axios** - API communication

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- npm
- Groq API Key ([Get one here](https://console.groq.com/))

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd RAG-chatbot

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Environment Setup

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access at: **http://localhost:5173**

## Usage

1. **Upload Documents** - Click "Upload Docs" to upload PDF, DOCX, or TXT files
2. **Ask Questions** - Type your question about the uploaded documents
3. **Get AI Answers** - Receive contextual responses based on your documents

## Project Structure

```
RAG-chatbot/
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── rag.py               # RAG implementation
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   └── ShaderBackground.tsx
│   │   └── main.tsx
│   ├── public/              # Logos & favicon
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/upload` | Upload documents |
| POST | `/chat` | Send chat message |
| GET | `/documents` | List uploaded documents |
| DELETE | `/clear` | Clear all documents |

## RAG Implementation

- **Text Chunking**: Paragraph-based chunking with 200-char overlap
- **Embeddings**: Word-hash based embeddings (384 dimensions)
- **Hybrid Search**: 70% vector similarity + 30% keyword matching
- **Context Injection**: Top 5 relevant chunks injected into LLM prompts

## Docker Deployment

```bash
docker-compose up --build
```

Services:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Railway Deployment

### Setup

1. **Push to GitHub** (ensure `.env` is in `.gitignore`)
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Create Railway Project**
   - Go to [Railway.app](https://railway.app/)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

3. **Configure Backend Service**
   - Add service → Select backend folder
   - Add environment variable:
     ```
     GROQ_API_KEY=gsk_your_actual_groq_api_key_here
     ```
   - Railway will auto-detect Python and run uvicorn

4. **Configure Frontend Service**
   - Add service → Select frontend folder
   - Update `vite.config.ts` proxy to point to Railway backend URL
   - Railway will auto-detect Node.js and run the build

5. **Deploy**
   - Railway will automatically deploy both services
   - Get your public URLs from Railway dashboard

### Environment Variables for Railway

Backend:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
PORT=8000
HOST=0.0.0.0
```

Frontend will automatically connect via the proxy configuration.

## Development

```bash
# Backend with hot reload
cd backend
python -m uvicorn main:app --reload

# Frontend dev server
cd frontend
npm run dev
```

## Contributing

**Created by:** Aaryan Choudhary  
**University:** MBM University, Jodhpur (CSE, 23UCSE4002)  
**Company:** Celebal Technologies - Summer Internship 2025

## License

MIT License

## Acknowledgments

- Celebal Technologies for internship opportunity
- MBM University for academic support
- Groq for providing fast LLM inference
