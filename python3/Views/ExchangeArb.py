import time

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QWidget, QGridLayout, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QCheckBox,
                             QHBoxLayout, QPushButton)

import CTColors
from Views.TwoOrderBooks import CTTwoOrderBooks


class CTSelectArbButton(QPushButton):
    def __init__(self, parent=None, row=None):
        super().__init__()
        self._row = row
        self._parent = parent
        self.setText("View")
        self.clicked.connect(self.select_arb)

    def select_arb(self):
        self._parent._selected_order_books = CTTwoOrderBooks(
            CTMain=self._parent._CTMain,
            exchange1=self._row['exchangeAsk'],
            market_symbol_1=self._row['marketAsk'],
            base_curr1=self._parent._CTMain._Crypto_Trader.trader[self._row['exchangeAsk']].get_local_code(
                self._row['code_base']
            ),
            curr_curr1=self._parent._CTMain._Crypto_Trader.trader[self._row['exchangeAsk']].get_local_code(
                self._row['code_curr']
            ),
            exchange2=self._row['exchangeBid'],
            market_symbol_2=self._row['marketBid'],
            base_curr2=self._parent._CTMain._Crypto_Trader.trader[self._row['exchangeBid']].get_local_code(
                self._row['code_base']
            ),
            curr_curr2=self._parent._CTMain._Crypto_Trader.trader[self._row['exchangeBid']].get_local_code(
                self._row['code_curr']
            ),
            depth=5
        )
        self._parent._selected_order_books.setGeometry(150, 150, 1600, 800)


class CTExchangeArb(QWidget):
    def __init__(self, CTMain=None):
        super().__init__()
        self._CTMain = CTMain

        self._tableWidget = QTableWidget()
        self._tableWidget.setColumnCount(10)
        self._layout = QGridLayout()

        self._required_rate_of_return_inputbox = QLineEdit('0.5', self)
        self._required_rate_of_return_inputbox.textEdited.connect(lambda: self.check_arbs(load_markets=False))
        label_return = QLabel("&Required Arbitrage Return (%):")
        label_return.setBuddy(self._required_rate_of_return_inputbox)

        self._sort_by_return = QCheckBox("Sort by return?", self)
        self._sort_by_return.setChecked(True)
        self._sort_by_return.stateChanged.connect(lambda: self.check_arbs(load_markets=False))

        topLayout = QHBoxLayout()
        topLayout.addWidget(label_return)
        topLayout.addWidget(self._required_rate_of_return_inputbox)
        topLayout.addWidget(self._sort_by_return)
        topLayout.addStretch(1)

        self._layout.addLayout(topLayout, 0, 0, 1, 10)
        self._layout.addWidget(self._tableWidget, 1, 0, 10, 10)

        self.setLayout(self._layout)

        self._arbitrage_possibilities = {}
        self.check_arbs()

        self._timer = QTimer(self)
        self._timer.start(5000)
        self._timer.timeout.connect(self.check_arbs)

    def check_arbs(self, load_markets=True):
        required_rate_of_return = 1.0
        try:
            required_rate_of_return += float(self._required_rate_of_return_inputbox.text()) / 100.0
        except:
            pass
        start_time = time.time()
        if load_markets:
            self._arbitrage_possibilities = self._CTMain._Crypto_Trader.get_arbitrage_possibilities(
                required_rate_of_return
            )
        results = self._arbitrage_possibilities
        rows_to_report = []

        count_rows = 0
        for code_base in results:
            for code_curr in results[code_base]:
                for exchangeBid in results[code_base][code_curr]:
                    for exchangeAsk in results[code_base][code_curr]:
                        if results[code_base][code_curr][exchangeAsk]['BestAsk'] > 0 and results[code_base][code_curr][exchangeBid]['BestBid'] > results[code_base][code_curr][exchangeAsk]['BestAsk'] * required_rate_of_return:
                            count_rows += 1
                            rows_to_report.append({
                                'code_base': code_base,
                                'code_curr': code_curr,
                                'exchangeAsk': exchangeAsk,
                                'marketAsk': results[code_base][code_curr][exchangeAsk]['MarketSymbol'],
                                'exchangeAskBid': results[code_base][code_curr][exchangeAsk]['BestBid'],
                                'exchangeAskAsk': results[code_base][code_curr][exchangeAsk]['BestAsk'],
                                'exchangeBid': exchangeBid,
                                'marketBid': results[code_base][code_curr][exchangeBid]['MarketSymbol'],
                                'exchangeBidBid': results[code_base][code_curr][exchangeBid]['BestBid'],
                                'exchangeBidAsk': results[code_base][code_curr][exchangeBid]['BestAsk'],
                                'return': 100.0 * (results[code_base][code_curr][exchangeBid]['BestBid'] / results[code_base][code_curr][exchangeAsk]['BestAsk'] - 1)
                            })

        if self._sort_by_return.isChecked():
            sorted_rows_to_report = sorted(rows_to_report, key=lambda kv: kv['return'], reverse=True)
        else:
            sorted_rows_to_report = rows_to_report

        self._tableWidget.setHorizontalHeaderLabels([
            'Base',
            'Currency',
            'Exchange1',
            'Exchange1 Bid',
            'Exchange1 Ask',
            'Exchange2',
            'Exchange2 Bid',
            'Exchange2 Ask',
            'Return',
            'View Order Books'
            ])
        self._tableWidget.setRowCount(count_rows)

        row_index = 0
        for row in sorted_rows_to_report:
            self._tableWidget.setItem(row_index, 0, QTableWidgetItem(row['code_base']))
            self._tableWidget.setItem(row_index, 1, QTableWidgetItem(row['code_curr']))
            self._tableWidget.setItem(row_index, 2, QTableWidgetItem(row['exchangeAsk']))
            self._tableWidget.setItem(row_index, 3, QTableWidgetItem('{:.8f}'.format(row['exchangeAskBid'])))
            ask_item = QTableWidgetItem('{:.8f}'.format(row['exchangeAskAsk']))
            ask_item.setBackground(CTColors.GREEN_LIGHT)
            self._tableWidget.setItem(row_index, 4, ask_item)
            self._tableWidget.setItem(row_index, 5, QTableWidgetItem(row['exchangeBid']))
            bid_item = QTableWidgetItem('{:.8f}'.format(row['exchangeBidBid']))
            bid_item.setBackground(CTColors.RED_LIGHT)
            self._tableWidget.setItem(row_index, 6, bid_item)
            self._tableWidget.setItem(row_index, 7, QTableWidgetItem('{:.8f}'.format(row['exchangeBidAsk'])))
            self._tableWidget.setItem(row_index, 8, QTableWidgetItem('{:.2f}%'.format(row['return'])))
            self._tableWidget.setCellWidget(row_index, 9, CTSelectArbButton(self, row))

            row_index += 1
        self._CTMain.log(' Check for arbitrage possibilities took {:.4f} seconds '.format(time.time() - start_time))
