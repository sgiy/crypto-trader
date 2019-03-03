import sys, os, json
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction)

import qtawesome as qta

from CryptoTrader import CryptoTrader
from CryptoTraderParameters import CryptoTraderParameters

from Views.Login import CTLogin
from Views.EncryptedSettings import CTEncryptedSettings
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

        self.setWindowTitle('Crypto Trader')
        self._Timer = QTimer(self)
        self.Views = {}
        with open(os.path.join(sys.path[0], 'settings'), 'rb') as myfile:
            msg=myfile.read()
        self._settings = eval(msg)
        self._selected_view = None
        self.refresh_stylesheet()
        self.switch_view('Login')
        self.setGeometry(
            300,
            300,
            1200,
            480
        )
        self.show()

    def initUI(self):
        self.setGeometry(
            self._settings['Initial Main Window Position and Size']['left'],
            self._settings['Initial Main Window Position and Size']['top'],
            self._settings['Initial Main Window Position and Size']['width'],
            self._settings['Initial Main Window Position and Size']['height']
        )
        self.initCryptoTrader()
        self._Parameters = CryptoTraderParameters()

        self.initActions()
        self.initMenuBar()
        self.initToolBar()
        self.initStatusBar()

        print('Ready')

    def initCryptoTrader(self):
        self._Crypto_Trader = CryptoTrader(
            API_KEYS = self._API_KEYS,
            SETTINGS = self._settings
        )
        print('Initialized Exchanges')

    def log(self, message = '', message_type = 'INFO'):
        message = '{0} ({1}): {2}'.format(message_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        self.StatusBar.showMessage(message)

    def initActions(self):
        self.Actions = {}

        self._actions_setup = {
            'Balances': {
                        'Icon': qta.icon('mdi.credit-card-multiple'),
                        'Shortcut': 'Ctrl+B',
                        'StatusTip': 'Balances',
                        'Connect': lambda: self.switch_view('Balances'),
                },
            'Market': {
                        'Icon': qta.icon('mdi.finance'),
                        'Shortcut': 'Ctrl+M',
                        'StatusTip': 'View Crypto Pair',
                        'Connect': lambda: self.switch_view('ViewPair'),
                },
            # 'View Two Exchange Order Books': {
            #             'StatusTip': 'View Two Exchange Order Books',
            #             'Connect': lambda: self.switch_view('ViewTwoExchangeOrderBooks'),
            #     },
            'Cross Exchange Arbitrage': {
                        'Icon': qta.icon('mdi.arrow-collapse-vertical'),
                        'StatusTip': 'View Cross Exchange Arbitrage Possibilities',
                        'Connect': lambda: self.switch_view('ViewCrossExchangeArbitrage'),
                },
            'Circle Exchange Arbitrage': {
                        'Icon': qta.icon('mdi.sync'),
                        'StatusTip': 'View Circle Exchange Arbitrage Possibilities',
                        'Connect': lambda: self.switch_view('ViewCircleExchangeArbitrage'),
                },
            'Settings': {
                        'Icon': qta.icon('mdi.shield-key-outline'),
                        'Shortcut': 'Ctrl+S',
                        'StatusTip': 'Settings',
                        'Connect': lambda: self.switch_view('ViewSettings'),
                },
            'Currencies': {
                        'StatusTip': 'View Exchange Currencies',
                        'Connect': lambda: self.switch_view('ViewCurrencies'),
                },
            'Debug': {
                        'StatusTip': 'Debug',
                        'Connect': lambda: self.switch_view('Debug'),
                },
            'Refresh Stylesheet': {
                        'StatusTip': 'Refresh Stylesheet',
                        'Connect': self.refresh_stylesheet,
                },
            'Exit': {
                        'Icon': qta.icon('mdi.door-open'),
                        'Shortcut': 'Ctrl+Q',
                        'StatusTip': 'Exit application',
                        'Connect': self.close,
                },
        }

        for action in self._actions_setup:
            if 'Icon' in self._actions_setup[action]:
                self.Actions[action] = QAction(self._actions_setup[action]['Icon'], action, self)
            else:
                self.Actions[action] = QAction(action, self)
            if 'Shortcut' in self._actions_setup[action]:
                self.Actions[action].setShortcut(self._actions_setup[action]['Shortcut'])
                self.Actions[action].setStatusTip("{0} ({1})".format(self._actions_setup[action]['StatusTip'],self._actions_setup[action]['Shortcut']))
            else:
                self.Actions[action].setStatusTip(self._actions_setup[action]['StatusTip'])
            self.Actions[action].triggered.connect(self._actions_setup[action]['Connect'])

    def initMenuBar(self):
        self.MenuBar = self.menuBar()
        file_menu = self.MenuBar.addMenu('&File')
        file_menu.addAction(self.Actions['Exit'])

        accounts_menu = self.MenuBar.addMenu('&Accounts')
        accounts_menu.addAction(self.Actions['Balances'])

        arbitrage_menu = self.MenuBar.addMenu('Arbitrage Possibilities')
        arbitrage_menu.addAction(self.Actions['Cross Exchange Arbitrage'])
        arbitrage_menu.addAction(self.Actions['Circle Exchange Arbitrage'])

        order_book_menu = self.MenuBar.addMenu('&Order Books')
        order_book_menu.addAction(self.Actions['Market'])
        # order_book_menu.addAction(self.Actions['View Two Exchange Order Books'])

        settings_menu = self.MenuBar.addMenu('&Settings')
        settings_menu.addAction(self.Actions['Currencies'])
        settings_menu.addAction(self.Actions['Debug'])
        settings_menu.addAction(self.Actions['Refresh Stylesheet'])
        settings_menu.addAction(self.Actions['Settings'])

    def initToolBar(self):
        self.ToolBar = self.addToolBar('ToolBar')
        self.ToolBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.ToolBar.addAction(self.Actions['Exit'])
        self.ToolBar.addAction(self.Actions['Balances'])
        self.ToolBar.addAction(self.Actions['Market'])

    def initStatusBar(self):
        self.StatusBar = self.statusBar()
        self.StatusBar.showMessage('Ready')

    def refresh_stylesheet(self):
        css = open(os.path.join(sys.path[0], "StyleSheet.css"), "r")
        self.setStyleSheet(css.read())

    def switch_view(self, view_name):
        self._Timer.stop()
        if view_name == 'ViewPair':
            self.Views['ViewPair'] = CTViewPair(
                CTMain = self,
                exchange = self._settings['Initial Market View Exchange'],
                base_code = self._settings['Initial Market View Base Currency'],
                curr_code = self._settings['Initial Market View Quote Currency'],
                chart_lookback = self._settings['Initial Market View Chart Lookback'],
                chart_interval = self._settings['Initial Market View Chart Interval'],
                order_book_depth = self._settings['Default Order Book Depth']
            )
        if view_name == 'Balances':
            self.Views['Balances'] = CTBalances(CTMain = self)
        if view_name == 'ViewCrossExchangeArbitrage':
            self.Views['ViewCrossExchangeArbitrage'] = CTExchangeArb(CTMain = self)
        if view_name == 'ViewCircleExchangeArbitrage':
            self.Views['ViewCircleExchangeArbitrage'] = CTExchangeArbCircle(CTMain = self)
        # if view_name == 'ViewTwoExchangeOrderBooks':
        #     self.Views['ViewTwoExchangeOrderBooks'] = CTTwoOrderBooks(
        #         CTMain = self,
        #         exchange1 = 'Bittrex',
        #         market_name1 = 'BTC-XLM',
        #         base_curr1 = 'BTC',
        #         curr_curr1 = 'XLM',
        #         exchange2 = 'Poloniex',
        #         market_name2 = 'BTC_STR',
        #         base_curr2 = 'BTC',
        #         curr_curr2 = 'STR',
        #         depth = 5
        #         )
        if view_name == 'Debug':
            self.Views['Debug'] = CTDebug(CTMain = self)
        if view_name == 'Login':
            self.Views['Login'] = CTLogin(CTMain = self)
        if view_name == 'ViewSettings':
            self.Views['ViewSettings'] = CTEncryptedSettings(CTMain = self)
        if view_name == 'ViewCurrencies':
            self.Views['ViewCurrencies'] = CTCurrencies(CTMain = self)
        self.setCentralWidget(self.Views[view_name])
        self._selected_view = view_name
        self.Views[view_name].show()

if __name__ == '__main__':
    print('Starting...')
    app = QApplication([])
    win = CTMainWindow()
    sys.exit(app.exec_())
