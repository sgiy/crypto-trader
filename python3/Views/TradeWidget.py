from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton)

class CTTradeWidget(QWidget):
    def __init__(self, CTMain, exchange, code_base, code_curr):
        super().__init__()
        self._CTMain = CTMain
        self._exchange = exchange
        self._code_base = code_base
        self._code_curr = code_curr
        self._local_base = CTMain._Crypto_Trader.trader[exchange].get_local_code(code_base)
        self._local_curr = CTMain._Crypto_Trader.trader[exchange].get_local_code(code_curr)
        self._market_symbol = CTMain._Crypto_Trader.trader[exchange]._active_markets[code_base][code_curr]['Market']

        self._layout = QVBoxLayout()

        self._form_layout = QFormLayout()
        self._price = QLineEdit('', self)
        self._price.textEdited[str].connect(self.recalculate_total)
        self._quantity = QLineEdit('', self)
        self._quantity.textEdited[str].connect(self.recalculate_total)
        self._amount_base = QLineEdit('', self)
        self._amount_base.textEdited[str].connect(self.recalculate_quantity)
        self._form_layout.addRow("Price:", self._price)
        self._form_layout.addRow("Quantity {}:".format(self._local_curr), self._quantity)
        self._form_layout.addRow("Total {}:".format(self._local_base), self._amount_base)

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

    def recalculate_total(self):
        if self._price.text() != '' and self._quantity.text() != '':
            self._amount_base.setText("{:.8f}".format(float(self._price.text()) * float(self._quantity.text())))

    def recalculate_quantity(self):
        if self._price.text() != '' and self._amount_base.text() != '':
            self._quantity.setText("{:.8f}".format(float(self._amount_base.text()) / float(self._price.text())))

    def submit_buy(self):
        self._trade_side = 'Buy'
        self.submit_trade()

    def submit_sell(self):
        self._trade_side = 'Sell'
        self.submit_trade()

    def submit_trade(self):
        print("{}ing on {} at {} {} with {} price {} quantity {} for total {} of {}".format(
            self._trade_side,
            self._exchange,
            self._market_symbol,
            self._local_curr,
            self._local_base,
            self._price.text(),
            self._quantity.text(),
            self._amount_base.text(),
            self._local_base
        ))
