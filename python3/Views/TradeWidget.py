from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel)

class CTTradeWidget(QWidget):
    def __init__(self, CTMain, exchange, code_base, code_curr, market_symbol = None):
        super().__init__()
        self._CTMain = CTMain

        self._exchange = exchange
        self._code_base = code_base
        self._code_curr = code_curr
        self._market_symbol = market_symbol

        self._price = QLineEdit('', self)
        self._price.textEdited[str].connect(self.recalculate_total)
        self._quantity = QLineEdit('', self)
        self._quantity.textEdited[str].connect(self.recalculate_total)
        self._base_amount  = QLineEdit('', self)
        self._base_amount.textEdited[str].connect(self.recalculate_quantity)

        self._label_price = QLabel("Price:")
        self._label_quantity = QLabel("")
        self._label_base_amount = QLabel("")

        self.update_currencies(exchange, code_base, code_curr, market_symbol, True)

        self._layout = QVBoxLayout()

        self._form_layout = QFormLayout()
        self._form_layout.addRow(self._label_price, self._price)
        self._form_layout.addRow(self._label_quantity, self._quantity)
        self._form_layout.addRow(self._label_base_amount, self._base_amount)

        self._buy_button = QPushButton("Buy", self)
        self._buy_button.setStyleSheet("background-color: green; color: white")
        self._buy_button.clicked.connect(self.submit_buy)
        self._sell_button = QPushButton("Sell", self)
        self._sell_button.setStyleSheet("background-color: red; color: white")
        self._sell_button.clicked.connect(self.submit_sell)
        self._trade_buttons = QHBoxLayout()
        self._trade_buttons.addWidget(self._buy_button)
        self._trade_buttons.addWidget(self._sell_button)

        self._layout.addLayout(self._form_layout)
        self._layout.addLayout(self._trade_buttons)

        self.setLayout(self._layout)

    def update_currencies(self, exchange, code_base, code_curr, market_symbol = None, force_update = False):
        if self._exchange != exchange or self._code_base != code_base or self._code_curr != code_curr or force_update:
            self._exchange = exchange
            self._code_base = code_base
            self._code_curr = code_curr
            self._local_base = self._CTMain._Crypto_Trader.trader[exchange].get_local_code(code_base)
            self._local_curr = self._CTMain._Crypto_Trader.trader[exchange].get_local_code(code_curr)
            if market_symbol is None:
                self._market_symbol = self._CTMain._Crypto_Trader.get_market_name(exchange, code_base, code_curr)
            else:
                self._market_symbol = market_symbol
            self._price.setText("")
            self._quantity.setText("")
            self._base_amount.setText("")
            self._label_quantity.setText("Quantity {}:".format(self._local_curr))
            self._label_base_amount.setText("Total {}:".format(self._local_base))
            self.repaint()

    def set_price(self, price):
        self._price.setText("{:.8f}".format(price))

    def set_quantity(self, quantity):
        self._quantity.setText("{:.8f}".format(quantity))

    def set_base_amount(self, base_amount):
        self._base_amount.setText("{:.8f}".format(base_amount))

    def recalculate_total(self):
        if self._price.text() != '' and self._quantity.text() != '':
            self.set_base_amount(float(self._price.text()) * float(self._quantity.text()))

    def recalculate_quantity(self):
        if self._price.text() != '' and self._base_amount.text() != '':
            self.set_quantity(float(self._base_amount.text()) / float(self._price.text()))

    def submit_buy(self):
        self._trade_side = 'Buy'
        self.submit_trade()

    def submit_sell(self):
        self._trade_side = 'Sell'
        self.submit_trade()

    def submit_trade(self):
        trade_price = float(self._price.text())
        trade_quantity = float(self._quantity.text())
        trade_base_amount = float(self._base_amount.text())
        print("{}ing on {} at {} {} with {} price {} quantity {} for total {} of {}".format(
            self._trade_side,
            self._exchange,
            self._market_symbol,
            self._local_curr,
            self._local_base,
            trade_price,
            trade_quantity,
            trade_base_amount,
            self._local_base
        ))
