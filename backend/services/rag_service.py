from core.document_loader import load_documents
from core.text_splitter import split_documents
from core.storage import create_vector_store
from core.retriever import get_retriever
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

class RAGService:
    def __init__(self, data_path: Path):
        self.data_path = data_path 
        self._build()

    def _build(self):
        documents = load_documents(self.data_path)

        if not documents:
            raise RuntimeError(f"No documents loaded in this {self.data_path}")

        chunks = split_documents(documents)
        vector_store = create_vector_store(chunks)
        self.retriever = get_retriever(vector_store)
    
    def query(self, question: str):

        if not self.retriever:
            raise  RuntimeError("No documents indexed yet.")
        
        return self.retriever.invoke(question)
    
    def rebuild(self):
        self._build()
