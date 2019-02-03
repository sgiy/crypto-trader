import sys, os
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction)
from PyQt5.QtCore import QTimer

# Static import
from config import *
try:
    from config_private import *
except:
    pass

from CryptoTrader import CryptoTrader
from CryptoTraderParameters import CryptoTraderParameters

from Views.Login import CTLogin
from Views.Dropdown import Dropdown
from Views.ExchangeArb import CTExchangeArb
from Views.ExchangeArbCircle import CTExchangeArbCircle
from Views.OrderBook import CTOrderBook
from Views.TwoOrderBooks import CTTwoOrderBooks
from Views.ViewPair import CTViewPair
from Views.Debug import CTDebug
from Views.Balances import CTBalances
from Views.Currencies import CTCurrencies

class CTMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Crypto Trader')
        self.setGeometry(
            WINDOW_SIZE['left'],
            WINDOW_SIZE['top'],
            WINDOW_SIZE['width'],
            WINDOW_SIZE['height']
        )
        self._Crypto_Trader = CryptoTrader({
            'API_KEYS': API_KEYS,
            'EXCHANGE_CURRENCY_RENAME_MAP': EXCHANGE_CURRENCY_RENAME_MAP,
            'EXCHANGES_TO_LOAD': EXCHANGES_TO_LOAD
        })
        print('Initialized Exchanges')
        self._Parameters = CryptoTraderParameters()
        self.Views = {}
        self._Timer = QTimer(self)

        self.initActions()

        self.initMenuBar()
        self.initToolBar()
        self.initStatusBar()
        self.switch_view('Debug')
        self.refresh_stylesheet()
        self.show()
        print('Ready')

    def log(self, message = '', message_type = 'INFO'):
        message = '{0} ({1}): {2}'.format(message_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        self.StatusBar.showMessage(message)

    def initActions(self):
        self.Actions = {}
        self.Actions['Exit'] = QAction('Exit', self)
        self.Actions['Exit'].setShortcut('Ctrl+Q')
        self.Actions['Exit'].setStatusTip('Exit application (Ctrl+Q)')
        self.Actions['Exit'].triggered.connect(self.close)

        self.Actions['Balances'] = QAction('Balances', self)
        self.Actions['Balances'].setStatusTip('Balances')
        self.Actions['Balances'].triggered.connect(lambda: self.switch_view('Balances'))

        self.Actions['ViewPair'] = QAction('ViewPair', self)
        self.Actions['ViewPair'].setShortcut('Ctrl+P')
        self.Actions['ViewPair'].setStatusTip('View Crypto Pair (Ctrl+P)')
        self.Actions['ViewPair'].triggered.connect(lambda: self.switch_view('ViewPair'))

        self.Actions['ExchangeArbitrage'] = QAction('ExchangeArbitrage', self)
        self.Actions['ExchangeArbitrage'].setShortcut('Ctrl+E')
        self.Actions['ExchangeArbitrage'].setStatusTip('View Current Exchange Arbitrage Possibilities (Ctrl+E)')
        self.Actions['ExchangeArbitrage'].triggered.connect(lambda: self.switch_view('ExchangeArbitrage'))

        self.Actions['ExchangeArbitrageCircle'] = QAction('ExchangeArbitrageCircle', self)
        self.Actions['ExchangeArbitrageCircle'].setStatusTip('View Current Exchange Arbitrage Circle Possibilities')
        self.Actions['ExchangeArbitrageCircle'].triggered.connect(lambda: self.switch_view('ExchangeArbitrageCircle'))

        self.Actions['ViewTwoExchangeOrderBooks'] = QAction('ViewTwoExchangeOrderBooks', self)
        self.Actions['ViewTwoExchangeOrderBooks'].setStatusTip('View Two Exchange Order Books')
        self.Actions['ViewTwoExchangeOrderBooks'].triggered.connect(lambda: self.switch_view('ViewTwoExchangeOrderBooks'))

        self.Actions['Debug'] = QAction('Debug', self)
        self.Actions['Debug'].setStatusTip('Debug')
        self.Actions['Debug'].triggered.connect(lambda: self.switch_view('Debug'))

        self.Actions['ViewSettings'] = QAction('Settings', self)
        self.Actions['ViewSettings'].setStatusTip('Settings')
        self.Actions['ViewSettings'].triggered.connect(lambda: self.switch_view('ViewSettings'))

        self.Actions['Currencies'] = QAction('Currencies', self)
        self.Actions['Currencies'].setStatusTip('Currencies')
        self.Actions['Currencies'].triggered.connect(lambda: self.switch_view('Currencies'))

        self.Actions['RefreshStylesheet'] = QAction('RefreshStylesheet', self)
        self.Actions['RefreshStylesheet'].setStatusTip('Refresh Stylesheet')
        self.Actions['RefreshStylesheet'].triggered.connect(self.refresh_stylesheet)

    def initMenuBar(self):
        self.MenuBar = self.menuBar()
        file_menu = self.MenuBar.addMenu('&File')
        file_menu.addAction(self.Actions['Exit'])
        settings_menu = self.MenuBar.addMenu('&Settings')
        settings_menu.addAction(self.Actions['Currencies'])

    def initToolBar(self):
        self.ToolBar = self.addToolBar('ToolBar')
        self.ToolBar.addAction(self.Actions['Exit'])
        self.ToolBar.addAction(self.Actions['Balances'])
        self.ToolBar.addAction(self.Actions['ViewPair'])
        self.ToolBar.addAction(self.Actions['ExchangeArbitrage'])
        self.ToolBar.addAction(self.Actions['ExchangeArbitrageCircle'])
        self.ToolBar.addAction(self.Actions['ViewTwoExchangeOrderBooks'])
        self.ToolBar.addAction(self.Actions['Debug'])
        self.ToolBar.addAction(self.Actions['ViewSettings'])
        self.ToolBar.addAction(self.Actions['RefreshStylesheet'])

    def initStatusBar(self):
        self.StatusBar = self.statusBar()
        self.StatusBar.showMessage('Ready')

    def refresh_stylesheet(self):
        css = open(os.path.join(sys.path[0], "StyleSheet.css"), "r")
        self.setStyleSheet(css.read())

    def switch_view(self, view_name):
        self._Timer.stop()
        # if view_name not in self.Views:
        if view_name == 'ViewPair':
            self.Views['ViewPair'] = CTViewPair(
                CTMain = self,
                exchange = HOME_VIEW_EXCHANGE,
                base_code = HOME_VIEW_BASE_CODE,
                curr_code = HOME_VIEW_CURRENCY_CODE,
                chart_lookback = HOME_VIEW_CHART_LOOKBACK,
                chart_interval = HOME_VIEW_CHART_INTERVAL,
                order_book_depth = DISPLAY_BOOK_DEPTH
                )
        if view_name == 'Balances':
            self.Views['Balances'] = CTBalances(CTMain = self)
        if view_name == 'ExchangeArbitrage':
            self.Views['ExchangeArbitrage'] = CTExchangeArb(CTMain = self)
        if view_name == 'ExchangeArbitrageCircle':
            self.Views['ExchangeArbitrageCircle'] = CTExchangeArbCircle(CTMain = self)
        if view_name == 'ViewTwoExchangeOrderBooks':
            self.Views['ViewTwoExchangeOrderBooks'] = CTTwoOrderBooks(
                CTMain = self,
                exchange1 = 'Bittrex',
                market_name1 = 'BTC-XLM',
                base_curr1 = 'BTC',
                curr_curr1 = 'XLM',
                exchange2 = 'Poloniex',
                market_name2 = 'BTC_STR',
                base_curr2 = 'BTC',
                curr_curr2 = 'STR',
                depth = 5
                )
        if view_name == 'Debug':
            self.Views['Debug'] = CTDebug(CTMain = self)
        if view_name == 'ViewSettings':
            self.Views['ViewSettings'] = CTLogin(CTMain = self)
        if view_name == 'Currencies':
            self.Views['Currencies'] = CTCurrencies(CTMain = self)
        self.setCentralWidget(self.Views[view_name])

if __name__ == '__main__':
    print('Starting...')
    app = QApplication([])
    win = CTMainWindow()
    sys.exit(app.exec_())
