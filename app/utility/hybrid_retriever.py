import logging
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_classic.retrievers import ContextualCompressionRetriever

# Initialize the cross-encoder model once
try:
    reranker_model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
    compressor = CrossEncoderReranker(model=reranker_model, top_n=4)
except Exception as e:
    logger.error(f"Failed to load reranker model: {e}")
    compressor = None

logger = logging.getLogger(__name__)

MODE_RETRIEVER_WEIGHTS: dict[str, list[float]] = {
#     "legal":      [0.6, 0.4],   
#     "finance":    [0.6, 0.4],   
#     "healthcare": [0.5, 0.5],  
#     "academic":   [0.3, 0.7],  
#     "business":   [0.4, 0.6],
#     "general":    [0.4, 0.6],
}


def build_hybrid_retriever(
    vectorstore: Chroma,
    user_id: int | None = None,
    filename_filter: str | None = None,
    mode: str = "general",
    k: int = 8,
):


    filters = None
    if user_id and filename_filter:
        filters = {"$and": [{"user_id": user_id}, {"filename": filename_filter}]}
    elif user_id:
        filters = {"user_id": user_id}
    elif filename_filter:
        filters = {"filename": filename_filter}

    search_kwargs: dict = {"k": k}
    if filters:
        search_kwargs["filter"] = filters

    semantic_retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)

    try:
        chroma_collection = vectorstore._collection
        raw = chroma_collection.get(
            where=filters if filters else None,
            include=["documents", "metadatas"],
            limit=5000,
        )

        corpus_docs: list[Document] = [
            Document(page_content=text, metadata=meta)
            for text, meta in zip(raw["documents"], raw["metadatas"])
            if text and text.strip()
        ]
    except Exception as e:
        logger.warning("BM25 corpus fetch failed, falling back to semantic-only: %s", e)
        return semantic_retriever

    if not corpus_docs:
        logger.info("No documents in corpus for user_id=%s, using semantic-only retriever", user_id)
        return semantic_retriever

    bm25_retriever = BM25Retriever.from_documents(corpus_docs)
    bm25_retriever.k = k

    weights = MODE_RETRIEVER_WEIGHTS.get(mode, [0.3, 0.7])
    ensemble = EnsembleRetriever(
        retrievers=[bm25_retriever, semantic_retriever],
        weights=weights,
    )

    if compressor is not None:
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=ensemble
        )
        logger.debug(
            "Hybrid retriever built with compression: corpus_size=%d, mode=%s, weights=%s",
            len(corpus_docs), mode, weights,
        )
        return compression_retriever

    logger.debug(
        "Hybrid retriever built: corpus_size=%d, mode=%s, weights=%s",
        len(corpus_docs), mode, weights,
    )
    return ensemble
