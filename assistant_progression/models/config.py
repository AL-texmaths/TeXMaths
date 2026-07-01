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

class ActionSettings(BaseModel):
    text: str
    shortcut: str | None = None
    icon: str | None = None
    checkable: bool = False

class ActionsConfig(BaseModel):
    add_level: ActionSettings
    add_chapter: ActionSettings
    add_seance: ActionSettings
    add_selected_item: ActionSettings
    delete_selected_item: ActionSettings
    show_unused_items: ActionSettings
    set_left_focus: ActionSettings
    set_right_focus: ActionSettings
    open_config_file: ActionSettings
    update_code_index_main: ActionSettings
    load_progression: ActionSettings
    save_progression: ActionSettings
    save_under_progression: ActionSettings
    export_progression: ActionSettings
    toggle_progression_panel: ActionSettings

class Config(BaseModel):
    executables: dict[str, list[str]]
    paths_candidates: dict[str, list[str]]
    catalogues: dict[str, CatalogueMetadata]
    codes: dict[str, str]
    settings: Settings
    actions: ActionsConfig