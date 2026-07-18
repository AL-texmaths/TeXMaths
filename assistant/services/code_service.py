class CodeService:

    def __init__(self, code_labels):

        self.code_labels = code_labels

        self.entries = []

    def display_name(self, code):
        code_label = self.code_labels.get(code)
        if code_label is None:
            return code

        return code_label.name

    def internal_name(self, display):

        for code, label in self.code_labels.items():

            if label.name == display:
                return code

        return display