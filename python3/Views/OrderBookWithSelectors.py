from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel)

from Views.Dropdown import Dropdown
from Views.OrderBook import CTOrderBook


class CTOrderBookWithSelectors(QWidget):
    def __init__(self, CTMain=None, exchange=None, market_symbol=None, base_curr=None, curr_curr=None, depth=None):
        super().__init__()

        self._CTMain = CTMain
        self._exchange = exchange
        self._market_symbol = market_symbol
        self._base_curr = base_curr
        self._curr_curr = curr_curr
        self._depth = depth

        self._order_book = CTOrderBook(
            self._CTMain,
            self._exchange,
            self._market_symbol,
            self._base_curr,
            self._curr_curr,
            self._depth
            )

        self._layout = QVBoxLayout()

        exchanges = self._CTMain._Crypto_Trader.trader.keys()
        self._dropdown_exchange = Dropdown(exchanges, self._exchange)
        self._dropdown_exchange.activated[str].connect(self.dropdown_exchange_changed)

        base_codes = self._CTMain._Crypto_Trader.trader[self._exchange]._active_markets.keys()
        self._dropdown_base_curr = Dropdown(base_codes, self._base_curr)
        self._dropdown_base_curr.activated[str].connect(self.dropdown_base_changed)

        curr_codes = self._CTMain._Crypto_Trader.trader[self._exchange]._active_markets[self._base_curr].keys()
        self._dropdown_curr_curr = Dropdown(curr_codes, self._curr_curr)
        self._dropdown_curr_curr.activated[str].connect(self.dropdown_curr_changed)

        label_base_exch = QLabel("&Echange:")
        label_base_exch.setBuddy(self._dropdown_exchange)
        label_base_curr = QLabel("&Base:")
        label_base_curr.setBuddy(self._dropdown_base_curr)
        label_curr_curr = QLabel("&Currency:")
        label_curr_curr.setBuddy(self._dropdown_curr_curr)

        self._topLayout = QHBoxLayout()
        self._topLayout.addWidget(label_base_exch)
        self._topLayout.addWidget(self._dropdown_exchange)
        self._topLayout.addWidget(label_base_curr)
        self._topLayout.addWidget(self._dropdown_base_curr)
        self._topLayout.addWidget(label_curr_curr)
        self._topLayout.addWidget(self._dropdown_curr_curr)
        self._topLayout.addStretch(1)

        self._layout.addLayout(self._topLayout)
        self._layout.addWidget(self._order_book)
        self.setLayout(self._layout)

    def dropdown_exchange_changed(self, exchange):
        self._exchange = exchange
        base_codes = sorted(self._CTMain._Crypto_Trader.trader[self._exchange]._active_markets)
        self._dropdown_base_curr.clear()
        self._dropdown_base_curr.addItems(base_codes)
        if self._base_curr not in base_codes:
            self._base_curr = base_codes[0]
        self._dropdown_base_curr.setCurrentText(self._base_curr)
        self.dropdown_base_changed(self._base_curr)

    def dropdown_base_changed(self, base_curr):
        self._base_curr = base_curr
        curr_codes = sorted(self._CTMain._Crypto_Trader.trader[self._exchange]._active_markets[self._base_curr])
        self._dropdown_curr_curr.clear()
        self._dropdown_curr_curr.addItems(curr_codes)
        if self._curr_curr not in curr_codes:
            self._curr_curr = curr_codes[0]
        self._dropdown_curr_curr.setCurrentText(self._curr_curr)
        self.dropdown_curr_changed(self._curr_curr)

    def dropdown_curr_changed(self, curr_curr):
        self._curr_curr = curr_curr
        self._market_symbol = self._CTMain._Crypto_Trader.get_market_symbol(
            self._exchange,
            self._base_curr,
            self._curr_curr
        )
        self._order_book.refresh_order_book(
            self._exchange,
            self._market_symbol,
            self._base_curr,
            self._curr_curr,
            self._depth
        )

    def refresh_order_book(self, exchange=None, market_symbol=None, base_curr=None, curr_curr=None, depth=None):
        self._order_book.refresh_order_book(
            exchange,
            market_symbol,
            base_curr,
            curr_curr,
            depth
        )
