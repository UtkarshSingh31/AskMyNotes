from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import shutil
import re
import traceback
from pathlib import Path
from services.rag_service import RAGService
from schemas import ChatRequest, ChatResponse
from llm import chain

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

rag_service = RAGService(data_path=DATA_DIR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="RAG API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def clean_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"([a-zA-Z])([ϵ≤≥])", r"\1 \2", text)
    text = re.sub(r"([ϵ≤≥])([a-zA-Z])", r"\1 \2", text)
    text = re.sub(r"-\s+", "", text)
    return text.strip()


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest): 
    try:
        results = rag_service.query(request.question)
        
        answer = chain.invoke({'topic': results})
        
        sources = [
            {
                "source": doc.metadata.get("source"),
                "page": doc.metadata.get("page")
            }
            for doc in results
        ]
        
        return ChatResponse(
            answer=answer,
            sources=sources
        )
    except Exception as e:
        print("CHAT ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(e)}"
        )


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):  
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )
        
        file_path = DATA_DIR / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        print(f"✓ File saved: {file_path}")

        print("Rebuilding index...")
        rag_service.rebuild()
        print("✓ Index rebuilt successfully")
        
        return {
            "status": "success",
            "message": "PDF uploaded and indexed",
            "filename": file.filename
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print("UPLOAD ERROR:", e)
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Upload error: {str(e)}"
        )

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "RAG API is running"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "rag_service": "ready" if rag_service else "not initialized"
    }