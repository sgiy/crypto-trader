import time

from PyQt5.QtCore import Qt, QTimer, QThreadPool
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem)

from Worker import CTWorker


class CTRecentTradesWidget(QWidget):
    def __init__(self, CTMain, exchange, code_base, code_curr, market_symbol):
        super().__init__()
        self._CTMain = CTMain
        self._re_draw_seconds = 0.3
        self._re_load_seconds = 1
        self._thread_pool = QThreadPool()
        self.update_market(exchange, code_base, code_curr, market_symbol)

        self._table_widget = QTableWidget()
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._table_widget)
        self.setLayout(self._layout)

        self._timer_painter = QTimer(self)
        self._timer_painter.start(self._re_draw_seconds * 1000)
        self._timer_painter.timeout.connect(self.re_draw)

        # generic thread using signal
        trade_reloader = CTWorker(self.re_load_recent_trades_thread)
        self._thread_pool.start(trade_reloader)

    def update_market(self, exchange, code_base, code_curr, market_symbol):
        self._exchange = exchange
        self._code_base = code_base
        self._code_curr = code_curr
        self._market_symbol = market_symbol

    def re_load_recent_trades_thread(self):
        while True:
            if self._exchange in self._CTMain._Crypto_Trader.trader:
                self._CTMain._Crypto_Trader.trader[self._exchange].update_recent_market_trades_per_market(
                    self._market_symbol
                )
            time.sleep(self._re_load_seconds)

    def re_draw(self):
        if self._exchange in self._CTMain._Crypto_Trader.trader:
            self._recent_trades = self._CTMain._Crypto_Trader.trader[self._exchange]._recent_market_trades.get(
                self._market_symbol,
                []
            )
        else:
            self._recent_trades = []

        self._table_widget.setRowCount(min(10, len(self._recent_trades)))
        self._table_widget.setColumnCount(4)
        self._table_widget.verticalHeader().hide()
        self._table_widget.setHorizontalHeaderLabels([
            'TradeTime',
            'Price',
            'Amount ' + self._code_curr,
            'Total ' + self._code_base
        ])

        row_index = 0
        for trade in sorted(self._recent_trades, key=lambda k_v: k_v['TradeTime'], reverse=True):
            if row_index < 10:
                self._table_widget.setItem(row_index, 0, QTableWidgetItem("{}".format(
                    trade['TradeTime'].strftime("%H:%M:%S")
                )))
                self._table_widget.setItem(row_index, 1, QTableWidgetItem("{0:,.8f}".format(trade['Price'])))
                self._table_widget.setItem(row_index, 2, QTableWidgetItem("{0:,.4f}".format(trade['Amount'])))
                self._table_widget.setItem(row_index, 3, QTableWidgetItem("{0:,.4f}".format(trade['Total'])))
                for col_index in range(4):
                    self._table_widget.item(row_index, col_index).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if trade['TradeType'] == 'Buy':
                        self._table_widget.item(row_index, col_index).setBackground(
                            self._CTMain._Parameters.Color['green_light']
                        )
                    else:
                        self._table_widget.item(row_index, col_index).setBackground(
                            self._CTMain._Parameters.Color['red_light']
                        )
                row_index += 1
