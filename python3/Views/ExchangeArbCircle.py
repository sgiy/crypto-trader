import time

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QWidget, QGridLayout, QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QCheckBox,
                             QHBoxLayout)


class CTExchangeArbCircle(QWidget):
    def __init__(self, CTMain=None):
        super().__init__()
        self._CTMain = CTMain

        self._tableWidget = QTableWidget()
        self._tableWidget.setColumnCount(11)
        self._layout = QGridLayout()

        self._required_rate_of_return_inputbox = QLineEdit('0.2', self)
        self._required_rate_of_return_inputbox.textEdited.connect(lambda: self.check_arbs(False))
        label_return = QLabel("&Required Arbitrage Return (%):")
        label_return.setBuddy(self._required_rate_of_return_inputbox)

        self._sort_by_return = QCheckBox("Sort by return?", self)
        self._sort_by_return.setChecked(True)
        self._sort_by_return.stateChanged.connect(lambda: self.check_arbs(False))

        top_layout = QHBoxLayout()
        top_layout.addWidget(label_return)
        top_layout.addWidget(self._required_rate_of_return_inputbox)
        top_layout.addWidget(self._sort_by_return)
        top_layout.addStretch(1)

        self._layout.addLayout(top_layout, 0, 0, 1, 10)
        self._layout.addWidget(self._tableWidget, 1, 0, 10, 10)

        self.setLayout(self._layout)

        self._arbitrage_possibilities = {}
        self.check_arbs()

        self._timer = QTimer(self)
        self._timer.start(5000)
        self._timer.timeout.connect(self.check_arbs)

        self.show()

    def check_arbs(self, load_markets=True):
        required_rate_of_return = 1.0
        try:
            required_rate_of_return += float(self._required_rate_of_return_inputbox.text()) / 100.0
        except:
            pass
        start_time = time.time()
        if load_markets:
            self._arbitrage_possibilities = self._CTMain._Crypto_Trader.get_arbitrage_possibilities_circle(
                required_rate_of_return
            )
        results = self._arbitrage_possibilities

        if self._sort_by_return.isChecked():
            sorted_rows_to_report = sorted(results, key=lambda kv: kv['return'], reverse=True)
        else:
            sorted_rows_to_report = results

        self._tableWidget.setHorizontalHeaderLabels([
            'Exchange',
            'Market1',
            'Action1',
            'Price1',
            'Market2',
            'Action2',
            'Price2',
            'Market3',
            'Action3',
            'Price3',
            'Return'
            ])
        self._tableWidget.setRowCount(len(results))

        row_index = 0
        for row in sorted_rows_to_report:
            self._tableWidget.setItem(row_index, 0, QTableWidgetItem(row['exchange']))
            self._tableWidget.setItem(row_index, 1, QTableWidgetItem(row['market1']['MarketSymbol']))
            self._tableWidget.setItem(row_index, 2, QTableWidgetItem(row['action1']))
            if row['action1'] == 'buy':
                price = row['market1']['BestAsk']
            else:
                price = row['market1']['BestBid']
            self._tableWidget.setItem(row_index, 3, QTableWidgetItem('{:.8f}'.format(price)))
            self._tableWidget.setItem(row_index, 4, QTableWidgetItem(row['market2']['MarketSymbol']))
            self._tableWidget.setItem(row_index, 5, QTableWidgetItem(row['action2']))
            if row['action2'] == 'buy':
                price = row['market2']['BestAsk']
            else:
                price = row['market2']['BestBid']
            self._tableWidget.setItem(row_index, 6, QTableWidgetItem('{:.8f}'.format(price)))
            self._tableWidget.setItem(row_index, 7, QTableWidgetItem(row['market3']['MarketSymbol']))
            self._tableWidget.setItem(row_index, 8, QTableWidgetItem(row['action3']))
            if row['action3'] == 'buy':
                price = row['market3']['BestAsk']
            else:
                price = row['market3']['BestBid']
            self._tableWidget.setItem(row_index, 9, QTableWidgetItem('{:.8f}'.format(price)))
            self._tableWidget.setItem(row_index, 10, QTableWidgetItem('{:.2f}%'.format(row['return'])))
            row_index += 1
        self._CTMain.log(' Check for arbitrage possibilities took {:.4f} seconds '.format(time.time() - start_time))
