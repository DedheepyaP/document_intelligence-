import chromadb
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.core import settings

COLLECTION_NAME = settings.COLLECTION_NAME
EMBEDDING_MODEL = settings.EMBEDDING_MODEL

_embedding_function = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

_chroma_client = chromadb.HttpClient(
    host=settings.CHROMA_HOST,
    port=settings.CHROMA_PORT,
)

_vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=_embedding_function,
    client=_chroma_client,
)


def get_vectorstore() -> Chroma:
    return _vectorstore