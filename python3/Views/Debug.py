from pprint import pformat
from PyQt5.QtWidgets import (QWidget, QGridLayout, QTextEdit, QPushButton)

class CTDebug(QWidget):
    def __init__(self, CTMain = None):
        super().__init__()
        self._CTMain = CTMain

        self._layout = QGridLayout()
        self._layout.setRowStretch(0, 1)
        self._layout.setRowStretch(1, 1)
        self._layout.setRowStretch(2, 4)

        self._text_field_code = QTextEdit()
        self._text_field_code.setPlaceholderText("Code to Run (e.g. self._CTMain._Crypto_Trader.trader['Poloniex'].get_all_markets())")

        self._button = QPushButton()
        self._button.setText("Run Code");
        self._button.clicked.connect(self.run_code)

        self._text_field_output = QTextEdit()
        self._text_field_output.setReadOnly(True)

        self._layout.addWidget(self._text_field_code, 0, 0)
        self._layout.addWidget(self._button, 1, 0)
        self._layout.addWidget(self._text_field_output, 2, 0)
        self.setLayout(self._layout)

    def run_code(self):
        self._text_field_output.setText(pformat(eval(self._text_field_code.toPlainText())))
