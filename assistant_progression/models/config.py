from pydantic import BaseModel, Field

class CurrentSettings(BaseModel):
    theme: str
    code: str


class Settings(BaseModel):
    main_window_title: str
    themes: dict
    current: CurrentSettings


class CatalogueMetadata(BaseModel):
    name: str
    tex_file_name: str
    sty_file_name: str
    types: list[str] = Field(default_factory=list)


class Config(BaseModel):
    executables: dict[str, list[str]]
    paths_candidates: dict[str, list[str]]
    catalogues: dict[str, CatalogueMetadata]
    codes: dict[str, str]
    settings: Settings