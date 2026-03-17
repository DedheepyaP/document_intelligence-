from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from langchain_groq import ChatGroq

from app.core import settings

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=settings.LLM_KEY, temperature=0.1)


MODE_PROMPTS: dict[str, str] = {
    # "legal":     "You are a legal assistant. Extract clauses and summarize terms strictly.",
    # "academic":   "You are a researcher. Summarize papers and generate citations accurately if asked.",
    # "healthcare": "You are a medical assistant. Extract patient history and suggest treatments if any.",
    # "business":  "You are a business consultant. Transcribe meetings and extract action items.",
    # "finance":   "You are a financial analyst. Answer queries related to bank policies and credits.",
    # "general":   "You are a strict assistant. Use ONLY the information provided.",

    "legal":     "You are a strict legal assistant. Extract clauses and summarize terms using ONLY the provided context.",
    "academic":   "You are a strict researcher. Summarize papers using ONLY the provided context. Do NOT generate citations unless they are in the context.",
    "healthcare": "You are a strict medical assistant. Extract patient history using ONLY the provided context. Do NOT suggest treatments unless explicitly mentioned in the context.",
    "business":  "You are a strict business consultant. Transcribe meetings and extract action items using ONLY the provided context.",
    "finance":   "You are a strict financial analyst. Answer queries related to bank policies and credits using ONLY the provided context.",
    "general":   "You are a strict assistant. Answer using ONLY the provided context. Do NOT hallucinate or bring in outside knowledge.",
}

ROLE_TO_MODE: dict[str, str] = {
    "doctor": "healthcare",
    "lawyer": "legal",
    "researcher": "academic",
    "admin":  "general",
    "consultant": "business",
    "financial_analyst": "finance",
    "general":  "general",
}


def get_mode_from_role(role: str) -> str:
    return ROLE_TO_MODE.get(role.lower(), "general")


def build_super_query_chain(mode: str):
    system_hint = MODE_PROMPTS.get(mode, MODE_PROMPTS["general"])
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a retrieval assistant. Given the chat history and the user's "
            "latest message, rewrite the question as a fully self-contained standalone question.\n"
            f"Domain context: {system_hint} "
            "Preserve ALL identifiers, numbers, codes, dates, and proper nouns "
            "verbatim from the original question.\n\n"
            "Respond ONLY with the rephrased standalone question, with no extra text or explanations.",
        ),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])
    return prompt | llm | StrOutputParser()


def parse_super_query(raw: str) -> str:
    return raw.strip()


def get_dynamic_prompt(mode: str) -> ChatPromptTemplate:
    instruction = MODE_PROMPTS.get(mode, MODE_PROMPTS["general"])
    return ChatPromptTemplate.from_messages([
        (
            "system",
            f"{instruction}\n\n"
            "Rules:\n"
            "1. Answer ONLY using the [CONTEXT] below. Do NOT use your internal knowledge.\n"
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


def format_docs(docs: list[Document]) -> str:
    if not docs:
        return ""
    return "\n\n".join(
        doc.page_content.strip()
        for doc in docs
        if doc.page_content
    )
