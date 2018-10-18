import sys

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import QtGui
from PyQt5.QtCore import Qt

import pyqtgraph as pg

from Bittrex import Bittrex

bittrex = Bittrex(APIKey='', Secret='')

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Crypto Trader'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.table_rows_one_direction = 5
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        btn = QtGui.QPushButton('press me')
        btn.clicked.connect(self.test)

        self.tableWidget = QtGui.QTableWidget()
        self.tableWidget.setRowCount(2 * self.table_rows_one_direction)
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(['Price','Quantity','XRP sum','BTC sum'])
        self.test()

        plot = pg.PlotWidget()
        layout = QtGui.QGridLayout()
        self.setLayout(layout)

        layout.addWidget(btn, 0, 0)
        layout.addWidget(self.tableWidget, 1, 0)
        layout.addWidget(plot, 0, 1, 2, 1)

        self.show()

    def test(self):
        color_green = QtGui.QColor(40,167,69)
        color_red = QtGui.QColor(220,53,69)
        align_right = Qt.AlignRight

        results = bittrex.load_order_book("BTC-ETH")
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
