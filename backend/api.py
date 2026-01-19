from fastapi import FastAPI,UploadFile,File,HTTPException
from contextlib import asynccontextmanager
import shutil
import re
from pathlib import Path
from backend.services.rag_service import RAGService
from backend.schemas import ChatRequest, ChatResponse
from backend.llm import chain

rag_service: RAGService | None = None

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag_service
    rag_service = RAGService(data_path="data")
    yield
    rag_service = None


app = FastAPI(
    title="RAG API",
    lifespan=lifespan
)


def clean_text(text: str) -> str:
    # Fix broken line breaks
    text = text.replace("\n", " ")

    # Fix multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Fix missing space before Greek symbols
    text = re.sub(r"([a-zA-Z])([ϵ≤≥])", r"\1 \2", text)

    # Fix missing space after symbols
    text = re.sub(r"([ϵ≤≥])([a-zA-Z])", r"\1 \2", text)

    # Fix hyphenated line breaks (e.g., explo- ration)
    text = re.sub(r"-\s+", "", text)

    return text.strip()


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    results = rag_service.query(request.question)

    answer = chain.invoke({'topic':results})

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

@app.post("/upload")
def upload_pdf(file: UploadFile = File(...)):
    try:
        file_path = DATA_DIR / file.filename

        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # rebuild index
        rag_service.rebuild()

        return {"status": "uploaded and indexed"}

    except Exception as e:
        print("UPLOAD ERROR:", e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )