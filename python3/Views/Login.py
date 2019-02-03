import os, sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QGridLayout, QGroupBox, QFormLayout,
    QLabel, QLineEdit, QPushButton)

from Protection import Protector

class CTLogin(QWidget):
    def __init__(self, CTMain = None):
        super().__init__()

        self._CTMain = CTMain
        self._file_name = os.path.join(sys.path[0], 'encrypted_settings')
        self.init_layout()

    def init_layout(self):
        if hasattr(self._CTMain, '_settings'):
            while self._layout.count():
                child = self._layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            if os.path.isfile(self._file_name):
                self._label_text = 'Please enter your password:'
            else:
                self._label_text = 'Please create a password to encrypt your settings'

            self._form_group_box = QGroupBox(self._label_text)
            group_box_layout = QFormLayout()
            self._textbox_password = QLineEdit('', self)
            self._textbox_password.returnPressed.connect(self.enter_password)
            group_box_layout.addRow(QLabel("Password:"), self._textbox_password)
            self._form_group_box.setLayout(group_box_layout)

            self._enter_button = QPushButton()
            self._enter_button.setText("OK");
            self._enter_button.clicked.connect(self.enter_password)

            self._label_notification = QLabel('')
            self._label_notification.setAlignment(Qt.AlignLeft | Qt.AlignTop)

            self._layout = QGridLayout()
            self._layout.setRowStretch(0, 3)
            self._layout.setRowStretch(1, 1)
            self._layout.setRowStretch(2, 1)
            self._layout.setRowStretch(3, 3)
            self._layout.setColumnStretch(0, 1)
            self._layout.setColumnStretch(1, 1)
            self._layout.setColumnStretch(2, 1)
            self._layout.addWidget(self._form_group_box, 1, 1)
            self._layout.addWidget(self._enter_button, 2, 1)
            self._layout.addWidget(self._label_notification, 3, 1)
            self.setLayout(self._layout)

        self.show()

    def enter_password(self):
        protector = Protector(self._textbox_password.text())
        if os.path.isfile(self._file_name):
            try:
                self._CTMain._settings = protector.decrypt_file(self._file_name)
                self.init_layout()
            except:
                self._label_notification.setText('Wrong password!')
        else:
            self._CTMain._settings = {}
            protector.save_encrypted_file(self._CTMain._settings, self._file_name)
