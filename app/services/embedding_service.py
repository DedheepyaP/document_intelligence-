import logging
from typing import List, Dict
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from docling.datamodel.document import DoclingDocument
from docling.chunking import HierarchicalChunker

from app.utility import get_vectorstore
from app.core import settings

logger = logging.getLogger(__name__)

summary_llm = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.LLM_KEY, temperature=0.1)

def _generate_document_summary(full_text: str) -> str:
    # Truncate to a reasonable length for the context window
    text_to_summarize = full_text[:40000]
    prompt = (
        "Please provide a comprehensive but concise overview/summary of the following document. "
        "Capture the main topics, key points, and overall purpose.\n\n"
        f"DOCUMENT TEXT:\n{text_to_summarize}"
    )
    try:
        response = summary_llm.invoke([HumanMessage(content=prompt)])
        return str(response.content)
    except Exception as e:
        logger.error(f"Failed to generate global summary: {e}")
        return "No summary generated."

def index_documents(extracted_docs: List[Dict], filename: str, user_id: int) -> int:

    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", "", ". ", ", "]
    )
    
    docling_chunker = HierarchicalChunker()

    all_chunks: List[Document] = []

    full_document_text = ""

    for item in extracted_docs:
        text = item.get("text", "").strip()
        if not text:
            continue
            
        full_document_text += text + "\n\n"

        metadata = item.get("metadata", {})
        metadata["filename"] = filename 
        metadata["user_id"] = user_id

        if metadata.get("source") == "docling":
            ast_dict = item.get("docling_ast")
            if not ast_dict:
                logger.warning("docling_ast missing for file=%s — skipping chunk, no data to embed", filename)
                continue
                
            docling_doc = DoclingDocument.model_validate(ast_dict)
            
            doc_chunks = docling_chunker.chunk(docling_doc)
            
            for c in doc_chunks:
                chunk_text = c.text
                headings = c.meta.headings if hasattr(c.meta, 'headings') else []
                heading = headings[0] if headings else None
                
                clean_metadata = metadata.copy()
                if heading:
                    chunk_text = f"[{heading}]\n\n{chunk_text}"
                    
                doc = Document(page_content=chunk_text, metadata=clean_metadata)
                all_chunks.append(doc)
        else:
            doc = Document(page_content=text, metadata=metadata)
            chunks = char_splitter.split_documents([doc])
            all_chunks.extend(chunks)

    if full_document_text:
        logger.info("Generating global document summary for file=%s", filename)
        summary_content = _generate_document_summary(full_document_text)
        if summary_content and summary_content != "No summary generated.":
            summary_doc = Document(
                page_content=f"[Document Summary]\n\n{summary_content}",
                metadata={"filename": filename, "user_id": user_id, "is_summary": True}
            )
            all_chunks.append(summary_doc)

    if not all_chunks:
        logger.warning("No valid text found to index for file=%s", filename)
        return 0

    # for i,chunk in enumerate(all_chunks):
    #     logger.debug("chunk %d: %s", i, chunk.page_content[:100])
    
    try:
        vectorstore = get_vectorstore()
        vectorstore.add_documents(all_chunks)
        
        logger.info("Successfully indexed %d chunks for file=%s", len(all_chunks), filename)
        return len(all_chunks)
    except Exception as e:
        logger.error("Failed to add documents to vector store: %s", str(e))
        raise RuntimeError(f"Indexing failed: {str(e)}")