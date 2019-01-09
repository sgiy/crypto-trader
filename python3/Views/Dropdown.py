from PyQt5.QtWidgets import QComboBox

class Dropdown(QComboBox):
    def __init__(self, items_list, selected_value):
        super().__init__()
        self.addItems(items_list)
        self.setCurrentText(selected_value)
