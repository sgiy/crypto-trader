from PyQt5.QtWidgets import (QWidget, QHBoxLayout)

from Views.OrderBookWithSelectors import CTOrderBookWithSelectors


class CTTwoOrderBooks(QWidget):
    def __init__(self, CTMain=None, exchange1=None, market_symbol_1=None, base_curr1=None, curr_curr1=None,
                 exchange2=None, market_symbol_2=None, base_curr2=None, curr_curr2=None, depth=None):
        super().__init__()

        self._CTMain = CTMain
        self._exchange1 = exchange1
        self._market_symbol_1 = market_symbol_1
        self._base_curr1 = base_curr1
        self._curr_curr1 = curr_curr1
        self._exchange2 = exchange2
        self._market_symbol_2 = market_symbol_2
        self._base_curr2 = base_curr2
        self._curr_curr2 = curr_curr2
        self._depth = depth

        self._order_book1 = CTOrderBookWithSelectors(
            self._CTMain,
            self._exchange1,
            self._market_symbol_1,
            self._base_curr1,
            self._curr_curr1,
            self._depth
            )
        self._order_book2 = CTOrderBookWithSelectors(
            self._CTMain,
            self._exchange2,
            self._market_symbol_2,
            self._base_curr2,
            self._curr_curr2,
            self._depth
            )

        self._layout = QHBoxLayout()
        self._layout.addWidget(self._order_book1)
        self._layout.addWidget(self._order_book2)
        self.setLayout(self._layout)

        self.refresh_order_books()
        self._CTMain._Timer.start(1000)
        self._CTMain._Timer.timeout.connect(self.refresh_order_books)

        self.show()

    def refresh_order_books(self):
        self._order_book1.refresh_order_book()
        self._order_book2.refresh_order_book()
