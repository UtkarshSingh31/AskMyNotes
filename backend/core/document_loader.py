from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

def load_documents(path="data"):
    loader = DirectoryLoader(
        path=path,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    return loader.load()

