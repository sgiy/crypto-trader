import sys, time
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton,
    QMenu, QAction)
from PyQt5.QtGui import QIcon


from PyQt5.QtWidgets import (QComboBox, QStyleFactory,
    QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QButtonGroup,
    QSizePolicy, QTableWidget, QTableWidgetItem)
from PyQt5.QtCore import Qt, QTimer


from PyQt5.QtWidgets import (QTextEdit)


import matplotlib
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.finance import candlestick2_ochl, candlestick_ohlc
import matplotlib.dates as dates

# Static import
from config import *

from CryptoTrader import CryptoTrader
from CryptoTraderParameters import CryptoTraderParameters

class Dropdown(QComboBox):
    def __init__(self, items_list, selected_value):
        super().__init__()
        self.addItems(items_list)
        self.setCurrentText(selected_value)

class DynamicCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def initialize_figure(self, quotes, interval):
        self.axes.cla()
        self.axes.xaxis.set_major_formatter(dates.DateFormatter('%Y-%m-%d %H:%M'))
        candlestick_ohlc(self.axes,
                        quotes,
                        width=0.0006 * interval,
                        colorup='g',
                        colordown='r',
                        alpha=0.75)
        self.draw()

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
        self.CryptoTrader = CryptoTrader({
            'API_KEYS': API_KEYS,
            'EXCHANGE_CURRENCY_RENAME_MAP': EXCHANGE_CURRENCY_RENAME_MAP,
        })
        self.Parameters = CryptoTraderParameters()

        self.initActions()

        # Do not add MenuBar for now because no useful functionality yet that
        # is not already in ToolBar, but keep stub code
        # self.initMenuBar()

        self.initToolBar()
        self.viewPair()
        self.initStatusBar()
        self.show()

    def initActions(self):
        self.Actions = {}
        self.Actions['Exit'] = QAction('Exit', self)
        self.Actions['Exit'].setShortcut('Ctrl+Q')
        self.Actions['Exit'].setStatusTip('Exit application')
        self.Actions['Exit'].triggered.connect(self.close)

        self.Actions['ViewPair'] = QAction('ViewPair', self)
        self.Actions['ViewPair'].setShortcut('Ctrl+P')
        self.Actions['ViewPair'].setStatusTip('View Crypto Pair')
        self.Actions['ViewPair'].triggered.connect(self.viewPair)

    def initMenuBar(self):
        self.MenuBar = self.menuBar()
        fileMenu = self.MenuBar.addMenu('&File')
        fileMenu.addAction(self.Actions['Exit'])

    def initToolBar(self):
        self.ToolBar = self.addToolBar('ToolBar')
        self.ToolBar.addAction(self.Actions['Exit'])
        self.ToolBar.addAction(self.Actions['ViewPair'])

    def initStatusBar(self):
        self.StatusBar = self.statusBar()
        self.StatusBar.showMessage('Ready')

    def viewPair(self):
        view = CTViewPair(self.CryptoTrader, self.Parameters)
        self.setCentralWidget(view)

