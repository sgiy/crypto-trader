import time

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QGridLayout, QTableWidget,
    QTableWidgetItem, QLineEdit, QLabel, QCheckBox, QHBoxLayout)

class CTViewExchangeArb(QWidget):
    def __init__(self, parent = None):
        super().__init__()
        self._parent = parent
        self._Crypto_Trader = parent._Crypto_Trader
        self._tableWidget = QTableWidget()
        self._tableWidget.setColumnCount(9)
        self._layout = QGridLayout()

        self._required_rate_of_return_inputbox = QLineEdit('0', self)
        self._required_rate_of_return_inputbox.textEdited.connect(lambda: self.check_arbs(False))
        label_return = QLabel("&Required Arbitrage Return (%):")
        label_return.setBuddy(self._required_rate_of_return_inputbox)

        self._sort_by_return = QCheckBox("Sort by return?",self)
        self._sort_by_return.setChecked(True)
        self._sort_by_return.stateChanged.connect(lambda: self.check_arbs(False))

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
        self._parent.Timer.start(1000)
        self._parent.Timer.timeout.connect(self.check_arbs)
        self.show()

    def check_arbs(self, load_markets = True):
        required_rate_of_return = 1.0
        try:
            required_rate_of_return += float(self._required_rate_of_return_inputbox.text()) / 100.0
        except:
            pass
        start_time = time.time()
        if load_markets:
            self._arbitrage_possibilities = self._Crypto_Trader.get_arbitrage_possibilities(required_rate_of_return)
        results = self._arbitrage_possibilities
        count_rows = 0
        for code_base in results:
            for code_curr in results[code_base]:
                for exchangeBid in results[code_base][code_curr]:
                    for exchangeAsk in results[code_base][code_curr]:
                        if results[code_base][code_curr][exchangeBid]['Bid'] > results[code_base][code_curr][exchangeAsk]['Ask'] * required_rate_of_return:
                            count_rows += 1

        self._tableWidget.setHorizontalHeaderLabels([
            'Base',
            'Currency',
            'Exchange1',
            'Exchange1 Bid',
            'Exchange1 Ask',
            'Exchange2',
            'Exchange2 Bid',
            'Exchange2 Ask',
            'Return'
            ])
        self._tableWidget.setRowCount(count_rows)

        row_index = 0
        for code_base in results:
            for code_curr in results[code_base]:
                for exchangeBid in results[code_base][code_curr]:
                    for exchangeAsk in results[code_base][code_curr]:
                        if results[code_base][code_curr][exchangeBid]['Bid'] > results[code_base][code_curr][exchangeAsk]['Ask'] * required_rate_of_return:
                            self._tableWidget.setItem(row_index,0, QTableWidgetItem(code_base))
                            self._tableWidget.setItem(row_index,1, QTableWidgetItem(code_curr))
                            self._tableWidget.setItem(row_index,2, QTableWidgetItem(exchangeAsk))
                            self._tableWidget.setItem(row_index,3, QTableWidgetItem('{:.8f}'.format(results[code_base][code_curr][exchangeAsk]['Bid'])))
                            self._tableWidget.setItem(row_index,4, QTableWidgetItem('{:.8f}'.format(results[code_base][code_curr][exchangeAsk]['Ask'])))
                            self._tableWidget.item(row_index,4).setBackground(self._parent.Parameters.Color['green_light'])
                            self._tableWidget.setItem(row_index,5, QTableWidgetItem(exchangeBid))
                            self._tableWidget.setItem(row_index,6, QTableWidgetItem('{:.8f}'.format(results[code_base][code_curr][exchangeBid]['Bid'])))
                            self._tableWidget.item(row_index,6).setBackground(self._parent.Parameters.Color['red_light'])
                            self._tableWidget.setItem(row_index,7, QTableWidgetItem('{:.8f}'.format(results[code_base][code_curr][exchangeBid]['Ask'])))
                            self._tableWidget.setItem(row_index,8, QTableWidgetItem('{:.2f}%'.format(100.0 * (results[code_base][code_curr][exchangeBid]['Bid'] / results[code_base][code_curr][exchangeAsk]['Ask'] - 1))))
                            row_index += 1
        if self._sort_by_return.isChecked():
            self._tableWidget.sortByColumn(8, Qt.DescendingOrder)
        self._parent.log(' Check for arbitrage possibilities took {:.4f} seconds '.format(time.time() - start_time))
