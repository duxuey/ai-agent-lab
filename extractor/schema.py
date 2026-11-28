"""数据契约：模型只允许输出符合这个 schema 的 JSON。"""
from pydantic import BaseModel, Field, field_validator


class TodoItem(BaseModel):
    todo: str = Field(min_length=2, description="待办内容")
    owner: str = Field(description="责任人；原文没有就写 未提及")
    due: str = Field(description="截止时间；原文没有就写 未提及")
    evidence: str = Field(min_length=5, description="逐字摘抄的原文依据")

    @field_validator("owner", "due")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("不能为空字符串，未知请写「未提及」")
        return v


class ExtractionResult(BaseModel):
    items: list[TodoItem] = Field(default_factory=list)
    note: str = ""
