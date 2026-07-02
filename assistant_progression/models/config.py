from pydantic import BaseModel, Field

class CurrentSettings(BaseModel):
    theme: str
    catalogue: str | None
    type: str | None
    current_file: str | None

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

class DialogConfig(BaseModel):
    title: str
    width: int
    height: int

class Settings(BaseModel):
    main_window: DialogConfig
    unused_items_dialog: DialogConfig
    themes: dict
    current: CurrentSettings


class CatalogueMetadata(BaseModel):
    name: str
    tex_file_name: str
    sty_file_name: str
    types: list[str] = Field(default_factory=list)

class ActionSettings(BaseModel):
    text: str
    shortcut: str
    button: bool = True
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
    save_as_progression: ActionSettings
    export_progression: ActionSettings
    toggle_progression_panel: ActionSettings
    close: ActionSettings
    undo: ActionSettings
    redo: ActionSettings
    move_item_up: ActionSettings
    move_item_down: ActionSettings

class Config(BaseModel):
    executables: dict[str, list[str]]
    paths_candidates: dict[str, list[str]]
    catalogues: dict[str, CatalogueMetadata]
    codes: dict[str, str]
    settings: Settings
    actions: ActionsConfig