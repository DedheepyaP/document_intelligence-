from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_groq import ChatGroq

from app.core import settings

# ---------------------------------------------------------------------------
# LLM (shared across RAG utilities)
# ---------------------------------------------------------------------------

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=settings.LLM_KEY, temperature=0.1)

# ---------------------------------------------------------------------------
# Mode / Role mappings
# ---------------------------------------------------------------------------

MODE_PROMPTS: dict[str, str] = {
    "legal":      "You are a legal assistant. Extract clauses and summarize terms strictly.",
    "academic":   "You are a researcher. Summarize papers and generate citations accurately if asked.",
    "healthcare": "You are a medical assistant. Extract patient history and suggest treatments if any.",
    "business":   "You are a business consultant. Transcribe meetings and extract action items.",
    "finance":    "You are a financial analyst. Answer queries related to bank policies and credits.",
    "general":    "You are a strict assistant. Use ONLY the information provided.",
}

ROLE_TO_MODE: dict[str, str] = {
    "doctor":           "healthcare",
    "lawyer":           "legal",
    "researcher":       "academic",
    "admin":            "general",
    "consultant":       "business",
    "financial_analyst": "finance",
    "general":          "general",
}


def get_mode_from_role(role: str) -> str:
    """Map a user role string to its corresponding RAG mode."""
    return ROLE_TO_MODE.get(role.lower(), "general")


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

contextualize_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "Given a chat history and the latest user question which might reference "
        "context in the chat history, formulate a standalone question which can be "
        "understood without the chat history. Handle pronoun references "
        "('it', 'that', 'them') and incomplete questions. "
        "Do NOT answer the question. Only reformulate it if needed, otherwise return it as is.",
    ),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

rephrase_chain = contextualize_prompt | llm | StrOutputParser()


def get_dynamic_prompt(mode: str) -> ChatPromptTemplate:
    """Return a mode-specific answer prompt."""
    instruction = MODE_PROMPTS.get(mode, MODE_PROMPTS["general"])
    return ChatPromptTemplate.from_messages([
        (
            "system",
            f"{instruction}\n\n"
            "Rules:\n"
            "1. Answer ONLY using the [CONTEXT] below.\n"
            "2. If the answer is not in the context, say: "
            "'No relevant information found in the provided documents.'\n"
            "3. Keep answers under 5 sentences. No filler like 'Based on the text...'\n"
            "4. Use chat history ONLY if it is directly relevant to the current question.\n"
            "5. If the question introduces a new topic, ignore previous conversation.\n"
            "CONTEXT:\n{context}",
        ),
        ("system", "Previous conversation:"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])


# ---------------------------------------------------------------------------
# Document formatter
# ---------------------------------------------------------------------------

def format_docs(docs: list[Document]) -> str:
    """Concatenate page content from retrieved documents."""
    if not docs:
        return ""
    return "\n\n".join(
        doc.page_content.strip()
        for doc in docs
        if doc.page_content
    )
