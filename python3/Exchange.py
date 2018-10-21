# Abstract Exchange class. Each exchange implementation should inherit from it.
import traceback

class Exchange:
    def __init__(self, APIKey='', Secret=''):
        self.APIKey = APIKey
        self.Secret = Secret
        self.BASE_URL = ''
        self._currencies = {}
        self._map_currency_code_to_exchange_code = {}
        self._map_exchange_code_to_currency_code = {}
        self._markets = {}
        self._active_markets = {}
        self._market_prices = {}
        self._available_balances = {}
        self._complete_balances_btc = {}

    def raise_not_implemented_error(self):
        raise NotImplementedError("Class " + self.__class__.__name__ + " needs to implement method " + traceback.extract_stack(None, 2)[0][2] + "!!! ")

    def print_exception(self, message=''):
        print(self.__class__.__name__ + " has an exception in method " + traceback.extract_stack(None, 2)[0][2] + "!!! " + message)

    def load_currencies(self):
        """
            Needs to update self._currencies with a map from exchange currency code to a map having Name and Enabled keys.
            Example:
                {
                    'BTC': {
                                'Name': 'Bitcoin',
                                'Enabled': 1
                            },
                    ...
                }
        """
        self.raise_not_implemented_error()

    def get_global_code(self, local_code):
        return self._map_exchange_code_to_currency_code.get(local_code, None)

    def update_market(self, market_symbol, local_base, local_curr, best_bid, best_ask, is_active = True, qty_bid = None, qty_ask = None):
        code_base = self.get_global_code(local_base)
        code_curr = self.get_global_code(local_curr)

        if not code_base in self._markets:
                self._markets[code_base] = {}

        market = {
            'Market': market_symbol,
            'Bid': best_bid,
            'Ask': best_ask,
        }
        if qty_bid is not None:
            market['QtyBid'] = qty_bid
            market['QtyAsk'] = qty_ask
        self._markets[code_base][code_curr] = market

        if is_active:
            if not code_base in self._active_markets:
                self._active_markets[code_base] = {}
            self._active_markets[code_base][code_curr] = market

    def load_markets(self):
        """
            Needs to update self._markets and self._active_markets with a map of maps from global base currency code to a global curr currency code that results in  map having Name and Enabled keys.
            Example:
                {
                    'BTC': {
                                'Name': 'Bitcoin',
                                'Enabled': 1
                            },
                    ...
                }
        """
        self.raise_not_implemented_error()

    def load_available_balances(self):
        """
            Returns a map by currency code and exchange showing available balances
        """
        self.raise_not_implemented_error()


    def load_balances_btc(self):
        """
            Returns a map by currency code and exchange showing available balances in currency terms and in btc terms
        """
        self.raise_not_implemented_error()


    def load_order_book(self):
        """
            Returns a short order book around best quotes at the example format.
            Example:
            {'Ask': {0: {'Price': 0.00876449, 'Quantity': 13.0407078},
                     1: {'Price': 0.00876901, 'Quantity': 1.78},
                     2: {'Price': 0.00878253, 'Quantity': 0.91},
                     3: {'Price': 0.00878498, 'Quantity': 34.36},
                     4: {'Price': 0.00879498, 'Quantity': 5.36827355}},
             'Bid': {0: {'Price': 0.00874998, 'Quantity': 0.06902944},
                     1: {'Price': 0.00874598, 'Quantity': 12.62079594},
                     2: {'Price': 0.00874049, 'Quantity': 0.77},
                     3: {'Price': 0.0087315, 'Quantity': 0.46},
                     4: {'Price': 0.00872501, 'Quantity': 72.15}},
             'Tradeable': 1}
        """
        self.raise_not_implemented_error()

    def submit_trade(self, direction="buy", market="", price=0, amount=0, trade_type=""):
        """
            Submits a trade with specified parameters. Returns json with amount traded.
            Example:

        """
        self.raise_not_implemented_error()

    def order_params_for_sig(self, data):
        """Convert params to ordered string for signature

        :param data:
        :return: ordered parameters like amount=10&price=1.1&type=BUY

        """
        strs = []
        for key in sorted(data):
            strs.append("{}={}".format(key, data[key]))
        return '&'.join(strs)
