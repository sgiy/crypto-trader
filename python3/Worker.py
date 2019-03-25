from PyQt5.QtCore import QRunnable


class CTWorker(QRunnable):
    """
        Worker thread

        Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

        :param callback: The function callback to run on this worker thread.
            Supplied args and kwargs will be passed through to the runner.
        :type callback: function
        :param args: Arguments to pass to the callback function
        :param kwargs: Keywords to pass to the callback function
    """
    def __init__(self, function, *args, **kwargs):
        QRunnable.__init__(self)
        self._function = function
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._function(*self._args, **self._kwargs)
