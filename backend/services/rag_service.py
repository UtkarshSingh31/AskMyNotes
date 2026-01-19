from backend.core.document_loader import load_documents
from backend.core.text_splitter import split_documents
from backend.core.storage import create_vector_store
from backend.core.retriever import get_retriever

class RAGService:
    def __init__(self, data_path: str):
        self.data_path = data_path 
        self._build()

    def _build(self):
        documents = load_documents(self.data_path)
        chunks = split_documents(documents)
        vector_store = create_vector_store(chunks)
        self.retriever = get_retriever(vector_store)
    
    def query(self, question: str):
        return self.retriever.invoke(question)
    
    def rebuild(self):
        self._build()
