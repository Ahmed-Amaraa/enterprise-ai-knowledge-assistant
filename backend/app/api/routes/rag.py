from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.session import get_db
from app.schemas.rag import QuestionRequest, AnswerResponse, ConversationCreate, ChatRequest
from app.services.rag_service import RagService
from app.models.conversation import Conversation
from app.models.message import Message


router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)

rag_service = RagService()


def _conversation_title(question: str) -> str:
    title = " ".join(question.split())
    max_length = 50
    if len(title) > max_length:
        return f"{title[:max_length].rstrip()}..."
    return title


@router.post(
    "/ask",
    response_model=AnswerResponse,
)
async def ask_question(
    request: QuestionRequest,
    current_user=Depends(get_current_user),
):
    try:
        answer = rag_service.answer_question(
            question=request.question,
        )

        return AnswerResponse(
            answer=answer,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/conversations")
async def get_conversations(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()

    titles_changed = False
    for conversation in conversations:
        if conversation.title and conversation.title.strip().lower() != "new chat":
            continue
        first_question = next(
            (message.content for message in conversation.messages if message.role == "user"),
            None,
        )
        if first_question:
            conversation.title = _conversation_title(first_question)
            titles_changed = True
    if titles_changed:
        db.commit()
    
    return [
        {
            "id": str(c.id),
            "title": c.title,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }
        for c in conversations
    ]


@router.post("/conversations")
async def create_conversation(
    payload: ConversationCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = Conversation(
        user_id=current_user.id,
        title=payload.title
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return {
        "id": str(conversation.id),
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
        "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    db.delete(conversation)
    db.commit()
    return {"message": "Conversation deleted successfully"}


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "feedback": m.feedback,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in messages
    ]


@router.post("/chat")
async def chat_rag(
    payload: ChatRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = db.query(Conversation).filter(
        Conversation.id == payload.conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    try:
        query_vector = rag_service.embed_query(payload.question)
        results = rag_service.search_chunks(query_vector=query_vector, top_k=5)
        context = rag_service.build_context(results, min_score=0.35)
        prompt = rag_service.build_prompt(question=payload.question, context=context)
        sources = list(set(
            result.payload.get("source")
            for result in results
            if result.payload and result.payload.get("source")
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Error: {str(e)}")

    try:
        answer = rag_service.generate_answer(prompt=prompt)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"RAG Error: {str(exc)}") from exc

    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=payload.question,
    )
    db.add(user_msg)

    assistant_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
    )
    db.add(assistant_msg)
    if not conversation.title or conversation.title.strip().lower() == "new chat":
        conversation.title = _conversation_title(payload.question)
    conversation.updated_at = datetime.utcnow()
    db.commit()

    return {
        "answer": answer,
        "content": answer,
        "sources": sources,
        "message_id": str(assistant_msg.id),
        "conversation_id": str(conversation.id),
    }


@router.post("/messages/{message_id}/feedback")
async def set_message_feedback(
    message_id: int,
    payload: dict,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    feedback = payload.get("feedback")
    if feedback not in {"useful", "not_useful"}:
        raise HTTPException(status_code=422, detail="Feedback must be useful or not_useful")

    message = db.query(Message).join(Conversation).filter(
        Message.id == message_id,
        Message.role == "assistant",
        Conversation.user_id == current_user.id,
    ).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.feedback = feedback
    db.commit()
    return {"message_id": str(message.id), "feedback": message.feedback}