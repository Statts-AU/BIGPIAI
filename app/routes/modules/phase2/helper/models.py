from pydantic import BaseModel


class Section(BaseModel):
    name: str
    page_number: int


class TocEntries(BaseModel):
    entries: list[Section]
