from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QLabel)

from Views.OrderBookWithSelectors import CTOrderBookWithSelectors

class CTBalances(QWidget):
    def __init__(self, CTMain = None):
        super().__init__()

        self._CTMain = CTMain

        self._label_btc_usd_price = QLabel("")
        self._tableWidget = QTableWidget()
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._label_btc_usd_price)
        self._layout.addWidget(self._tableWidget)
        self.reload_balances()
        self.setLayout(self._layout)

        self.show()

    def reload_balances(self):
        self._btc_usd_price = self._CTMain._Crypto_Trader.trader['Coinbase'].get_btc_usd_price()
        self._label_btc_usd_price.setText("BTC price: {0:,.2f} USD".format(self._btc_usd_price))
        self._label_btc_usd_price.repaint()
        self._balances = self._CTMain._Crypto_Trader.calculate_balances_btc_totals(self._btc_usd_price)
        self._tableWidget.setRowCount(len(self._balances) + 1)
        self._tableWidget.setColumnCount(3)
        self._tableWidget.verticalHeader().hide()
        self._tableWidget.setHorizontalHeaderLabels([
            'Exchange',
            'BTC',
            'USD'
        ])

        cell_index = 0
        totals = {'BTC': 0.0, 'USD': 0.0}
        for exchange in sorted(self._balances.keys()):
            self._tableWidget.setItem(cell_index, 0, QTableWidgetItem(exchange))
            self._tableWidget.setItem(cell_index, 1, QTableWidgetItem("{0:,.8f}".format(self._balances[exchange]['BTC'])))
            self._tableWidget.setItem(cell_index, 2, QTableWidgetItem("{0:,.2f}".format(self._balances[exchange]['USD'])))
            self._tableWidget.item(cell_index, 1).setTextAlignment(Qt.AlignRight)
            self._tableWidget.item(cell_index, 2).setTextAlignment(Qt.AlignRight)
            totals['BTC'] += self._balances[exchange]['BTC']
            totals['USD'] += self._balances[exchange]['USD']
            cell_index += 1
        self._tableWidget.setItem(cell_index, 0, QTableWidgetItem("Total"))
        self._tableWidget.setItem(cell_index, 1, QTableWidgetItem("{0:,.8f}".format(totals['BTC'])))
        self._tableWidget.setItem(cell_index, 2, QTableWidgetItem("{0:,.2f}".format(totals['USD'])))
        self._tableWidget.item(cell_index, 1).setTextAlignment(Qt.AlignRight)
        self._tableWidget.item(cell_index, 2).setTextAlignment(Qt.AlignRight)
