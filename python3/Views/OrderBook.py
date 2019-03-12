import threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout)

class CTOrderBook(QWidget):
    def __init__(self, CTMain = None, exchange = None, market_symbol = None, base_curr = None, curr_curr = None, depth = None):
        super().__init__()
        self._CTMain = CTMain
        self._exchange = exchange
        self._market_symbol = market_symbol
        self._base_curr = base_curr
        self._curr_curr = curr_curr
        self._depth = depth

        self._tableWidget = QTableWidget()
        self._tableWidget.setRowCount(2 * self._depth)
        self._tableWidget.setColumnCount(4)
        self._tableWidget.verticalHeader().hide()

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._tableWidget)
        self.setLayout(self._layout)

    def load_order_book(self):
        self._order_book = self._CTMain._Crypto_Trader.trader[self._exchange].load_order_book(self._market_symbol, self._depth)

    def refresh_order_book(self, exchange = None, market_symbol = None, base_curr = None, curr_curr = None, depth = None):
        try:
            if exchange is not None:
                self._exchange = exchange
            if market_symbol is not None:
                self._market_symbol = market_symbol
            if base_curr is not None:
                self._base_curr = base_curr
            if curr_curr is not None:
                self._curr_curr = curr_curr
            if depth is not None:
                self._depth = depth

            self._tableWidget.setHorizontalHeaderLabels([
                'Price',
                'Quantity',
                self._curr_curr + ' sum',
                self._base_curr + ' sum'
            ])

            t = threading.Thread(target = self.load_order_book)
            t.start()
            t.join(1) # Keeps thread alive for only 1 second

            results = self._order_book
            for cell_index in range(2 * self._depth):
                self._tableWidget.setItem(cell_index,0, QTableWidgetItem(""))
                self._tableWidget.setItem(cell_index,1, QTableWidgetItem(""))
            sum_bid = 0
            sum_bid_base = 0

            for bid in results['Bid']:
                self._tableWidget.setItem(self._depth + bid, 0, QTableWidgetItem("{0:.8f}".format(results['Bid'][bid]['Price'])))
                self._tableWidget.setItem(self._depth + bid, 1, QTableWidgetItem("{0:.8f}".format(results['Bid'][bid]['Quantity'])))
                sum_bid += results['Bid'][bid]['Quantity']
                sum_bid_base += results['Bid'][bid]['Quantity'] * results['Bid'][bid]['Price']
                self._tableWidget.setItem(self._depth + bid, 2, QTableWidgetItem("{0:.8f}".format(sum_bid)))
                self._tableWidget.setItem(self._depth + bid, 3, QTableWidgetItem("{0:.8f}".format(sum_bid_base)))
                for i in range(4):
                    if bid > 0:
                        self._tableWidget.item(self._depth + bid, i).setBackground(self._CTMain._Parameters.Color['green_light'])
                    else:
                        self._tableWidget.item(self._depth + bid, i).setBackground(self._CTMain._Parameters.Color['green_bold'])
                    self._tableWidget.item(self._depth + bid, i).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)

            sum_ask = 0
            sum_ask_base = 0
            for ask in results['Ask']:
                self._tableWidget.setItem(self._depth - 1 - ask, 0, QTableWidgetItem("{0:.8f}".format(results['Ask'][ask]['Price'])))
                self._tableWidget.setItem(self._depth - 1 - ask, 1, QTableWidgetItem("{0:.8f}".format(results['Ask'][ask]['Quantity'])))
                sum_ask += results['Ask'][ask]['Quantity']
                sum_ask_base += results['Ask'][ask]['Quantity'] * results['Ask'][ask]['Price']
                self._tableWidget.setItem(self._depth - 1 - ask, 2, QTableWidgetItem("{0:.8f}".format(sum_ask)))
                self._tableWidget.setItem(self._depth - 1 - ask, 3, QTableWidgetItem("{0:.8f}".format(sum_ask_base)))
                for i in range(4):
                    if ask > 0:
                        self._tableWidget.item(self._depth - 1 - ask, i).setBackground(self._CTMain._Parameters.Color['red_light'])
                    else:
                        self._tableWidget.item(self._depth - 1 - ask, i).setBackground(self._CTMain._Parameters.Color['red_bold'])
                    self._tableWidget.item(self._depth - 1 - ask, i).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self._CTMain.log("Loaded market " + self._market_symbol)
        except Exception as e:
            print(str(e))
