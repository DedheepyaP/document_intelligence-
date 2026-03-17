import logging
from sqlalchemy.orm import Session
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.models.conversation import ConversationMessage
from langchain_groq import ChatGroq
from app.core import settings

logger = logging.getLogger(__name__)

MAX_WINDOW = 10 

summary_llm = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.LLM_KEY, temperature=0.1)


def _compress_message(content: str, role: str) -> str:
    if len(content) < 300:
        return content
    
    prompt = (
        f"Please summarize the following '{role}' message concisely. "
        "Retain key concepts, names, and intent in no more than 2-3 sentences:\n\n"
        f"{content}"
    )
    
    try:
        response = summary_llm.invoke([HumanMessage(content=prompt)])
        return str(response.content)
    except Exception as e:
        logger.error(f"Compression failed: {e}")
        return content[:1000]


class PostgresChatHistory(BaseChatMessageHistory):


    def __init__(self, user_id: int, db: Session, filename: str | None = None, limit: int = 10):
        self.user_id = user_id
        self.filename = filename
        self.db = db
        self.limit = limit

    @property
    def messages(self) -> list[BaseMessage]:
        query = self.db.query(ConversationMessage).filter(ConversationMessage.user_id == self.user_id)
        if self.filename:
            query = query.filter(ConversationMessage.filename == self.filename)
        else:
            query = query.filter(ConversationMessage.filename.is_(None))
            
        rows = (
            query
            .order_by(ConversationMessage.created_at.desc())
            .limit(self.limit)
            .all()
        )
        rows = list(reversed(rows))
        result: list[BaseMessage] = []
        for r in rows:
            if r.role == "human":
                result.append(HumanMessage(content=r.content))
            else:
                result.append(AIMessage(content=r.content))
        return result

    def add_messages(self, messages: list[BaseMessage]) -> None:

        for message in messages:
            role = "human" if isinstance(message, HumanMessage) else "ai"
            compressed_content = _compress_message(str(message.content), role)
            self.db.add(
                ConversationMessage(
                    user_id=self.user_id,
                    filename=self.filename,
                    role=role,
                    content=compressed_content,
                )
            )
        self.db.commit()
        _enforce_window(self.db, self.user_id, self.filename)

    def clear(self) -> None:
        query = self.db.query(ConversationMessage).filter(ConversationMessage.user_id == self.user_id)
        if self.filename:
            query = query.filter(ConversationMessage.filename == self.filename)
        else:
            query = query.filter(ConversationMessage.filename.is_(None))
        query.delete()
        self.db.commit()


def _enforce_window(db: Session, user_id: int, filename: str | None = None) -> None:
    query = db.query(ConversationMessage).filter(ConversationMessage.user_id == user_id)
    if filename:
        query = query.filter(ConversationMessage.filename == filename)
    else:
        query = query.filter(ConversationMessage.filename.is_(None))
        
    total = query.count()
    if total <= MAX_WINDOW:
        return

    excess = total - MAX_WINDOW
    oldest_ids = (
        query.with_entities(ConversationMessage.id)
        .order_by(ConversationMessage.created_at.asc())
        .limit(excess)
        .all()
    )
    ids_to_delete = [row.id for row in oldest_ids]
    db.query(ConversationMessage).filter(
        ConversationMessage.id.in_(ids_to_delete)
    ).delete(synchronize_session=False)
    db.commit()
    logger.info(
        f"Pruned {excess} old messages for user_id={user_id} (window={MAX_WINDOW})"
    )
