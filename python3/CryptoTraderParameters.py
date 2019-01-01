from PyQt5.QtGui import QColor

class CryptoTraderParameters:
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
