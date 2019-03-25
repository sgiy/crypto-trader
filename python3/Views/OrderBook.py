import time

from PyQt5.QtCore import Qt, QTimer, QThreadPool
from PyQt5.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout)

from Worker import CTWorker


class CTOrderBook(QWidget):
    def __init__(self, CTMain = None, exchange = None, market_symbol = None, base_curr = None, curr_curr = None, depth = None):
        super().__init__()
        self._CTMain = CTMain
        self._exchange = exchange
        self._market_symbol = market_symbol
        self._base_curr = base_curr
        self._curr_curr = curr_curr
        self._depth = depth

        self._order_book = {}
        self._tableWidget = QTableWidget()
        self._tableWidget.setRowCount(2 * self._depth)
        self._tableWidget.setColumnCount(4)
        self._tableWidget.verticalHeader().hide()

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._tableWidget)
        self.setLayout(self._layout)

        self._re_load_seconds = 1
        self._re_draw_seconds = 0.3
        self._thread_pool = QThreadPool()
        order_book_reloader = CTWorker(self.load_order_book_thread)
        self._thread_pool.start(order_book_reloader)

        self._timer_painter = QTimer(self)
        self._timer_painter.start(self._re_draw_seconds * 1000)
        self._timer_painter.timeout.connect(self.refresh_order_book)

    def load_order_book_thread(self):
        while True:
            if self._exchange in self._CTMain._Crypto_Trader.trader:
                if not self._CTMain._Crypto_Trader.trader[self._exchange].has_implementation('ws_order_book'):
                    self._order_book = self._CTMain._Crypto_Trader.trader[self._exchange].get_consolidated_order_book(self._market_symbol, self._depth)
            time.sleep(self._re_load_seconds)

    def refresh_order_book(self, exchange = None, market_symbol = None, base_curr = None, curr_curr = None, depth = None):
        try:
            if exchange is not None:
                self._exchange = exchange
            if market_symbol is not None:
                self._market_symbol = market_symbol
            if self._market_symbol is None:
                return

            if base_curr is not None:
                self._base_curr = base_curr
            if curr_curr is not None:
                self._curr_curr = curr_curr
            if depth is not None:
                self._depth = depth

            self._tableWidget.setHorizontalHeaderLabels([
                'Price',
                self._curr_curr + ' amount',
                self._curr_curr + ' sum',
                self._base_curr + ' sum'
            ])
            if self._CTMain._Crypto_Trader.trader[self._exchange].has_implementation('ws_order_book'):
                full_book = self._CTMain._Crypto_Trader.trader[self._exchange]._order_book.get(self._market_symbol, {})
                results = {
                    'Bid': {},
                    'Ask': {}
                }
                if 'Bids' in full_book:
                    bids = [{'Price': k, 'Quantity': full_book['Bids'][k]} for k in sorted(full_book['Bids'].keys(), reverse=True)[:5]]
                    for i in range(len(bids)):
                        results['Bid'][i] = {
                            'Price': bids[i]['Price'],
                            'Quantity': bids[i]['Quantity']
                        }
                else:
                    self._CTMain._Crypto_Trader.trader[self._exchange].ws_subscribe(self._market_symbol)
                if 'Asks' in full_book:
                    asks = [{'Price': k, 'Quantity': full_book['Asks'][k]} for k in sorted(full_book['Asks'].keys())[:5]]
                    for i in range(len(asks)):
                        results['Ask'][i] = {
                            'Price': asks[i]['Price'],
                            'Quantity': asks[i]['Quantity']
                        }
            else:
                results = self._order_book

            for cell_index in range(2 * self._depth):
                self._tableWidget.setItem(cell_index,0, QTableWidgetItem(""))
                self._tableWidget.setItem(cell_index,1, QTableWidgetItem(""))
            sum_bid = 0
            sum_bid_base = 0

            for bid in results.get('Bid', []):
                self._tableWidget.setItem(self._depth + bid, 0, QTableWidgetItem("{0:,.8f}".format(results['Bid'][bid]['Price'])))
                self._tableWidget.setItem(self._depth + bid, 1, QTableWidgetItem("{0:,.8f}".format(results['Bid'][bid]['Quantity'])))
                sum_bid += results['Bid'][bid]['Quantity']
                sum_bid_base += results['Bid'][bid]['Quantity'] * results['Bid'][bid]['Price']
                self._tableWidget.setItem(self._depth + bid, 2, QTableWidgetItem("{0:,.4f}".format(sum_bid)))
                self._tableWidget.setItem(self._depth + bid, 3, QTableWidgetItem("{0:,.4f}".format(sum_bid_base)))
                for i in range(4):
                    if bid > 0:
                        self._tableWidget.item(self._depth + bid, i).setBackground(self._CTMain._Parameters.Color['green_light'])
                    else:
                        self._tableWidget.item(self._depth + bid, i).setBackground(self._CTMain._Parameters.Color['green_bold'])
                    self._tableWidget.item(self._depth + bid, i).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)

            sum_ask = 0
            sum_ask_base = 0
            for ask in results.get('Ask', []):
                self._tableWidget.setItem(self._depth - 1 - ask, 0, QTableWidgetItem("{0:,.8f}".format(results['Ask'][ask]['Price'])))
                self._tableWidget.setItem(self._depth - 1 - ask, 1, QTableWidgetItem("{0:,.8f}".format(results['Ask'][ask]['Quantity'])))
                sum_ask += results['Ask'][ask]['Quantity']
                sum_ask_base += results['Ask'][ask]['Quantity'] * results['Ask'][ask]['Price']
                self._tableWidget.setItem(self._depth - 1 - ask, 2, QTableWidgetItem("{0:,.4f}".format(sum_ask)))
                self._tableWidget.setItem(self._depth - 1 - ask, 3, QTableWidgetItem("{0:,.4f}".format(sum_ask_base)))
                for i in range(4):
                    if ask > 0:
                        self._tableWidget.item(self._depth - 1 - ask, i).setBackground(self._CTMain._Parameters.Color['red_light'])
                    else:
                        self._tableWidget.item(self._depth - 1 - ask, i).setBackground(self._CTMain._Parameters.Color['red_bold'])
                    self._tableWidget.item(self._depth - 1 - ask, i).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
            self._CTMain.log("Loaded market " + self._market_symbol)
        except Exception as e:
            print(str(e))
