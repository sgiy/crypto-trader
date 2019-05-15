import json
import sys
from datetime import datetime

import qtawesome as qta
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction)

from CryptoTrader import CryptoTrader
from Views.ActiveMarkets import CTActiveMarkets
from Views.Balances import CTBalances
from Views.Currencies import CTCurrencies
from Views.Debug import CTDebug
from Views.EncryptedSettings import CTEncryptedSettings
from Views.ExchangeArb import CTExchangeArb
from Views.ExchangeArbCircle import CTExchangeArbCircle
from Views.Login import CTLogin
from Views.TwentyFourHours import CTTwentyFourHours
from Views.ViewPair import CTViewPair


class CTMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load public settings
        self._settings = self.read_public_settings()

        # Declare API KEYS container
        self._API_KEYS = {}

        # Set window title and icon
        self.setWindowTitle('Crypto Trader')
        self.setWindowIcon(qta.icon('mdi.chart-line'))

        # Set initial window position
        window_position = self._settings.get('Initial Main Window Position and Size', {})
        self.setGeometry(
            window_position['left'],
            window_position['top'],
            window_position['width'],
            window_position['height']
        )

        # Load application level style sheet
        self.refresh_stylesheet()

        # Declare views
        self._views = {}
        self._selected_view = None

        # Declare Crypto Trader
        self._Crypto_Trader = None

        # Declare GUI actions through a setup dictionary using self.init_actions()
        self._actions = {}
        self._actions_setup = [
            {
                'Name': 'Balances',
                'Icon': qta.icon('mdi.credit-card-multiple'),
                'Shortcut': 'Ctrl+B',
                'StatusTip': 'Balances',
                'Connect': lambda: self.switch_view('Balances'),
            },
            {
                'Name': 'Market',
                'Icon': qta.icon('mdi.monitor-dashboard'),
                'Shortcut': 'Ctrl+M',
                'StatusTip': 'View Crypto Pair',
                'Connect': lambda: self.switch_view('ViewPair'),
            },
            {
                'Name': 'Cross Exchange Arbitrage',
                'Icon': qta.icon('mdi.arrow-collapse-vertical'),
                'StatusTip': 'View Cross Exchange Arbitrage Possibilities',
                'Connect': lambda: self.switch_view('ViewCrossExchangeArbitrage'),
            },
            {
                'Name': 'Circle Exchange Arbitrage',
                'Icon': qta.icon('mdi.sync'),
                'StatusTip': 'View Circle Exchange Arbitrage Possibilities',
                'Connect': lambda: self.switch_view('ViewCircleExchangeArbitrage'),
            },
            {
                'Name': 'Settings',
                'Icon': qta.icon('mdi.shield-key-outline'),
                'Shortcut': 'Ctrl+S',
                'StatusTip': 'Settings',
                'Connect': lambda: self.switch_view('ViewSettings'),
            },
            {
                'Name': 'Currencies',
                'StatusTip': 'View Exchange Currencies',
                'Connect': lambda: self.switch_view('ViewCurrencies'),
            },
            {
                'Name': 'Tradeable Markets',
                'StatusTip': 'View Tradeable Markets',
                'Connect': lambda: self.switch_view('ViewActiveMarkets'),
            },
            {
                'Name': '24-Hour Market Moves',
                'Icon': qta.icon('mdi.finance'),
                'StatusTip': 'View 24-Hour Market Moves',
                'Connect': lambda: self.switch_view('View24HourMoves'),
            },
            {
                'Name': 'Login',
                'Icon': qta.icon('mdi.security-account'),
                'StatusTip': 'Login',
                'Connect': lambda: self.switch_view('Login'),
            },
            {
                'Name': 'Debug',
                'StatusTip': 'Debug',
                'Connect': lambda: self.switch_view('Debug'),
            },
            {
                'Name': 'Refresh Stylesheet',
                'StatusTip': 'Refresh Stylesheet',
                'Connect': self.refresh_stylesheet,
            },
            {
                'Name': 'Exit',
                'Icon': qta.icon('mdi.door-open'),
                'Shortcut': 'Ctrl+Q',
                'StatusTip': 'Exit application',
                'Connect': self.close,
            },
        ]

        # Declare Menu/Tool/Status bars
        self._menu_bar = self.menuBar()
        self._tool_bar = self.addToolBar('ToolBar')
        self._tool_bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self._status_bar = self.statusBar()

        # Display Login view
        self.switch_view('Login')
        self.show()

    @staticmethod
    def read_public_settings():
        """
        Loading public (non-encrypted) settings file
        :return: file contents as a dictionary
        """
        try:
            with open('settings.json', 'rb') as settings_file:
                file_contents = json.loads(settings_file.read())
            return file_contents
        except FileNotFoundError:
            print('Settings file is missing')
            return {}
        except SyntaxError as e:
            print('Settings file is corrupted: {}\n{}'.format(e, e.text))
            return {}

    def refresh_stylesheet(self):
        """
        Sets application level style sheet.
        Can update style sheet while application is running.
        """
        with open('StyleSheet.css', 'r') as style_sheet_file:
            self.setStyleSheet(style_sheet_file.read())

    def init_gui(self):
        self.init_crypto_trader()

        if not self._actions:
            self.init_actions()
            self.init_menu_bar()
            self.init_tool_bar()
            self.init_status_bar()

        print('Ready')

    def init_crypto_trader(self):
        self._Crypto_Trader = CryptoTrader(
            API_KEYS=self._API_KEYS,
            SETTINGS=self._settings
        )
        print('Initialized Crypto Trader')

    def log(self, message='', message_type='INFO'):
        message = '{0} ({1}): {2}'.format(message_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message)
        self._status_bar.showMessage(message)

    def init_actions(self):
        """
        Sets up self._actions using self._actions_setup
        """
        for action in self._actions_setup:
            if 'Icon' in action:
                self._actions[action['Name']] = QAction(action['Icon'], action['Name'], self)
            else:
                self._actions[action['Name']] = QAction(action['Name'], self)
            if 'Shortcut' in action:
                self._actions[action['Name']].setShortcut(action['Shortcut'])
                self._actions[action['Name']].setStatusTip(
                    "{0} ({1})".format(
                        action['StatusTip'],
                        action['Shortcut']
                    )
                )
            else:
                self._actions[action['Name']].setStatusTip(action['StatusTip'])
            self._actions[action['Name']].triggered.connect(action['Connect'])

    def init_menu_bar(self):
        file_menu = self._menu_bar.addMenu('&File')
        file_menu.addAction(self._actions['Exit'])

        accounts_menu = self._menu_bar.addMenu('&Accounts')
        accounts_menu.addAction(self._actions['Balances'])

        arbitrage_menu = self._menu_bar.addMenu('Arbitrage Possibilities')
        arbitrage_menu.addAction(self._actions['Cross Exchange Arbitrage'])
        arbitrage_menu.addAction(self._actions['Circle Exchange Arbitrage'])

        order_book_menu = self._menu_bar.addMenu('&Market')
        order_book_menu.addAction(self._actions['24-Hour Market Moves'])
        order_book_menu.addAction(self._actions['Market'])

        settings_menu = self._menu_bar.addMenu('&Settings')
        settings_menu.addAction(self._actions['Currencies'])
        settings_menu.addAction(self._actions['Tradeable Markets'])
        settings_menu.addAction(self._actions['Debug'])
        settings_menu.addAction(self._actions['Refresh Stylesheet'])
        settings_menu.addAction(self._actions['Settings'])
        settings_menu.addAction(self._actions['Login'])

    def init_tool_bar(self):
        self._tool_bar.addAction(self._actions['Exit'])
        self._tool_bar.addAction(self._actions['Balances'])
        self._tool_bar.addAction(self._actions['24-Hour Market Moves'])
        self._tool_bar.addAction(self._actions['Market'])

    def init_status_bar(self):
        self._status_bar.showMessage('Ready')

    def switch_view(self, view_name):
        if view_name == 'ViewPair':
            self._views[view_name] = CTViewPair(CTMain=self)
        elif view_name == 'Balances':
            self._views[view_name] = CTBalances(CTMain=self)
        elif view_name == 'ViewCrossExchangeArbitrage':
            self._views[view_name] = CTExchangeArb(CTMain=self)
        elif view_name == 'ViewCircleExchangeArbitrage':
            self._views[view_name] = CTExchangeArbCircle(CTMain=self)
        elif view_name == 'Debug':
            self._views[view_name] = CTDebug(CTMain=self)
        elif view_name == 'Login':
            self._views[view_name] = CTLogin(CTMain=self)
        elif view_name == 'ViewSettings':
            self._views[view_name] = CTEncryptedSettings(CTMain=self)
        elif view_name == 'ViewCurrencies':
            self._views[view_name] = CTCurrencies(CTMain=self)
        elif view_name == 'ViewActiveMarkets':
            self._views[view_name] = CTActiveMarkets(CTMain=self)
        elif view_name == 'View24HourMoves':
            self._views[view_name] = CTTwentyFourHours(CTMain=self)
        else:
            return

        self.setCentralWidget(self._views[view_name])
        self._selected_view = view_name
        self._views[view_name].show()


if __name__ == '__main__':
    print('Initializing...')
    font = QFont("Helvetica")
    font.setPointSize(9)

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setFont(font)
    app = QApplication([])
    win = CTMainWindow()
    sys.exit(app.exec_())
