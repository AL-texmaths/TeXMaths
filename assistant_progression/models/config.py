from pydantic import BaseModel, Field

class CurrentSettings(BaseModel):
    theme: str
    catalogue: str | None
    type: str | None
    current_file_path: str | None

    @property
    def size(self) -> tuple[int, int]:
        return (self.width, self.height)

class DialogConfig(BaseModel):
    title: str
    width: int
    height: int

class SplittersModel(BaseModel):
    size: list

class ProgressionTreeModel(BaseModel):
    scrolling_step: int

class GUIModel(BaseModel):
    main_window: DialogConfig
    unused_items_dialog: DialogConfig
    splitter: SplittersModel
    progression_tree: ProgressionTreeModel

class ThemeColorsModel(BaseModel):
    bg: str
    fg: str
    panel: str
    accent: str
    border: str
    focus_bg: str
    focus_border: str
    font: str

class ThemeTreeModel(BaseModel):
    items_height: str
    padding: str

class ThemeStyleModel(BaseModel):
    progression_tree: ThemeTreeModel    

class ThemeModel(BaseModel):
    colors: ThemeColorsModel
    style: ThemeStyleModel

class Settings(BaseModel):
    gui: GUIModel
    themes: dict[str, ThemeModel]
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
    add_custom_item: ActionSettings
    add_level: ActionSettings
    add_chapter: ActionSettings
    add_seance: ActionSettings
    add_selected_item: ActionSettings
    delete_selected_branch: ActionSettings
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
    copy_item: ActionSettings
    cut_item: ActionSettings
    paste_item: ActionSettings

class CodeLabelModel(BaseModel):
    name: str
    command: str

class Config(BaseModel):
    executables: dict[str, list[str]]
    paths_candidates: dict[str, list[str]]
    catalogues: dict[str, CatalogueMetadata]
    codes: dict[str, CodeLabelModel]
    settings: Settings
    actions: ActionsConfig