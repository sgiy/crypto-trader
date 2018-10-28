import sys, time
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox, QStyleFactory,
    QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QButtonGroup,
    QMenu, QSizePolicy, QTableWidget,QTableWidgetItem)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QTimer

import matplotlib
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from matplotlib.finance import candlestick2_ochl, candlestick_ohlc
import matplotlib.dates as dates

from config import *

from CryptoTrader import CryptoTrader

import ipdb

class CryptoTraderParams:
    def __init__(self):
        self.Color = {
            'green_light':  QColor( 40, 167,  69, 127),
            'green_bold':   QColor( 40, 167,  69, 191),
            'red_light':    QColor(220,  53,  69, 127),
            'red_bold':     QColor(220,  53,  69, 191),
        }
        self.ChartLookbackWindow = {
            '1 Day':    24*60,         #translations into minutes
            '5 Days':   5*24*60,
            '1 Month':  30*24*60,
            '3 Months': 3*30*24*60
        }
        self.ChartInterval = {
            '1 Minute':     1,
            '5 Minutes':    5,
            '15 Minutes':   15,
            '30 Minutes':   30,
            '1 Hour':       60,
            '8 Hours':      8*60,
            '1 Day':        24*60
        }

    def get_chart_lookback_windows(self):
        return list(self.ChartLookbackWindow)

    def get_chart_intervals(self):
        return list(self.ChartInterval)

    def get_chart_number_of_intervals(self, lookback, interval):
        return self.ChartLookbackWindow(lookback) / self.ChartLookbackWindow(lookback)

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

    def initialize_figure(self, opens, closes, highs, lows, number_of_ticks_to_show = 12*24):
        self.axes.cla()
        candlestick2_ochl(self.axes,
                        opens[-number_of_ticks_to_show:],
                        closes[-number_of_ticks_to_show:],
                        highs[-number_of_ticks_to_show:],
                        lows[-number_of_ticks_to_show:],
                        width=0.6,
                        colorup='g',
                        colordown='r',
                        alpha=0.75)
        self.draw()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Crypto Trader'
        self.left = WINDOW_SIZE['left']
        self.top = WINDOW_SIZE['top']
        self.width = WINDOW_SIZE['width']
        self.height = WINDOW_SIZE['height']
        self.table_rows_one_direction = DISPLAY_BOOK_DEPTH
        self.crypto_trader = CryptoTrader({
            'API_KEYS': API_KEYS,
            'EXCHANGE_CURRENCY_RENAME_MAP': EXCHANGE_CURRENCY_RENAME_MAP,
        })
        self.params = CryptoTraderParams()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

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
        label_lookback = QLabel("Lookback:")
        self._chart_dropdown_lookback = Dropdown(self.params.get_chart_lookback_windows(), HOME_VIEW_CHART_LOOKBACK)
        label_interval = QLabel("Interval:")
        self._chart_dropdown_interval = Dropdown(self.params.get_chart_intervals(), HOME_VIEW_CHART_INTERVAL)

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
        load_chart = self.crypto_trader.trader[exchange].load_ticks(market_name)
        self.chart.initialize_figure(load_chart['opens'], load_chart['closes'], load_chart['highs'], load_chart['lows'])

if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    sys.exit(app.exec_())
