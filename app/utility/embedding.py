from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.core import settings

COLLECTION_NAME = settings.COLLECTION_NAME
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
PERSIST_DIR = settings.CHROMA_PERSIST_DIR

_embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

_vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=_embedding_function,
    persist_directory=PERSIST_DIR,
)

def get_vectorstore() -> Chroma:
    return _vectorstore