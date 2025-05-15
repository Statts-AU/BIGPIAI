from pydantic import BaseModel


class Section(BaseModel):
    name: str
    page_number: str


class TocEntries(BaseModel):
    entries: list[Section]