class CTViewPair(QWidget):
    def __init__(self, crypto_trader, parameters):
        super().__init__()
        self.table_rows_one_direction = DISPLAY_BOOK_DEPTH
        self.crypto_trader = crypto_trader
        self.params = parameters
        self.initUI()

    def initUI(self):
        if 'Fusion' in QStyleFactory.keys():
            self.changeStyle('Fusion')

        self.timer = QTimer(self)

        self.buttons_nav_home = QPushButton('Home', self)
        self.buttons_nav_home.clicked.connect(self.draw_view_home)
        self.buttons_nav_compare = QPushButton('Compare', self)
        self.buttons_nav_compare.clicked.connect(self.draw_view_home)
        self.buttons_nav_settings = QPushButton('Settings', self)
        self.buttons_nav_settings.clicked.connect(self.draw_view_settings)

        self.nav_bar = QVBoxLayout()
        self.nav_bar.addWidget(self.buttons_nav_home)
        self.nav_bar.addWidget(self.buttons_nav_compare)
        self.nav_bar.addWidget(self.buttons_nav_settings)
        self.nav_bar.addStretch(1)

        top_level_layout = QGridLayout()
        self.view_layout = QGridLayout()
        top_level_layout.addLayout(self.nav_bar, 1, 0)
        top_level_layout.addLayout(self.view_layout, 1, 1, 1, 9)

        self.setLayout(top_level_layout)
        self.draw_view_home()

        self.show()

    def clear_view(self):
        self.timer.stop()
        def deleteItems(layout):
            if layout is not None:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                    else:
                        deleteItems(item.layout())

        deleteItems(self.view_layout)

    def view_home_refresh_dropdown_exchange_change(self, exchange, default_base = None, default_curr = None):
        self._home_view_exchange = exchange
        if default_base is None:
            default_base = self._home_view_dropdown_base_curr.currentText
        if default_curr is None:
            default_curr = self._home_view_dropdown_curr_curr.currentText
        base_codes = list(self.crypto_trader.trader[exchange]._active_markets)
        self._home_view_dropdown_base_curr.clear()
        self._home_view_dropdown_base_curr.addItems(base_codes)
        if not default_base in base_codes:
            default_base = base_codes[0]
        self._home_view_dropdown_base_curr.setCurrentText(default_base)
        self.view_home_refresh_dropdown_base_change(default_base, default_curr)

    def view_home_refresh_dropdown_base_change(self, base_curr, default_curr = None):
        self._home_view_base_curr = base_curr
        if default_curr is None:
            default_curr = self._home_view_dropdown_curr_curr.currentText
        curr_codes = list(self.crypto_trader.trader[self._home_view_exchange]._active_markets[base_curr])
        self._home_view_dropdown_curr_curr.clear()
        self._home_view_dropdown_curr_curr.addItems(curr_codes)
        if not default_curr in curr_codes:
            default_curr = curr_codes[0]
        self._home_view_dropdown_curr_curr.setCurrentText(default_curr)
        self.view_home_refresh_dropdown_curr_change(default_curr)

    def view_home_refresh_dropdown_curr_change(self, curr_curr):
        self._home_view_curr_curr = curr_curr
        self._home_view_market_name = self.crypto_trader.get_market_name(self._home_view_exchange, self._home_view_base_curr, curr_curr)
        self.tableWidget.setHorizontalHeaderLabels([
            'Price',
            'Quantity',
            curr_curr + ' sum',
            self._home_view_base_curr + ' sum'
        ])
        self.view_home_refresh_order_book()
        self.view_home_refresh_chart()


    def draw_view_home(self):
        self._home_view_exchange = HOME_VIEW_EXCHANGE
        self._home_view_base_curr = HOME_VIEW_BASE_CODE
        self._home_view_curr_curr = HOME_VIEW_CURRENCY_CODE

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(2 * self.table_rows_one_direction)
        self.tableWidget.setColumnCount(4)
        self.chart = DynamicCanvas(self, width=5, height=4, dpi=100)

        exchanges = self.crypto_trader.trader.keys()
        self._home_view_dropdown_exchange = Dropdown(exchanges, HOME_VIEW_EXCHANGE)
        self._home_view_dropdown_exchange.activated[str].connect(self.view_home_refresh_dropdown_exchange_change)

        base_codes = self.crypto_trader.trader[HOME_VIEW_EXCHANGE]._active_markets.keys()
        self._home_view_dropdown_base_curr = Dropdown(base_codes, HOME_VIEW_BASE_CODE)
        self._home_view_dropdown_base_curr.activated[str].connect(self.view_home_refresh_dropdown_base_change)

        curr_codes = self.crypto_trader.trader[HOME_VIEW_EXCHANGE]._active_markets[HOME_VIEW_BASE_CODE].keys()
        self._home_view_dropdown_curr_curr = Dropdown(curr_codes, HOME_VIEW_CURRENCY_CODE)
        self._home_view_dropdown_curr_curr.activated[str].connect(self.view_home_refresh_dropdown_curr_change)

        label_lookback = QLabel("Lookback:")
        self._chart_dropdown_lookback = Dropdown(self.params.get_chart_lookback_windows(), HOME_VIEW_CHART_LOOKBACK)
        self._chart_dropdown_lookback.currentTextChanged.connect(self.view_home_refresh_chart)
        label_interval = QLabel("Interval:")
        self._chart_dropdown_interval = Dropdown(self.params.get_chart_intervals(), HOME_VIEW_CHART_INTERVAL)
        self._chart_dropdown_interval.currentTextChanged.connect(self.view_home_refresh_chart)

        self.view_home_refresh_dropdown_exchange_change(HOME_VIEW_EXCHANGE, HOME_VIEW_BASE_CODE, HOME_VIEW_CURRENCY_CODE)

        label_base_exch = QLabel("&Echange:")
        label_base_exch.setBuddy(self._home_view_dropdown_exchange)
        label_base_curr = QLabel("&Base:")
        label_base_curr.setBuddy(self._home_view_dropdown_base_curr)
        label_curr_curr = QLabel("&Currency:")
        label_curr_curr.setBuddy(self._home_view_dropdown_curr_curr)

        topLayout = QHBoxLayout()
        topLayout.addWidget(label_base_exch)
        topLayout.addWidget(self._home_view_dropdown_exchange)
        topLayout.addWidget(label_base_curr)
        topLayout.addWidget(self._home_view_dropdown_base_curr)
        topLayout.addWidget(label_curr_curr)
        topLayout.addWidget(self._home_view_dropdown_curr_curr)
        topLayout.addStretch(1)

        self.clear_view()
        self.view_layout.addLayout(topLayout, 0, 0, 1, 3)
        self.view_layout.addWidget(self.tableWidget, 1, 0, 1, 3)
        self.view_layout.addWidget(self.chart, 1, 3, 1, 7)
        self.navi_toolbar = NavigationToolbar(self.chart, self)
        self.navi_toolbar.addSeparator()

        self.navi_toolbar.addWidget(label_lookback)
        self.navi_toolbar.addWidget(self._chart_dropdown_lookback)
        self.navi_toolbar.addWidget(label_interval)
        self.navi_toolbar.addWidget(self._chart_dropdown_interval)

        self.view_layout.addWidget(self.navi_toolbar, 0, 3, 1, 7)

        self.timer.start(1000)
        self.timer.timeout.connect(self.view_home_refresh_order_book)


    def draw_view_settings(self):
        styleComboBox = QComboBox()
        styleComboBox.addItems(QStyleFactory.keys())
        styleComboBox.activated[str].connect(self.changeStyle)

        self.clear_view()
        self.view_layout.addWidget(styleComboBox, 1, 1)

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

    def view_home_refresh_order_book(self):
        exchange = self._home_view_exchange
        code_base = self._home_view_base_curr
        code_curr = self._home_view_curr_curr
        market_name = self._home_view_market_name
        print("Loading market " + market_name)

        align_right = Qt.AlignRight

        results = self.crypto_trader.trader[exchange].load_order_book(market_name)
        for cell_index in range(2 * self.table_rows_one_direction):
            self.tableWidget.setItem(cell_index,0, QTableWidgetItem(""))
            self.tableWidget.setItem(cell_index,1, QTableWidgetItem(""))
        sum_bid = 0
        sum_bid_base = 0
        for bid in results['Bid']:
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 0, QTableWidgetItem("{0:.8f}".format(results['Bid'][bid]['Price'])))
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 1, QTableWidgetItem("{0:.8f}".format(results['Bid'][bid]['Quantity'])))
            sum_bid += results['Bid'][bid]['Quantity']
            sum_bid_base += results['Bid'][bid]['Quantity'] * results['Bid'][bid]['Price']
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 2, QTableWidgetItem("{0:.8f}".format(sum_bid)))
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 3, QTableWidgetItem("{0:.8f}".format(sum_bid_base)))
            for i in range(4):
                if bid > 0:
                    self.tableWidget.item(self.table_rows_one_direction + bid, i).setBackground(self.params.Color['green_light'])
                else:
                    self.tableWidget.item(self.table_rows_one_direction + bid, i).setBackground(self.params.Color['green_bold'])
                self.tableWidget.item(self.table_rows_one_direction + bid, i).setTextAlignment(align_right)

        sum_ask = 0
        sum_ask_base = 0
        for ask in results['Ask']:
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 0, QTableWidgetItem("{0:.8f}".format(results['Ask'][ask]['Price'])))
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 1, QTableWidgetItem("{0:.8f}".format(results['Ask'][ask]['Quantity'])))
            sum_ask += results['Ask'][ask]['Quantity']
            sum_ask_base += results['Ask'][ask]['Quantity'] * results['Ask'][ask]['Price']
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 2, QTableWidgetItem("{0:.8f}".format(sum_ask)))
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 3, QTableWidgetItem("{0:.8f}".format(sum_ask_base)))
            for i in range(4):
                if ask > 0:
                    self.tableWidget.item(self.table_rows_one_direction - 1 - ask, i).setBackground(self.params.Color['red_light'])
                else:
                    self.tableWidget.item(self.table_rows_one_direction - 1 - ask, i).setBackground(self.params.Color['red_bold'])
                self.tableWidget.item(self.table_rows_one_direction - 1 - ask, i).setTextAlignment(align_right)

    def view_home_refresh_chart(self):
        exchange = self._home_view_exchange
        code_base = self._home_view_base_curr
        code_curr = self._home_view_curr_curr
        market_name = self._home_view_market_name
        interval_name = self._chart_dropdown_interval.currentText()
        lookback_name = self._chart_dropdown_lookback.currentText()
        interval = self.params.ChartInterval[interval_name]
        lookback = self.params.ChartLookbackWindow[lookback_name]

        load_chart = self.crypto_trader.trader[exchange].load_chart_data(market_name, interval, lookback)
        self.chart.initialize_figure(load_chart, interval)

if __name__ == '__main__':
    app = QApplication([])
    win = CTMainWindow()
    sys.exit(app.exec_())
