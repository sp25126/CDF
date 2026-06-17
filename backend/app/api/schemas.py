from pydantic import BaseModel, Field
from typing import List, Optional, Union, Any, Dict

class CommandRequest(BaseModel):
    text: str
    session_id: str
    context: Optional[dict] = None
    source_mode: Optional[bool] = False

class Citation(BaseModel):
    source_title: str
    snippet: str
    page_number: Optional[int] = None
    section_label: Optional[str] = None

class ExplainResponse(BaseModel):
    mode: str = "explain"
    title: str
    grade_level: int
    bullets: List[str]
    example: str
    recap: str
    response_text: str
    language_mode: Optional[str] = None
    source_mode: Optional[bool] = None
    citations: Optional[List[Citation]] = None

class QuizQuestion(BaseModel):
    id: int
    question: str
    options: List[str]
    correct_answer: str

class QuizResponse(BaseModel):
    mode: str = "quiz"
    title: str
    instructions: str
    questions: List[QuizQuestion]
    answer_key: Union[str, List[str]]
    response_text: str
    language_mode: Optional[str] = None
    source_mode: Optional[bool] = None
    citations: Optional[List[Citation]] = None

class ClarifyResponse(BaseModel):
    mode: str = "clarify"
    message: str
    suggestions: List[str]
    response_text: str
    language_mode: Optional[str] = None
    source_mode: Optional[bool] = None
    citations: Optional[List[Citation]] = None

class GlobalResponse(BaseModel):
    status: str = "success"
    data: Optional[Any] = None
    error: Optional[dict] = None

# New Source-specific Request Schemas
class UrlSourceRequest(BaseModel):
    url: str

class TextSourceRequest(BaseModel):
    title: str
    text: str

class SourceMetadata(BaseModel):
    id: str
    title: str
    type: str
    page_count: Optional[int] = None
    origin_url: Optional[str] = None
    language: str
    created_at: str
