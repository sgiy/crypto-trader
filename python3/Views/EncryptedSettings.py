import os
import shutil
import sys

from PyQt5.QtWidgets import (QWidget, QGridLayout, QGroupBox, QLabel, QLineEdit, QPushButton)

from Protection import Protector


class CTEncryptedSettings(QWidget):
    def __init__(self, CTMain = None):
        super().__init__()

        self._CTMain = CTMain
        self._full_file_path = os.path.join(sys.path[0], 'encrypted_settings')
        self.init_layout()

    def init_layout(self):
        self._label_notification = QLabel('')
        if not hasattr(self, '_layout'):
            self._layout = QGridLayout()
            self._layout.setRowStretch(0, 3)
            self._layout.setRowStretch(1, 1)
            self._layout.setRowStretch(2, 1)
            self._layout.setRowStretch(3, 3)
            self._layout.setColumnStretch(0, 1)
            self._layout.setColumnStretch(1, 1)
            self._layout.setColumnStretch(2, 1)
            self._layout.setColumnStretch(3, 1)
            self.setLayout(self._layout)

        # Clear self._layout if already populated
        if hasattr(self, '_layout'):
            while self._layout.count():
                child = self._layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

        # Forming a form for exchange API keys
        self._form_api_keys = QGroupBox('Exchange API Keys')
        api_keys_layout = QGridLayout()
        api_keys_layout.setRowStretch(0, 1)
        api_keys_layout.addWidget(QLabel('Exchange'), 0, 0)
        api_keys_layout.addWidget(QLabel('API Key'), 0, 1)
        api_keys_layout.addWidget(QLabel('Secret'), 0, 2)
        api_keys_layout.addWidget(QLabel('API Password'), 0, 3)
        row_index = 1
        self._api_key_inputs = {}
        for exchange in sorted(self._CTMain._settings['Exchanges with Trading API']):
            api_keys_layout.setRowStretch(row_index, 1)

            self._api_key_inputs[exchange] = {}
            self._api_key_inputs[exchange]['APIKey'] = QLineEdit(self._CTMain._API_KEYS.get(exchange, {}).get('APIKey', ''), self)
            self._api_key_inputs[exchange]['Secret'] = QLineEdit(self._CTMain._API_KEYS.get(exchange, {}).get('Secret', ''), self)
            self._api_key_inputs[exchange]['APIPassword'] = QLineEdit(self._CTMain._API_KEYS.get(exchange, {}).get('APIPassword', ''), self)
            if self._CTMain._settings['Exchanges with Trading API'][exchange].get('APIPassword','True') == 'False':
                self._api_key_inputs[exchange]['APIPassword'].setReadOnly(True)

            api_keys_layout.addWidget(QLabel(exchange), row_index, 0)
            api_keys_layout.addWidget(self._api_key_inputs[exchange]['APIKey'], row_index, 1)
            api_keys_layout.addWidget(self._api_key_inputs[exchange]['Secret'], row_index, 2)
            api_keys_layout.addWidget(self._api_key_inputs[exchange]['APIPassword'], row_index, 3)
            row_index += 1
        self._form_api_keys.setLayout(api_keys_layout)
        self._layout.addWidget(self._form_api_keys, 0, 1, 1, 2)

        self._form_save = QGroupBox("Save Changes")
        save_layout = QGridLayout()
        save_layout.addWidget(QLabel("Password:"), 0, 0)
        self._textbox_password = QLineEdit('', self)
        self._textbox_password.setEchoMode(QLineEdit.Password)
        self._textbox_password.returnPressed.connect(self.save_changes)
        save_layout.addWidget(self._textbox_password, 0, 1)
        self._save_button = QPushButton()
        self._save_button.setText("Save")
        self._save_button.clicked.connect(self.save_changes)
        save_layout.addWidget(self._save_button, 1, 0, 1, 2)
        self._form_save.setLayout(save_layout)

        self._layout.addWidget(self._form_save, 2, 1, 1, 2)
        self._layout.addWidget(self._label_notification, 3, 1, 1, 2)
        # self.show()

    def save_changes(self):
        password = self._textbox_password.text()
        if len(password) < 8:
            self._label_notification.setText('Password is too short! Please enter at least 8 characters!')
            return
        protector = Protector(password)
        settings_to_save = self._CTMain._settings
        settings_to_save['API Keys'] = {}
        for exchange in self._api_key_inputs:
            settings_to_save['API Keys'][exchange] = {}
            settings_to_save['API Keys'][exchange]['APIKey'] = self._api_key_inputs[exchange]['APIKey'].text()
            settings_to_save['API Keys'][exchange]['Secret'] = self._api_key_inputs[exchange]['Secret'].text()
            settings_to_save['API Keys'][exchange]['APIPassword'] = self._api_key_inputs[exchange]['APIPassword'].text()
        shutil.copy2(self._full_file_path, self._full_file_path + '_backup')
        protector.save_encrypted_file(settings_to_save, self._full_file_path)
        self._CTMain._API_KEYS = settings_to_save['API Keys']
        self._CTMain.initCryptoTrader()
        self._label_notification.setText('Saved!')
