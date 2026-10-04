from pydantic import BaseModel, ConfigDict, Field


class ChatHistoryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: str = Field(pattern=r"^(user|assistant)$")
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatHistoryItem] = Field(default_factory=list, max_length=8)


class ChatResponse(BaseModel):
    message: str
