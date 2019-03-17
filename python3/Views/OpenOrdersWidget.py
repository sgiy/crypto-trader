import threading
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton)

from PyQt5.QtCore import QTimer

class CTCancelOrderButton(QPushButton):
    def __init__(self, parent=None, orderId=None):
        super().__init__()
        self._orderId = orderId
        self._parent = parent
        self.setText("Cancel");
        self.clicked.connect(self.cancel)

    def cancel(self):
        self._parent._CTMain._Crypto_Trader.trader[self._parent._exchange].cancel_order(self._orderId)
        self._parent._single_shot_timer.start(500)

class CTOpenOrdersWidget(QWidget):
    def __init__(self, CTMain, exchange, market_symbol):
        super().__init__()
        self._CTMain = CTMain
        self.update_market(exchange, market_symbol)

        self._table_widget = QTableWidget()
        self._layout = QVBoxLayout()
        self._layout.addWidget(self._table_widget)
        self.setLayout(self._layout)

        self._single_shot_timer = QTimer(self)
        self._single_shot_timer.setSingleShot(True)
        self._single_shot_timer.timeout.connect(self.update_open_orders)

        self._timer = QTimer(self)
        self._timer.start(1000)
        self._timer.timeout.connect(self.refresh_widget)

    def update_market(self, exchange, market_symbol):
        self._exchange = exchange
        self._market_symbol = market_symbol

    def update_open_orders(self):
        self._CTMain._Crypto_Trader.trader[self._exchange].update_open_user_orders_in_market(self._market_symbol)

    def refresh_widget(self):
        t = threading.Thread(target = self.refresh)
        t.start()
        t.join(1)

    def refresh(self):
        self._open_orders = self._CTMain._Crypto_Trader.trader[self._exchange]._open_orders.get(self._market_symbol, [])

        self._table_widget.setRowCount(len(self._open_orders))
        self._table_widget.setColumnCount(7)
        self._table_widget.verticalHeader().hide()
        self._table_widget.setHorizontalHeaderLabels([
            'OrderType',
            'OpderOpenedAt',
            'Price',
            'Amount',
            'Total',
            'AmountRemaining',
            ''
        ])

        row_index = 0
        for order in self._open_orders:
            self._table_widget.setItem(row_index, 0, QTableWidgetItem("{}".format(order['OrderType'])))
            self._table_widget.setItem(row_index, 1, QTableWidgetItem("{}".format(order['OpderOpenedAt'])))
            self._table_widget.setItem(row_index, 2, QTableWidgetItem("{0:,.8f}".format(order['Price'])))
            self._table_widget.setItem(row_index, 3, QTableWidgetItem("{0:,.8f}".format(order['Amount'])))
            self._table_widget.setItem(row_index, 4, QTableWidgetItem("{0:,.8f}".format(order['Total'])))
            self._table_widget.setItem(row_index, 5, QTableWidgetItem("{0:,.8f}".format(order['AmountRemaining'])))
            self._table_widget.setCellWidget(row_index, 6, CTCancelOrderButton(self, order['OrderId']));
            row_index += 1
