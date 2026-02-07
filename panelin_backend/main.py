"""FastAPI application for Panelin Conversation Logging"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os

from panelin_backend.database import db

app = FastAPI(title="Panelin Conversation Logging API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class ConversationCreate(BaseModel):
    thread_id: str
    assistant_id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_type: Optional[str] = "customer"


class MessageCreate(BaseModel):
    thread_id: str
    message_id: str
    role: str
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    id: str
    thread_id: str
    user_name: Optional[str]
    user_type: str
    status: str
    created_at: datetime
    message_count: Optional[int] = 0


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


@app.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(conversation: ConversationCreate):
    """Create a new conversation thread"""
    try:
        result = db.create_conversation(
            thread_id=conversation.thread_id,
            assistant_id=conversation.assistant_id,
            user_id=conversation.user_id,
            user_name=conversation.user_name,
            user_type=conversation.user_type or "customer"
        )
        return ConversationResponse(
            id=str(result["id"]),
            thread_id=result["thread_id"],
            user_name=result["user_name"],
            user_type=result["user_type"],
            status=result["status"],
            created_at=result["created_at"],
            message_count=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create conversation: {str(e)}")


@app.post("/api/conversations/{conversation_id}/messages")
async def add_message(conversation_id: str, message: MessageCreate):
    """Add a message to a conversation"""
    try:
        # Verify conversation exists
        conversation = db.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        result = db.add_message(
            conversation_id=conversation_id,
            message_id=message.message_id,
            thread_id=message.thread_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at
        )
        return MessageResponse(
            id=str(result["id"]),
            role=result["role"],
            content=result["content"],
            created_at=result["created_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


@app.get("/api/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    user_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List all conversations with filters"""
    try:
        results = db.get_conversations(
            user_type=user_type,
            status=status,
            limit=limit,
            offset=offset
        )
        return [
            ConversationResponse(
                id=str(row["id"]),
                thread_id=row["thread_id"],
                user_name=row["user_name"],
                user_type=row["user_type"],
                status=row["status"],
                created_at=row["created_at"],
                message_count=row.get("message_count", 0)
            )
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list conversations: {str(e)}")


@app.get("/api/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(conversation_id: str):
    """Get all messages for a conversation"""
    try:
        # Verify conversation exists
        conversation = db.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        results = db.get_conversation_messages(conversation_id)
        return [
            MessageResponse(
                id=str(row["id"]),
                role=row["role"],
                content=row["content"],
                created_at=row["created_at"]
            )
            for row in results
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@app.get("/api/conversations/{conversation_id}/export")
async def export_conversation(conversation_id: str, format: str = "json"):
    """Export conversation to JSON/CSV/PDF"""
    try:
        # Verify conversation exists
        conversation = db.get_conversation_by_id(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        messages = db.get_conversation_messages(conversation_id)
        
        if format == "json":
            return {
                "conversation": {
                    "id": str(conversation["id"]),
                    "thread_id": conversation["thread_id"],
                    "user_name": conversation["user_name"],
                    "created_at": conversation["created_at"].isoformat(),
                },
                "messages": [
                    {
                        "role": msg["role"],
                        "content": msg["content"],
                        "created_at": msg["created_at"].isoformat()
                    }
                    for msg in messages
                ]
            }
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export conversation: {str(e)}")


@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary (total conversations, avg response time, etc.)"""
    try:
        conversations = db.get_conversations(limit=1000000)
        total_conversations = len(conversations)
        total_messages = sum(conv.get("message_count", 0) for conv in conversations)
        
        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": total_messages / total_conversations if total_conversations > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}
