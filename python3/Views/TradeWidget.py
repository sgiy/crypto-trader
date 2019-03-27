from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel)


class CTTradeWidget(QWidget):
    def __init__(self, CTMain, exchange, code_base, code_curr, market_symbol=None):
        super().__init__()
        self._CTMain = CTMain

        self._exchange = exchange
        self._code_base = code_base
        self._code_curr = code_curr
        self._market_symbol = market_symbol

        self._single_shot_timer = QTimer(self)
        self._single_shot_timer.setSingleShot(True)

        self._price = QLineEdit('', self)
        self._price.textEdited[str].connect(self.recalculate_total)
        self._quantity = QLineEdit('', self)
        self._quantity.textEdited[str].connect(self.recalculate_total)
        self._base_amount = QLineEdit('', self)
        self._base_amount.textEdited[str].connect(self.recalculate_quantity)

        self._label_price = QLabel("Price:")
        self._label_quantity = QLabel("")
        self._label_base_amount = QLabel("")
        self._available_balances_base = QLabel("")
        self._available_balances_currency = QLabel("")

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
        self._layout.addWidget(self._available_balances_base)
        self._layout.addWidget(self._available_balances_currency)
        self._layout.addLayout(self._trade_buttons)

        self.setLayout(self._layout)

    def update_currencies(self, exchange, code_base, code_curr, market_symbol=None, force_update=False):
        if self._exchange != exchange or self._code_base != code_base or self._code_curr != code_curr or force_update:
            self._exchange = exchange
            self._code_base = code_base
            self._code_curr = code_curr
            self._local_base = self._CTMain._Crypto_Trader.trader[exchange].get_local_code(code_base)
            self._local_curr = self._CTMain._Crypto_Trader.trader[exchange].get_local_code(code_curr)
            if market_symbol is None:
                self._market_symbol = self._CTMain._Crypto_Trader.get_market_symbol(exchange, code_base, code_curr)
            else:
                self._market_symbol = market_symbol
            self._price.setText("")
            self._quantity.setText("")
            self._base_amount.setText("")
            self._label_quantity.setText("Quantity {}:".format(self._local_curr))
            self._label_base_amount.setText("Total {}:".format(self._local_base))
            self.update_after_trade()
            self.repaint()

    def update_available_balances(self):
        if self._exchange in self._CTMain._Crypto_Trader._SETTINGS.get('Exchanges with API Keys', []):
            self._available_balances_base.setText("Available {}: {:,.8f}".format(
                    self._local_base,
                    self._CTMain._Crypto_Trader.trader[self._exchange].get_available_balance(self._local_base, True)
                )
            )
            # Need to force reload balances only once, assuming balances are updated
            # for all currencies simultaneously
            self._available_balances_currency.setText("Available {}: {:,.8f}".format(
                    self._local_curr,
                    self._CTMain._Crypto_Trader.trader[self._exchange].get_available_balance(self._local_curr, False)
                )
            )
        else:
            self._available_balances_base.setText("Available {}: {:,.8f}".format(
                    self._local_base,
                    0
                )
            )
            self._available_balances_currency.setText("Available {}: {:,.8f}".format(
                    self._local_curr,
                    0
                )
            )

    def update_after_trade(self):
        self.update_available_balances()
        self._CTMain._Crypto_Trader.trader[self._exchange].update_open_user_orders_in_market(self._market_symbol)

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
        self.submit_trade('buy')

    def submit_sell(self):
        self.submit_trade('sell')

    def submit_trade(self, order_type):
        trade_price = float(self._price.text())
        trade_quantity = float(self._quantity.text())
        trade_base_amount = float(self._base_amount.text())
        self._CTMain._Crypto_Trader.trader[self._exchange].private_submit_new_order(
            order_type,
            self._market_symbol,
            trade_price,
            trade_quantity,
            'Limit'
        )
        print("{}ing on {} at {} {} with {} price {} quantity {} for total {} of {}".format(
            order_type,
            self._exchange,
            self._market_symbol,
            self._local_curr,
            self._local_base,
            trade_price,
            trade_quantity,
            trade_base_amount,
            self._local_base
        ))
        # Give 0.5 seconds for submitted order to propagate through the exchange
        # so that the following balances update has new values
        if not self._CTMain._Crypto_Trader.trader[self._exchange].has_implementation('ws_account_balances'):
            self._single_shot_timer.start(500)
            self._single_shot_timer.timeout.connect(self.update_after_trade)
            self.repaint()
