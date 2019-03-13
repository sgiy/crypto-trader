import threading
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton)

from PyQt5.QtCore import Qt, QTimer

class CTRecentTradesWidget(QWidget):
    def __init__(self, CTMain, exchange, code_base, code_curr, market_symbol):
        super().__init__()
        self._CTMain = CTMain
        self.update_market(exchange, code_base, code_curr, market_symbol)

        self._table_widget = QTableWidget()
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._table_widget)
        self.setLayout(self._layout)

        self._single_shot_timer = QTimer(self)
        self._single_shot_timer.setSingleShot(True)
        self._single_shot_timer.timeout.connect(self.reload_recent_trades)

        self._timer = QTimer(self)
        self._timer.start(1500)
        self._timer.timeout.connect(self.refresh_widget)

    def update_market(self, exchange, code_base, code_curr, market_symbol):
        self._exchange = exchange
        self._code_base = code_base
        self._code_curr = code_curr
        self._market_symbol = market_symbol

    def reload_recent_trades(self):
        self._CTMain._Crypto_Trader.trader[self._exchange].update_recent_market_trades_per_market(self._market_symbol)

    def refresh_widget(self):
        t = threading.Thread(target = self.refresh)
        t.start()
        t.join(1)

    def refresh(self):
        self._CTMain._Crypto_Trader.trader[self._exchange].update_recent_market_trades_per_market(self._market_symbol)
        self._recent_trades = self._CTMain._Crypto_Trader.trader[self._exchange]._recent_market_trades.get(self._market_symbol, [])

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
                self._table_widget.setItem(row_index, 0, QTableWidgetItem("{}".format(trade['TradeTime'].strftime("%H:%M:%S"))))
                self._table_widget.setItem(row_index, 1, QTableWidgetItem("{0:,.8f}".format(trade['Price'])))
                self._table_widget.setItem(row_index, 2, QTableWidgetItem("{0:,.4f}".format(trade['Amount'])))
                self._table_widget.setItem(row_index, 3, QTableWidgetItem("{0:,.4f}".format(trade['Total'])))
                for col_index in range(4):
                    self._table_widget.item(row_index, col_index).setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
                    if trade['TradeType'] == 'Buy':
                        self._table_widget.item(row_index, col_index).setBackground(self._CTMain._Parameters.Color['green_light'])
                    else:
                        self._table_widget.item(row_index, col_index).setBackground(self._CTMain._Parameters.Color['red_light'])
                row_index += 1
