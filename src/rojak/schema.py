from enum import Enum

from pydantic import BaseModel, Field, field_validator


class TaskType(str, Enum):
    normalize = "normalize"
    intent = "intent"
    instruct = "instruct"
    translate = "translate"


class Status(str, Enum):
    draft = "draft"
    verified = "verified"


INTENT_LABELS = ("complaint", "inquiry", "praise", "request", "other")


class Item(BaseModel):
    id: str
    task: TaskType
    prompt: str
    reference: str
    languages: list[str] = Field(min_length=1)
    status: Status = Status.draft
    meta: dict[str, str] = Field(default_factory=dict)

    @field_validator("prompt", "reference")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v

    @field_validator("reference")
    @classmethod
    def intent_label_valid(cls, v: str, info) -> str:
        if info.data.get("task") == TaskType.intent and v not in INTENT_LABELS:
            raise ValueError(f"intent reference must be one of {INTENT_LABELS}")
        return v


class Prediction(BaseModel):
    id: str
    model: str
    output: str
