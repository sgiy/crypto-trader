import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QGridLayout, QGroupBox, QFormLayout, QLabel, QLineEdit, QTextEdit, QPushButton)

from Protection import Protector


class CTLogin(QWidget):
    def __init__(self, CTMain=None):
        super().__init__()

        self._CTMain = CTMain
        self._full_file_path = os.path.join(sys.path[0], 'encrypted_settings')

        # Initialize grid layout
        self._layout = QGridLayout()
        self._layout.setRowStretch(0, 2)
        self._layout.setRowStretch(1, 1)
        self._layout.setRowStretch(2, 1)
        self._layout.setRowStretch(3, 1)
        self._layout.setRowStretch(4, 1)
        self._layout.setRowStretch(5, 2)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 1)
        self._layout.setColumnStretch(2, 1)
        self._layout.setColumnStretch(3, 1)

        # Create top and bottom notifications
        self._label_bottom = QTextEdit('')
        self._label_bottom.setReadOnly(True)
        self._label_bottom.setStyleSheet("""
            background-color: #f1f1f1;
            border: none;
        """)
        if os.path.isfile(self._full_file_path):
            self._label_top_text = 'Please enter your password to load your API keys or press button below ' + \
                                   'to continue with public data'
        else:
            self._label_top_text = 'Please create a password to encrypt your API Keys'
            self._label_bottom.setText('It is recommended to use longer passwords that include lower and ' +
                                       'upper case letters, numbers, and special characters.')
        self._label_top = QTextEdit(self._label_top_text)
        self._label_top.setReadOnly(True)
        self._label_top.setAlignment(Qt.AlignCenter)
        self._label_top.setStyleSheet("""
            background-color: #f1f1f1;
            border: none;
        """)

        self._password_form_box = QGroupBox("")
        group_box_layout = QFormLayout()
        self._textbox_password = QLineEdit('', self)
        self._textbox_password.setEchoMode(QLineEdit.Password)
        self._textbox_password.returnPressed.connect(self.enter_password)
        self._label_password = QLabel("Password:")
        self._label_password.setMinimumSize(100, 23)
        group_box_layout.addRow(self._label_password, self._textbox_password)
        self._password_form_box.setLayout(group_box_layout)

        self._enter_button = QPushButton()
        self._enter_button.setText("OK")
        self._enter_button.clicked.connect(self.enter_password)

        self._skip_button = QPushButton()
        self._skip_button.setText("Proceed without unlocking encrypted settings")
        self._skip_button.clicked.connect(self.skip_password)

        self._layout.addWidget(self._label_top, 1, 1, 1, 2)
        self._layout.addWidget(self._password_form_box, 2, 1, 1, 2)
        self._layout.addWidget(self._enter_button, 3, 1, 1, 2)
        if os.path.isfile(self._full_file_path):
            self._layout.addWidget(self._skip_button, 4, 1, 1, 2)
        self._layout.addWidget(self._label_bottom, 5, 1, 1, 2)

        self.setLayout(self._layout)
        self.show()

    def enter_password(self):
        password = self._textbox_password.text()
        protector = Protector(password)
        if os.path.isfile(self._full_file_path):
            try:
                # Decrypt encrypted settings
                decrypted_settings = protector.decrypt_file(self._full_file_path)
                self._label_bottom.setText('')
            except:
                self._label_bottom.setText('Wrong password!')
                return

            # Split out API Keys and store them separately if they are present
            self._CTMain._API_KEYS = decrypted_settings.pop('API Keys', {})

            # Add to regular settings a list of names of exchanges with API Keys
            decrypted_settings['Exchanges with API Keys'] = list(self._CTMain._API_KEYS.keys())

            # Add regular settings to _settings
            if not hasattr(self._CTMain, '_settings'):
                self._CTMain._settings = {}
            self._CTMain._settings.update(decrypted_settings)
            # Update settings with decrypted values that take precedence.
            # Initialize the system, and show balances view by default
            self._CTMain.init_gui()
            self._CTMain.switch_view('Balances')

        else:
            if len(password) < 8:
                self._label_bottom.setText('Password is too short! Please enter at least 8 characters!')
                return
            # A new file with default settings is created and the system is
            # initiated. Then go to settings view to enter api keys
            self._CTMain._API_KEYS = {}
            protector.save_encrypted_file(self._CTMain._settings, self._full_file_path)
            self._CTMain.init_gui()
            self._CTMain.switch_view('ViewSettings')

    def skip_password(self):
        # If user chooses to skip decrypting settings, declare default values,
        # initialize the system, and show currency pair view by default
        self._CTMain._API_KEYS = {}
        self._CTMain.init_gui()
        self._CTMain.switch_view('ViewPair')
