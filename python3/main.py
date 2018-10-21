import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QComboBox, QStyleFactory,
    QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QButtonGroup)
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer

import pyqtgraph as pg

from config import *

from CryptoTrader import CryptoTrader

import ipdb

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
        top_level_layout.addLayout(self.view_layout, 1, 1, 1, 4)

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

    def view_home_refresh_dropdown_base_change(self, base_curr, default_selection = None):
        if default_selection is None:
            default_selection = self._home_view_dropdown_curr_curr.currentText
        self._home_view_dropdown_curr_curr.clear()
        curr_codes = self.crypto_trader.trader[self._home_view_exchange]._active_markets[base_curr].keys()
        self._home_view_dropdown_curr_curr.addItems(curr_codes)
        index = self._home_view_dropdown_curr_curr.findText(default_selection, Qt.MatchFixedString)
        if index >= 0:
            self._home_view_dropdown_curr_curr.setCurrentIndex(index)
        self._home_view_base_curr = base_curr

    def view_home_refresh_dropdown_curr_change(self, curr_curr):
        self._home_view_curr_curr = curr_curr
        self.tableWidget.setHorizontalHeaderLabels([
            'Price',
            'Quantity',
            curr_curr + ' sum',
            self._home_view_base_curr + ' sum'
        ])
        self.view_home_refresh_order_book()

    def draw_view_home(self):
        self._home_view_dropdown_base_curr = QComboBox()
        self._home_view_dropdown_curr_curr = QComboBox()

        self._home_view_exchange = HOME_VIEW_EXCHANGE
        base_codes = self.crypto_trader.trader[self._home_view_exchange]._active_markets.keys()
        self.view_home_refresh_dropdown_base_change(HOME_VIEW_BASE_CODE, HOME_VIEW_CURRENCY_CODE)

        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setRowCount(2 * self.table_rows_one_direction)
        self.tableWidget.setColumnCount(4)
        self.view_home_refresh_dropdown_curr_change(HOME_VIEW_CURRENCY_CODE)

        self._home_view_dropdown_base_curr.addItems(base_codes)
        index = self._home_view_dropdown_base_curr.findText(HOME_VIEW_BASE_CODE, Qt.MatchFixedString)
        if index >= 0:
            self._home_view_dropdown_base_curr.setCurrentIndex(index)
        self._home_view_dropdown_base_curr.activated[str].connect(self.view_home_refresh_dropdown_base_change)

        label_base_curr = QLabel("&Base:")
        label_base_curr.setBuddy(self._home_view_dropdown_base_curr)

        self._home_view_dropdown_curr_curr.activated[str].connect(self.view_home_refresh_dropdown_curr_change)

        label_curr_curr = QLabel("&Currency:")
        label_curr_curr.setBuddy(self._home_view_dropdown_curr_curr)

        topLayout = QHBoxLayout()
        topLayout.addWidget(label_base_curr)
        topLayout.addWidget(self._home_view_dropdown_base_curr)
        topLayout.addWidget(label_curr_curr)
        topLayout.addWidget(self._home_view_dropdown_curr_curr)
        topLayout.addStretch(1)

        plot = pg.PlotWidget()

        self.clear_view()
        self.view_layout.addLayout(topLayout, 0, 0, 1, 2)
        self.view_layout.addWidget(self.tableWidget, 2, 0)
        self.view_layout.addWidget(plot, 2, 1)

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
        market_name = self.crypto_trader.get_market_name(exchange, code_base, code_curr)
        print("Loading market " + market_name)

        color_green = QtGui.QColor(40,167,69)
        color_red = QtGui.QColor(220,53,69)
        align_right = Qt.AlignRight

        results = self.crypto_trader.trader[exchange].load_order_book(market_name)
        for cell_index in range(2 * self.table_rows_one_direction):
            self.tableWidget.setItem(cell_index,0, QtGui.QTableWidgetItem(""))
            self.tableWidget.setItem(cell_index,1, QtGui.QTableWidgetItem(""))
        sum_bid = 0
        sum_bid_base = 0
        for bid in results['Bid']:
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 0, QtGui.QTableWidgetItem("{0:.8f}".format(results['Bid'][bid]['Price'])))
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 1, QtGui.QTableWidgetItem("{0:.8f}".format(results['Bid'][bid]['Quantity'])))
            sum_bid += results['Bid'][bid]['Quantity']
            sum_bid_base += results['Bid'][bid]['Quantity'] * results['Bid'][bid]['Price']
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 2, QtGui.QTableWidgetItem("{0:.8f}".format(sum_bid)))
            self.tableWidget.setItem(self.table_rows_one_direction + bid, 3, QtGui.QTableWidgetItem("{0:.8f}".format(sum_bid_base)))
            for i in range(4):
                self.tableWidget.item(self.table_rows_one_direction + bid, i).setBackground(color_green)
                self.tableWidget.item(self.table_rows_one_direction + bid, i).setTextAlignment(align_right)

        sum_ask = 0
        sum_ask_base = 0
        for ask in results['Ask']:
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 0, QtGui.QTableWidgetItem("{0:.8f}".format(results['Ask'][ask]['Price'])))
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 1, QtGui.QTableWidgetItem("{0:.8f}".format(results['Ask'][ask]['Quantity'])))
            sum_ask += results['Ask'][ask]['Quantity']
            sum_ask_base += results['Ask'][ask]['Quantity'] * results['Ask'][ask]['Price']
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 2, QtGui.QTableWidgetItem("{0:.8f}".format(sum_ask)))
            self.tableWidget.setItem(self.table_rows_one_direction - 1 - ask, 3, QtGui.QTableWidgetItem("{0:.8f}".format(sum_ask_base)))
            for i in range(4):
                self.tableWidget.item(self.table_rows_one_direction - 1 - ask, i).setBackground(color_red)
                self.tableWidget.item(self.table_rows_one_direction - 1 - ask, i).setTextAlignment(align_right)

if __name__ == '__main__':
    app = QApplication([])
    ex = App()
    sys.exit(app.exec_())
