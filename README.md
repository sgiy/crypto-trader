# crypto-trader

The goal of this project is to create an open, usable interface to monitor cryptocurrency moves, personal balances, and execute trades on multiple exchanges. This requires user to create API keys for each of the exchange and input them in program's configuration. The code has to be open to make sure that the key and the secret are used only in the manner specified by the relevant exchange and are not distributed.

It is recommended that the exchange API keys are created only with access to trading capabilities, but are not allowed to withdraw currency in order to limit user's exposure. Additionally, some exchanges allow specifying that the given API key can be used only from the specified IP address. This provides additional protection to the user.

Need to install
    PyQt5
    pyqtgraph
    traceback
    packages.
    * If you use Anaconda, PyQt5 comes preinstalled, so you only need to execute
        conda install pyqtgraph
