from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton)


class CTCurrencies(QWidget):
    def __init__(self, CTMain=None):
        super().__init__()

        self._CTMain = CTMain

        self._layout = QVBoxLayout()

        self._reload_currencies_button = QPushButton()
        self._reload_currencies_button.setText("Reload currency definitions from exchanges")
        self._reload_currencies_button.clicked.connect(self._CTMain._Crypto_Trader.init_currencies)
        self._layout.addWidget(self._reload_currencies_button)

        self._tableWidget = QTableWidget()
        self._layout.addWidget(self._tableWidget)
        self.setLayout(self._layout)

        self.show_currencies()
        self._timer_painter = QTimer(self)
        self._timer_painter.start(2000)
        self._timer_painter.timeout.connect(self.show_currencies)

    def show_currencies(self):
        exchanges = sorted(self._CTMain._Crypto_Trader._map_exchange_code_to_currency_code.keys())
        column_names = ['Code'] + exchanges
        code_map = self._CTMain._Crypto_Trader._map_currency_code_to_exchange_code
        codes = sorted(code_map.keys())
        self._tableWidget.setRowCount(len(codes))
        self._tableWidget.setColumnCount(len(column_names))
        self._tableWidget.verticalHeader().hide()
        self._tableWidget.setHorizontalHeaderLabels(column_names)
        cell_index = 0
        for code in codes:
            self._tableWidget.setItem(cell_index, 0, QTableWidgetItem(code))
            for exchange_i in range(len(exchanges)):
                exchange_name_column = exchanges[exchange_i] + 'Name'
                if exchanges[exchange_i] in code_map[code] and exchange_name_column in code_map[code]:
                    self._tableWidget.setItem(
                        cell_index,
                        exchange_i + 1,
                        QTableWidgetItem('{0}: {1}'.format(code_map[code][exchanges[exchange_i]],
                                                           code_map[code][exchange_name_column]))
                    )
            cell_index += 1
