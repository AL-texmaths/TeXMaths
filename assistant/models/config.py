from pydantic import BaseModel, Field

class CurrentSettings(BaseModel):
    theme: str
    catalogue: str | None
    type: str | None
    current_file_path: str | None
    code_index_file_name: str | None
    pdf_data_file_name: str | None

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
    level_colors: list[str] = Field(default_factory=list)
    type_colors: dict[str, str] = Field(default_factory=dict)

class DocumentTabGUIModel(BaseModel):
    vertical_splitter: int
    horizontal_splitter: int

class GUIModel(BaseModel):
    main_window: DialogConfig
    unused_items_dialog: DialogConfig
    splitter: SplittersModel
    progression_tree: ProgressionTreeModel
    documents_tab: DocumentTabGUIModel

class ThemeColorsModel(BaseModel):
    bg: str
    fg: str
    panel: str
    accent: str
    border: str
    focus_bg: str
    focus_border: str

class ThemeTreeModel(BaseModel):
    items_height: str
    padding: str

class FontStyleModel(BaseModel):
    family: str
    size: str

class ThemeStyleModel(BaseModel):
    font: FontStyleModel
    progression_tree: ThemeTreeModel    

class ThemeModel(BaseModel):
    colors: ThemeColorsModel
    style: ThemeStyleModel

class PedagoDocTypeModel(BaseModel):
    name: str
    dir_name: str
    tex_name: str
    name_pattern: str

class PedagoServiceModel(BaseModel):
    metadata: list[str]
    to_convert: list[str]
    pedago_doc_types: dict[str, PedagoDocTypeModel]
    string_check_order: list[str]
    tex_non_optional_keys: list[str]

class Settings(BaseModel):
    gui: GUIModel
    pedago_service: PedagoServiceModel
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
    update_code_index: ActionSettings
    update_data_index: ActionSettings
    check_database: ActionSettings
    latexmk_all_tex_files: ActionSettings
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
    restore_default_settings: ActionSettings
    extract_flash_previews: ActionSettings
    update_flash_previews: ActionSettings
    toggle_detailed_mode: ActionSettings

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