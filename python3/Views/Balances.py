from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QGridLayout, QTableWidget,
    QTableWidgetItem, QLabel, QSizePolicy)

from Views.OrderBookWithSelectors import CTOrderBookWithSelectors

class CTBalances(QWidget):
    def __init__(self, CTMain = None):
        super().__init__()

        self._CTMain = CTMain

        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._label_btc_usd_price = QLabel("")
        self._balances_summary_table = QTableWidget()
        self._balances_summary_table.setSizePolicy(sizePolicy);
        self._label_balances_details = QLabel("Holdings of individual currencies and their total BTC value")
        self._balances_details_table = QTableWidget()
        self._balances_details_table.setSizePolicy(sizePolicy);
        self._layout = QGridLayout()
        self._layout.addWidget(self._label_btc_usd_price, 0, 0)
        self._layout.addWidget(self._balances_summary_table, 1, 0)
        self._layout.addWidget(self._label_balances_details, 2, 0)
        self._layout.addWidget(self._balances_details_table, 3, 0)
        self._layout.setRowStretch(0, 1);
        self._layout.setRowStretch(1, 10);
        self._layout.setRowStretch(2, 1);
        self._layout.setRowStretch(3, 30);
        self.reload_balances()
        self.setLayout(self._layout)

        self.show()

    def reload_balances(self):
        # Populate current BTC price in USD
        self._btc_usd_price = self._CTMain._Crypto_Trader.trader['Coinbase'].get_btc_usd_price()
        self._label_btc_usd_price.setText("BTC price: {0:,.2f} USD".format(self._btc_usd_price))
        self._label_btc_usd_price.repaint()

        # Populate balances summary table
        self._balances_summary = self._CTMain._Crypto_Trader.calculate_balances_btc_totals(self._btc_usd_price)
        self._balances_summary_table.setRowCount(len(self._balances_summary) + 1)
        self._balances_summary_table.setColumnCount(3)
        self._balances_summary_table.verticalHeader().hide()
        self._balances_summary_table.setHorizontalHeaderLabels([
            'Exchange',
            'BTC',
            'USD'
        ])

        cell_index = 0
        totals = {'BTC': 0.0, 'USD': 0.0}
        ordered_exchanges = sorted(self._balances_summary.keys())
        for exchange in ordered_exchanges:
            self._balances_summary_table.setItem(cell_index, 0, QTableWidgetItem(exchange))
            self._balances_summary_table.setItem(cell_index, 1, QTableWidgetItem("{0:,.8f}".format(self._balances_summary[exchange]['BTC'])))
            self._balances_summary_table.setItem(cell_index, 2, QTableWidgetItem("{0:,.2f}".format(self._balances_summary[exchange]['USD'])))
            self._balances_summary_table.item(cell_index, 1).setTextAlignment(Qt.AlignRight)
            self._balances_summary_table.item(cell_index, 2).setTextAlignment(Qt.AlignRight)
            totals['BTC'] += self._balances_summary[exchange]['BTC']
            totals['USD'] += self._balances_summary[exchange]['USD']
            cell_index += 1
        self._balances_summary_table.setItem(cell_index, 0, QTableWidgetItem("Total"))
        self._balances_summary_table.setItem(cell_index, 1, QTableWidgetItem("{0:,.8f}".format(totals['BTC'])))
        self._balances_summary_table.setItem(cell_index, 2, QTableWidgetItem("{0:,.2f}".format(totals['USD'])))
        self._balances_summary_table.item(cell_index, 1).setTextAlignment(Qt.AlignRight)
        self._balances_summary_table.item(cell_index, 2).setTextAlignment(Qt.AlignRight)

        # Populate balances details table
        self._balances_details = self._CTMain._Crypto_Trader._balances_btc
        self._balances_details_table.setRowCount(len(self._balances_details))
        self._balances_details_table.setColumnCount(len(self._balances_summary) + 2)
        self._balances_details_table.verticalHeader().hide()
        self._balances_details_table.setHorizontalHeaderLabels(['Currency Code'] + ordered_exchanges + ['TotalBtcValue'])

        row_index = 0
        for code, holdings in sorted(self._balances_details.items(), key=lambda k_v: k_v[1]['TotalBtcValue'], reverse=True):
            column_index = 0
            self._balances_details_table.setItem(row_index, column_index, QTableWidgetItem(code))
            for exchange in ordered_exchanges:
                column_index += 1
                if exchange in holdings:
                    self._balances_details_table.setItem(row_index, column_index, QTableWidgetItem("{0:,.8f}".format(holdings[exchange]['Total'])))
                    self._balances_details_table.item(row_index, column_index).setTextAlignment(Qt.AlignRight)
            column_index += 1
            self._balances_details_table.setItem(row_index, column_index, QTableWidgetItem("{0:,.8f}".format(holdings['TotalBtcValue'])))
            self._balances_details_table.item(row_index, column_index).setTextAlignment(Qt.AlignRight)
            row_index += 1
