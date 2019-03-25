from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem)


class CTActiveMarkets(QWidget):
    def __init__(self, CTMain = None):
        super().__init__()

        self._CTMain = CTMain

        self._tableWidget = QTableWidget()
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._tableWidget)
        self.show_markets()
        self.setLayout(self._layout)

    def show_markets(self):
        exchanges = sorted(self._CTMain._Crypto_Trader._map_exchange_code_to_currency_code.keys())
        column_names = ['BaseCode', 'CurrencyCode'] + exchanges
        markets = self._CTMain._Crypto_Trader.load_active_markets()
        markets.pop(None)
        row_count = 0
        for code_base in markets:
            row_count += len(markets[code_base])

        self._tableWidget.setRowCount(row_count)
        self._tableWidget.setColumnCount(len(column_names))
        self._tableWidget.verticalHeader().hide()
        self._tableWidget.setHorizontalHeaderLabels(column_names)

        cell_index = 0
        for code_base in sorted(markets.keys()):
            for code_curr in sorted(markets[code_base].keys()):
                self._tableWidget.setItem(cell_index, 0, QTableWidgetItem(code_base))
                self._tableWidget.setItem(cell_index, 1, QTableWidgetItem(code_curr))
                for exchange_i in range(len(exchanges)):
                    if exchanges[exchange_i] in markets[code_base][code_curr]:
                        self._tableWidget.setItem(
                            cell_index,
                            exchange_i + 2,
                            QTableWidgetItem(markets[code_base][code_curr][exchanges[exchange_i]]['MarketSymbol'])
                        )
                cell_index += 1
