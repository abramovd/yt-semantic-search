# from sqlmodel import SQLModel, Field, Relationship, JSON, Column, String, Text
# from sqlalchemy.dialects.mysql import JSON
# from typing import Optional, List
# from mariadb_vector import Vector
# from datetime import datetime

# # class Document(SQLModel, table=True):
# #     id: Optional[int] = Field(default=None, primary_key=True)
# #     title: str = Field(sa_column=Column(String(512)))
# #     created_at: datetime = Field(default_factory=datetime.utcnow)
# #     meta: dict = Field(sa_type=JSON, nullable=False)

# #     chunks: List["Chunk"] = Relationship(back_populates="document")


# # class Chunk(SQLModel, table=True):
# #     id: Optional[int] = Field(default=None, primary_key=True)

# #     chunk_index: int
# #     start_ts: int
# #     end_ts: int
# #     text: str = Field(sa_column=Column(Text))

# #     document_id: int = Field(foreign_key="document.id")
# #     document: Document | None = Relationship(back_populates="chunks")

# #     embedding: list[float] = Field(sa_column=Column(Vector(384)))
