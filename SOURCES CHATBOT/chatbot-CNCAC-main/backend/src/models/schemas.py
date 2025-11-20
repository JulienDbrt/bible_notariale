from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    PENDING = "pending"
    EMBEDDING = "embedding"
    COMPLETE = "complete"
    FAILED = "failed"

class IndexingStatus(str, Enum):
    PENDING = "pending"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"

class EmbeddingJobStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# User schemas
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str
    created_date: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_admin: bool = False

# Document schemas
class DocumentBase(BaseModel):
    filename: str
    file_size: int

class DocumentCreate(DocumentBase):
    user_id: str
    file_path: str
    file_extension: str
    minio_path: str
    indexing_status: IndexingStatus = IndexingStatus.PENDING

class DocumentResponse(DocumentBase):
    id: str
    user_id: Optional[str] = None
    file_extension: str
    file_path: str
    minio_path: str
    folder_path: Optional[str] = "/"
    upload_date: datetime
    indexing_status: IndexingStatus
    status: DocumentStatus

# Conversation schemas
class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    user_id: str

class ConversationResponse(ConversationBase):
    id: str
    user_id: str
    created_date: datetime

# Chat schemas
class Citation(BaseModel):
    documentId: str
    documentPath: str
    text: str

# Message schemas
class MessageBase(BaseModel):
    content: str
    is_user: bool

class MessageCreate(MessageBase):
    conversation_id: str

class MessageResponse(MessageBase):
    id: str
    timestamp: datetime
    citations: List[Citation] = Field(default_factory=list)

# Chat schemas
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    message_id: str
    citations: List[Citation] = Field(default_factory=list)

# Embedding job schemas
class EmbeddingJobResponse(BaseModel):
    id: str
    status: EmbeddingJobStatus
    progress: int = Field(ge=0, le=100)
    created_date: datetime

# Standard API response
class APIResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str = ""
    errors: List[str] = []
