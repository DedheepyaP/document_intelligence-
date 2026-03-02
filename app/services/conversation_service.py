import logging
from sqlalchemy.orm import Session
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.models.conversation import ConversationMessage

logger = logging.getLogger(__name__)

MAX_WINDOW = 20 


class PostgresChatHistory(BaseChatMessageHistory):


    def __init__(self, user_id: int, db: Session, limit: int = 10):
        self.user_id = user_id
        self.db = db
        self.limit = limit

    @property
    def messages(self) -> list[BaseMessage]:
        rows = (
            self.db.query(ConversationMessage)
            .filter(ConversationMessage.user_id == self.user_id)
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
            self.db.add(
                ConversationMessage(
                    user_id=self.user_id,
                    role=role,
                    content=message.content,
                )
            )
        self.db.commit()
        _enforce_window(self.db, self.user_id)

    def clear(self) -> None:
        self.db.query(ConversationMessage).filter(
            ConversationMessage.user_id == self.user_id
        ).delete()
        self.db.commit()


def _enforce_window(db: Session, user_id: int) -> None:
    total = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.user_id == user_id)
        .count()
    )
    if total <= MAX_WINDOW:
        return

    excess = total - MAX_WINDOW
    oldest_ids = (
        db.query(ConversationMessage.id)
        .filter(ConversationMessage.user_id == user_id)
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
