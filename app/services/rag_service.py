from typing import Any

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session

from app.utility import get_vectorstore
from app.utility.rag import (
    llm,
    build_super_query_chain,
    parse_super_query,
    get_mode_from_role,
    get_dynamic_prompt,
    format_docs,
    MODE_PROMPTS,
)
from app.utility.hybrid_retriever import build_hybrid_retriever
from app.services.conversation_service import PostgresChatHistory

import logging
logger = logging.getLogger(__name__)


def _build_chain(
    mode: str,
    filename_filter: str | None,
    user_id: int | None,
):
    vectorstore = get_vectorstore()
    super_query_chain = build_super_query_chain(mode)

    retriever = build_hybrid_retriever(
        vectorstore=vectorstore,
        user_id=user_id,
        filename_filter=filename_filter,
        mode=mode,
        k=8,
    )

    def get_context(x: dict) -> str:
        raw = super_query_chain.invoke({
            "input": x["input"],
            "chat_history": x.get("chat_history", []),
        })
        return format_docs(retriever.invoke(parse_super_query(raw)))

    answer_prompt = get_dynamic_prompt(mode)

    return (
        RunnablePassthrough.assign(context=RunnableLambda(get_context))
        | RunnablePassthrough.assign(answer=answer_prompt | llm | StrOutputParser())
    )


def query_rag(
    question: str,
    role: str,
    filename_filter: str | None = None,
    user_id: int | None = None,
    db: Session | None = None,
    callbacks: list[Any] | None = None,
) -> dict[str, Any]:

    mode = get_mode_from_role(role)

    chain_with_history = RunnableWithMessageHistory(
        _build_chain(mode, filename_filter, user_id),
        lambda session_id: PostgresChatHistory(user_id=user_id, db=db, filename=filename_filter),
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    session_id = f"{user_id}:{filename_filter}" if filename_filter else str(user_id)
    config = {"configurable": {"session_id": session_id}}
    if callbacks:
        config["callbacks"] = callbacks

    result = chain_with_history.invoke(
        {"input": question},
        config=config,
    )

    return {"answer": result["answer"]}
