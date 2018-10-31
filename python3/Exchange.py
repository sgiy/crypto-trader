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
        self._tick_intervals = {}
        self._tick_lookbacks = {}
        self._map_tick_intervals = {}

    def raise_not_implemented_error(self):
        raise NotImplementedError("Class " + self.__class__.__name__ + " needs to implement method " + traceback.extract_stack(None, 2)[0][2] + "!!! ")

    def print_exception(self, message=''):
        print(self.__class__.__name__ + " has an exception in method " + traceback.extract_stack(None, 2)[0][2] + "!!! " + message)

    def get_global_code(self, local_code):
        return self._map_exchange_code_to_currency_code.get(local_code, None)

    def load_currencies(self):
        """
            Individual exchange implementation needs to update self._currencies
            with a map from exchange currency code to a map having Name and
            Enabled keys.
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

    def update_market(self,
            market_symbol,
            local_base,
            local_curr,
            best_bid,
            best_ask,
            is_active = True,
            qty_bid = None,
            qty_ask = None):
        """
            Updates self._markets and self._active_markets using provided
            market_symbol (exchange symbol for traded pair, e.g. 'BTC-ETH')
            local_base (exchange code for base currency)
            local_curr (exchange code for traded currency)
            best_bid (best bid price)
            best_ask (best ask price)
            is_active (flag showing if market is active as opposed to frozen)
            qty_bid (if available, this shows quantity of traded currency available at bid price)
            qty_ask (if available, this shows quantity of traded currency available at ask price)
        """
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
            Individual exchange implementation needs to update self._markets
            and self._active_markets using update_market function resulting in
            maps of maps with a structure:
            {
                'BTC': {
                    'ETH': {
                        'Market': market_symbol,
                        'Bid': best_bid,
                        'Ask': best_ask,
                        'QtyBid': qty_bid, -optional
                        'QtyAsk': qty_ask  -optional
                    }
                }
            }.
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
            Returns a short order book around best quotes in the following format:
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

    def load_ticks(self, market_name, interval, lookback):
        """
            interval is an exchange specific name, e.g. 'fiveMin'
            Returns a candlestick data: times, opens, closes, ...
            Example:
            [
                (time, open, high, low, close, volume, baseVolume)
            ]
        """
        self.raise_not_implemented_error()

    def load_chart_data(self, market_name, interval, lookback):
        """
            interval and lookback come in terms of number of minutes
        """
        self._map_tick_intervals = {}
        take_i_name = None
        take_i_mins = None
        for i_name in self._tick_intervals:
            i_mins = self._tick_intervals[i_name]
            self._map_tick_intervals[i_mins] = i_name
            if take_i_mins is None or (i_mins <= interval and i_mins > take_i_mins):
                take_i_mins = i_mins
                take_i_name = i_name

        number_of_ticks_to_take = int(lookback / interval)
        preliminary_ticks = self.load_ticks(market_name, take_i_name, lookback)
        if take_i_mins == interval:
            return preliminary_ticks[-number_of_ticks_to_take:]
        else:
            base = interval / take_i_mins
            number_of_ticks_to_consider = int(number_of_ticks_to_take * base)
            number_of_ticks_to_consider = min(number_of_ticks_to_consider, len(preliminary_ticks))
            start_index = len(preliminary_ticks) - number_of_ticks_to_consider
            results = []
            for i in range(number_of_ticks_to_consider):
                if i % base == 0:
                    open_v = preliminary_ticks[start_index + i][1]
                    high_v = preliminary_ticks[start_index + i][2]
                    low_v = preliminary_ticks[start_index + i][3]
                    volume_v = preliminary_ticks[start_index + i][5]
                    baseVolume_v = preliminary_ticks[start_index + i][6]
                else:
                    if preliminary_ticks[start_index + i][2] > high_v:
                        high_v = preliminary_ticks[start_index + i][2]
                    if preliminary_ticks[start_index + i][3] < low_v:
                        low_v = preliminary_ticks[start_index + i][3]
                    volume_v += preliminary_ticks[start_index + i][5]
                    baseVolume_v += preliminary_ticks[start_index + i][6]
                    if i % base == base - 1:
                        close_v = preliminary_ticks[start_index + i][4]
                        time_v = preliminary_ticks[start_index + i][0]
                        new_row = time_v, open_v, high_v, low_v, close_v, volume_v, baseVolume_v
                        results.append(new_row)
            return results

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
