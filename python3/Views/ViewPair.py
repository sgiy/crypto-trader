from PyQt5.QtWidgets import (QWidget, QStyleFactory, QGridLayout, QLabel,
    QHBoxLayout, QApplication, QSizePolicy)

from PyQt5.QtChart import (QChart, QChartView, QCandlestickSet,
    QCandlestickSeries, QLineSeries, QDateTimeAxis, QValueAxis)
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QDateTime

from Views.Dropdown import Dropdown
from Views.OrderBook import CTOrderBook

class CTViewPair(QWidget):
    def __init__(self, CTMain = None, exchange = '', base_code = '', curr_code = '',
                    chart_lookback = '', chart_interval = '', order_book_depth = 5):
        super().__init__()
        self._CTMain = CTMain
        self._exchange = exchange
        self._base_curr = base_code
        self._curr_curr = curr_code
        self._chart_lookback = chart_lookback
        self._chart_interval = chart_interval
        self._order_book_depth = order_book_depth

        if 'Fusion' in QStyleFactory.keys():
            self.changeStyle('Fusion')

        self._layout = QGridLayout()
        self.setLayout(self._layout)

        self.draw_view()
        self.show()

    def refresh_dropdown_exchange_change(self, exchange, default_base = None, default_curr = None):
        self._exchange = exchange
        if default_base is None:
            default_base = self._dropdown_base_curr.currentText
        if default_curr is None:
            default_curr = self._dropdown_curr_curr.currentText
        base_codes = list(self._CTMain._Crypto_Trader.trader[exchange]._active_markets)
        self._dropdown_base_curr.clear()
        self._dropdown_base_curr.addItems(base_codes)
        if not default_base in base_codes:
            default_base = base_codes[0]
        self._dropdown_base_curr.setCurrentText(default_base)
        self.refresh_dropdown_base_change(default_base, default_curr)

    def refresh_dropdown_base_change(self, base_curr, default_curr = None):
        self._base_curr = base_curr
        if default_curr is None:
            default_curr = self._dropdown_curr_curr.currentText
        curr_codes = list(self._CTMain._Crypto_Trader.trader[self._exchange]._active_markets[base_curr])
        self._dropdown_curr_curr.clear()
        self._dropdown_curr_curr.addItems(curr_codes)
        if not default_curr in curr_codes:
            default_curr = curr_codes[0]
        self._dropdown_curr_curr.setCurrentText(default_curr)
        self.refresh_dropdown_curr_change(default_curr)

    def refresh_dropdown_curr_change(self, curr_curr):
        self._curr_curr = curr_curr
        self._market_name = self._CTMain._Crypto_Trader.get_market_name(self._exchange, self._base_curr, curr_curr)

        self.refresh_order_book()
        self.refresh_chart()

    def draw_view(self):
        self._order_book_widget = CTOrderBook(
            self._CTMain,
            None,
            None,
            None,
            None,
            self._order_book_depth
            )
        self.chartView = QChartView()
        self.chartView.setRenderHint(QPainter.Antialiasing)
        self.chart = self.chartView.chart()
        self.chart.legend().setVisible(False)
        self.chart.setTitle("Candlesticks")

        self.CandlestickSeries = QCandlestickSeries()
        self.CandlestickSeries.setIncreasingColor(Qt.green);
        self.CandlestickSeries.setDecreasingColor(Qt.red);

        exchanges = self._CTMain._Crypto_Trader.trader.keys()
        self._dropdown_exchange = Dropdown(exchanges, self._exchange)
        self._dropdown_exchange.activated[str].connect(self.refresh_dropdown_exchange_change)

        base_codes = self._CTMain._Crypto_Trader.trader[self._exchange]._active_markets.keys()
        self._dropdown_base_curr = Dropdown(base_codes, self._base_curr)
        self._dropdown_base_curr.activated[str].connect(self.refresh_dropdown_base_change)

        curr_codes = self._CTMain._Crypto_Trader.trader[self._exchange]._active_markets[self._base_curr].keys()
        self._dropdown_curr_curr = Dropdown(curr_codes, self._curr_curr)
        self._dropdown_curr_curr.activated[str].connect(self.refresh_dropdown_curr_change)

        label_lookback = QLabel("Lookback:")
        self._chart_dropdown_lookback = Dropdown(self._CTMain._Parameters.get_chart_lookback_windows(), self._chart_lookback)
        self._chart_dropdown_lookback.currentTextChanged.connect(self.refresh_chart)
        label_interval = QLabel("Interval:")
        self._chart_dropdown_interval = Dropdown(self._CTMain._Parameters.get_chart_intervals(), self._chart_interval)
        self._chart_dropdown_interval.currentTextChanged.connect(self.refresh_chart)

        self.refresh_dropdown_exchange_change(self._exchange, self._base_curr, self._curr_curr)

        label_base_exch = QLabel("&Echange:")
        label_base_exch.setBuddy(self._dropdown_exchange)
        label_base_curr = QLabel("&Base:")
        label_base_curr.setBuddy(self._dropdown_base_curr)
        label_curr_curr = QLabel("&Currency:")
        label_curr_curr.setBuddy(self._dropdown_curr_curr)

        topLayout = QHBoxLayout()
        topLayout.addWidget(label_base_exch)
        topLayout.addWidget(self._dropdown_exchange)
        topLayout.addWidget(label_base_curr)
        topLayout.addWidget(self._dropdown_base_curr)
        topLayout.addWidget(label_curr_curr)
        topLayout.addWidget(self._dropdown_curr_curr)
        topLayout.addStretch(1)

        self._layout.addLayout(topLayout, 0, 0, 1, 3)
        self._layout.addWidget(self._order_book_widget, 1, 0, 1, 3)
        self._layout.addWidget(self.chartView, 1, 3, 1, 7)

        self._CTMain._Timer.start(1000)
        self._CTMain._Timer.timeout.connect(self.refresh_order_book)
        self.show()

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

    def refresh_order_book(self):
        self._order_book_widget.refresh_order_book(
            self._exchange,
            self._market_name,
            self._base_curr,
            self._curr_curr
            )

    def refresh_chart(self):
        exchange = self._exchange
        code_base = self._base_curr
        code_curr = self._curr_curr
        market_name = self._market_name
        interval_name = self._chart_dropdown_interval.currentText()
        lookback_name = self._chart_dropdown_lookback.currentText()
        interval = self._CTMain._Parameters.ChartInterval[interval_name]
        lookback = self._CTMain._Parameters.ChartLookbackWindow[lookback_name]

        load_chart = self._CTMain._Crypto_Trader.trader[exchange].load_chart_data(market_name, interval, lookback)

        ch_max = load_chart[0][2]
        ch_min = load_chart[0][3]
        for point in load_chart:
            candle = QCandlestickSet(point[1],point[2],point[3],point[4], point[0])
            ch_max = max(ch_max, point[2])
            ch_min = min(ch_min, point[3])
            self.CandlestickSeries.append(candle)

        self.chart.addSeries(self.CandlestickSeries)
        axisX = QDateTimeAxis()
        axisX.setFormat("dd-MM-yyyy h:mm")
        self.chart.setAxisX(axisX, self.CandlestickSeries)

        axisY = QValueAxis()
        axisY.setRange(max(0, ch_min - 0.1 * (ch_max - ch_min)), ch_max + 0.1 * (ch_max - ch_min))
        self.chart.setAxisY(axisY, self.CandlestickSeries)

        # self.chart.initialize_figure(load_chart, interval)
