from pydantic import BaseModel


class Subsection(BaseModel):
    Subheader: str
    Requirements: list[str]
    PageLimit: str


class Section(BaseModel):
    Header: str
    Subheaders: list[Subsection]


class SectionEntries(BaseModel):
    Sections: list[Section]