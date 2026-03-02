from typing import Any

from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.orm import Session

from app.utility import get_vectorstore
from app.utility.rag import llm, rephrase_chain, get_mode_from_role, get_dynamic_prompt, format_docs
from app.services.conversation_service import PostgresChatHistory


def _build_chain(mode: str, filename_filter: str | None, user_id: int | None):
    filters = None
    if user_id and filename_filter:
        filters = {"$and": [{"user_id": user_id}, {"filename": filename_filter}]}
    elif user_id:
        filters = {"user_id": user_id}
    elif filename_filter:
        filters = {"filename": filename_filter}

    vectorstore = get_vectorstore()
    search_kwargs: dict = {"k": 10}
    if filters:
        search_kwargs["filter"] = filters
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)

    def retrieve_with_history(x: dict) -> str:
        rephrased = rephrase_chain.invoke(x) if x.get("chat_history") else x["input"]
        return format_docs(retriever.invoke(rephrased))

    answer_prompt = get_dynamic_prompt(mode)

    return (
        RunnablePassthrough.assign(context=RunnableLambda(retrieve_with_history))
        | RunnablePassthrough.assign(answer=answer_prompt | llm | StrOutputParser())
    )


def query_rag(
    question: str,
    role: str,
    filename_filter: str | None = None,
    user_id: int | None = None,
    db: Session | None = None,
) -> dict[str, Any]:

    mode = get_mode_from_role(role)

    chain_with_history = RunnableWithMessageHistory(
        _build_chain(mode, filename_filter, user_id),
        lambda session_id: PostgresChatHistory(int(session_id), db),
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    result = chain_with_history.invoke(
        {"input": question},
        config={"configurable": {"session_id": str(user_id)}},
    )

    return {"answer": result["answer"]}
