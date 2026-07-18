from PySide6.QtWidgets import QMenu


class FilterPDFDocumentsMenu(QMenu):
    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.filter_type_menu = QMenu("Filtrer par type", self)
        self.filter_field_menu = QMenu("Filtrer par champ", self)
    
    def rebuild_types_menu(self, types):
        self.clear()
        for type_name in types:
            action = self.filter_type_menu.addAction(type_name)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(self.parent().document_tab.update_results)
        self.addMenu(self.filter_type_menu)
    
    def rebuild_fields_menu(self, fields):
        self.filter_field_menu.clear()
        for field_name in fields:
            action = self.filter_field_menu.addAction(field_name)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(self.parent().document_tab.update_results)
        self.addMenu(self.filter_field_menu)

    def get_checked_types(self):
        checked_types = []
        for action in self.filter_type_menu.actions():
            if action.isChecked():
                checked_types.append(action.text())
        return checked_types

    def get_checked_fields(self):
        checked_fields = []
        for action in self.filter_field_menu.actions():
            if action.isChecked():
                checked_fields.append(action.text())
        return checked_fields