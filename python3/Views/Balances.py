from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QLabel, QSizePolicy)

from Views.OrderBookWithSelectors import CTOrderBookWithSelectors

class CTBalances(QWidget):
    def __init__(self, CTMain = None):
        super().__init__()

        self._CTMain = CTMain

        self._label_btc_usd_price_summary = QLabel("")
        self._label_btc_usd_price_details = QLabel("")
        self._balances_summary_table = QTableWidget()
        self._balances_details_table = QTableWidget()

        self._tabs = QTabWidget()
        self._tab1 = QWidget()
        self._tab2 = QWidget()
        self._tabs.addTab(self._tab1, "Balances Summary")
        self._tabs.addTab(self._tab2, "Balances Details")

        self._tab1.layout = QVBoxLayout()
        self._tab1.layout.addWidget(self._label_btc_usd_price_summary)
        self._tab1.layout.addWidget(self._balances_summary_table)
        self._tab1.setLayout(self._tab1.layout)

        self._tab2.layout = QVBoxLayout()
        self._tab2.layout.addWidget(self._label_btc_usd_price_details)
        self._tab2.layout.addWidget(self._balances_details_table)
        self._tab2.setLayout(self._tab2.layout)

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._tabs)
        self.setLayout(self._layout)

        self.reload_balances()
        self.setStyleSheet("""
                QTableWidget::item {
                    padding: 2px 4px;
                    border-style: none;
                    margin: 0px;
                    height: 1.0em;
                    min-height: 1.0em;
                    max-height: 1.0em;
                }
            """)
        self.show()

    def reload_balances(self):
        # Populate current BTC price in USD
        self._btc_usd_price = self._CTMain._Crypto_Trader.trader['Coinbase'].get_btc_usd_price()
        self._label_btc_usd_price_summary.setText("BTC price: {0:,.2f} USD".format(self._btc_usd_price))
        self._label_btc_usd_price_summary.repaint()
        self._label_btc_usd_price_details.setText("BTC price: {0:,.2f} USD".format(self._btc_usd_price))
        self._label_btc_usd_price_details.repaint()

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
            self._balances_summary_table.setItem(cell_index, 1, QTableWidgetItem("{0:,.4f}".format(self._balances_summary[exchange]['BTC'])))
            self._balances_summary_table.setItem(cell_index, 2, QTableWidgetItem("{0:,.2f}".format(self._balances_summary[exchange]['USD'])))
            self._balances_summary_table.item(cell_index, 1).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self._balances_summary_table.item(cell_index, 2).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            totals['BTC'] += self._balances_summary[exchange]['BTC']
            totals['USD'] += self._balances_summary[exchange]['USD']
            cell_index += 1

        self._balances_summary_table.setItem(cell_index, 0, QTableWidgetItem("Total"))
        self._balances_summary_table.setItem(cell_index, 1, QTableWidgetItem("{0:,.4f}".format(totals['BTC'])))
        self._balances_summary_table.setItem(cell_index, 2, QTableWidgetItem("{0:,.2f}".format(totals['USD'])))
        self._balances_summary_table.item(cell_index, 1).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
        self._balances_summary_table.item(cell_index, 2).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
        bold_font = QFont('Droid Sans', 10, QFont.Bold)
        self._balances_summary_table.item(cell_index, 0).setFont(bold_font)
        self._balances_summary_table.item(cell_index, 1).setFont(bold_font)
        self._balances_summary_table.item(cell_index, 2).setFont(bold_font)

        # Populate balances details table
        self._balances_details = self._CTMain._Crypto_Trader._balances_btc
        self._balances_details_table.setRowCount(len(self._balances_details))
        self._balances_details_table.setColumnCount(len(self._balances_summary) + 5)
        self._balances_details_table.verticalHeader().hide()
        self._balances_details_table.setHorizontalHeaderLabels(
                ['Currency Code'] +
                ordered_exchanges +
                ['Total Amount', 'Total BTC Value', 'Currency USD Price', 'Total USD Value']
            )

        row_index = 0
        for code, holdings in sorted(self._balances_details.items(), key=lambda k_v: k_v[1]['TotalBtcValue'], reverse=True):
            column_index = 0
            currency_total = 0
            self._balances_details_table.setItem(row_index, column_index, QTableWidgetItem(code))
            for exchange in ordered_exchanges:
                column_index += 1
                if exchange in holdings:
                    self._balances_details_table.setItem(row_index, column_index, QTableWidgetItem("{0:,.4f}".format(holdings[exchange]['Total'])))
                    self._balances_details_table.item(row_index, column_index).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    if holdings[exchange].get('BtcValue', 0) > 0:
                        currency_total += holdings[exchange].get('Total', 0)
            column_index += 1
            self._balances_details_table.setItem(row_index, column_index, QTableWidgetItem("{0:,.4f}".format(currency_total)))
            self._balances_details_table.item(row_index, column_index).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            column_index += 1
            self._balances_details_table.setItem(row_index, column_index, QTableWidgetItem("{0:,.8f}".format(holdings['TotalBtcValue'])))
            self._balances_details_table.item(row_index, column_index).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            column_index += 1
            self._balances_details_table.setItem(row_index, column_index, QTableWidgetItem("{0:,.4f}".format(holdings['TotalBtcValue'] * self._btc_usd_price / currency_total)))
            self._balances_details_table.item(row_index, column_index).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            column_index += 1
            self._balances_details_table.setItem(row_index, column_index, QTableWidgetItem("{0:,.2f}".format(holdings['TotalBtcValue'] * self._btc_usd_price)))
            self._balances_details_table.item(row_index, column_index).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            row_index += 1
