# Abstract Exchange class. Each exchange implementation should inherit from it.
import traceback
import time

class Exchange:
    def __init__(self, APIKey='', Secret='', PassPhrase=''):
        self.update_keys(APIKey, Secret, PassPhrase)
        self._BASE_URL = ''
        self._API_KEY = ''
        self._API_SECRET = ''
        self._API_PASSPHRASE = ''

        self._currencies = {}
        self._markets = {}
        self._active_markets = {}
        self._balances = {}
        self._timestamps = {}

        self._map_currency_code_to_exchange_code = {}
        self._map_exchange_code_to_currency_code = {}
        self._map_market_to_global_codes = {}


        self._market_prices = {}
        self._available_balances = {}
        self._complete_balances_btc = {}
        self._tick_intervals = {}
        self._tick_lookbacks = {}
        self._map_tick_intervals = {}
        self._max_error_count = 3
        self._error ={
            'count': 0,
            'message': '',
            'result_timestamp': time.time()
        }

    def update_keys(self, APIKey='', Secret='', PassPhrase=''):
        self._API_KEY = APIKey
        self._API_SECRET = Secret
        self._API_PASSPHRASE = PassPhrase

    def load_currencies(self):
        """
            get_formatted_currencies() needs to return a dictionary:
            exchange currency code to a dictionary
            Example:
                {
                    'BTC': {
                                'Name': 'Bitcoin',
                                'DepositEnabled': True,
                                'WithdrawalEnabled': True,
                                'Notice': '',
                                'ExchangeBaseAddress': 'address',
                                'MinConfirmation': 2,
                                'WithdrawalFee': 0.001,
                                'WithdrawalMinAmount': 0.001,
                                'Precision': 0.00000001
                            },
                    ...
                }
        """
        currencies = self.get_formatted_currencies()
        for currency in currencies.keys():
            if currency in self._currencies:
                self._currencies[currency].update(currencies[currency])
            else:
                self._currencies[currency] = currencies[currency]
        self._timestamps['load_currencies'] = time.time()

    def update_market_definitions(self):
        """
            Updates _markets with current market definitions
        """
        self.raise_not_implemented_error()

    def get_global_code(self, local_code):
        return self._map_exchange_code_to_currency_code.get(local_code, None)

    def get_local_code(self, global_code):
        return self._map_currency_code_to_exchange_code.get(global_code, None)

    def update_market(self, market_symbol, dict):
        """
            Updates self._markets and self._active_markets using provided
            market_symbol (exchange symbol for traded pair, e.g. 'BTC-ETH')
            local_base (exchange code for base currency)
            local_curr (exchange code for traded currency)
            dict contains a dictionary of data to update for the market:
            {
                'BaseMinAmount': 0,
                'BaseIncrement': 0.00000001,
                'CurrMinAmount': 0,
                'CurrIncrement': 0.00000001,
                'IsActive':      True,
                'IsRestricted':  False,
                'Notice':        '',
                'Created':       datetime,
                'LogoUrl':       'url',
            }
        """
        local_base = dict.pop('LocalBase', None)
        local_curr = dict.pop('LocalCurr', None)
        if local_base is not None and local_curr is not None:
            code_base = self.get_global_code(local_base)
            code_curr = self.get_global_code(local_curr)
            self._map_market_to_global_codes[market_symbol] = {
                'LocalBase': local_base,
                'LocalCurr': local_curr,
                'GlobalBase': code_base,
                'GlobalCurr': code_curr
            }
        else:
            if market_symbol in self._map_market_to_global_codes:
                code_base = self._map_market_to_global_codes[market_symbol]['GlobalBase']
                code_curr = self._map_market_to_global_codes[market_symbol]['GlobalCurr']
            else:
                code_base = self.get_global_code(local_base)
                code_curr = self.get_global_code(local_curr)

        if not code_base in self._markets:
            self._markets[code_base] = {}
        if not code_curr in self._markets[code_base]:
            self._markets[code_base][code_curr] = {}
        if not code_base in self._active_markets:
            self._active_markets[code_base] = {}
        if not code_curr in self._active_markets[code_base]:
            self._active_markets[code_base][code_curr] = {}

        update_dict = {
            'MarketSymbol':     market_symbol,
            'BaseMinAmount':    0,
            'BaseIncrement':    0.00000001,
            'CurrMinAmount':    0,
            'CurrIncrement':    0.00000001,
            'PriceMin':         0,
            'PriceIncrement':   0.00000001,
            'IsActive':         True,
            'IsRestricted':     False,
            'Notice':           '',
        }
        update_dict.update(dict)
        self._markets[code_base][code_curr].update(update_dict)

        if update_dict['IsActive'] and not update_dict['IsRestricted']:
            self._active_markets[code_base][code_curr].update(update_dict)
        else:
            self._active_markets[code_base].pop(code_curr)

    def get_market_name(self, code_base, code_curr):
        return self._markets[code_base][code_curr]['MarketSymbol']


    def raise_not_implemented_error(self):
        raise NotImplementedError("Class " + self.__class__.__name__ + " needs to implement method " + traceback.extract_stack(None, 2)[0][2] + "!!! ")

    def log_request_success(self):
        self._error ={
            'count': 0,
            'message': '',
            'result_timestamp': time.time()
        }

    def log_request_error(self, message):
        error_message = 'Exception in class {} method {}: {}'.format(self.__class__.__name__, traceback.extract_stack(None, 2)[0][2], message)
        print(error_message)
        self._error ={
            'count': self._error['count'] + 1,
            'message': error_message
        }

    def retry_count_not_exceeded(self):
        return self._error['count'] < self._max_error_count

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


    def load_order_book(self, market, depth):
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
                (
                    time, - timestamp in seconds
                    open,
                    high,
                    low,
                    close,
                    volume,
                    baseVolume
                )
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
        if preliminary_ticks is None:
            return None
        else:
            if take_i_mins == interval:
                results = []
                for entry in preliminary_ticks:
                    if entry[0] >= preliminary_ticks[-1][0] - lookback * 60:
                        results.append(entry)
                return results
            else:
                results = []
                result_dict = {}
                for entry in preliminary_ticks:
                    agg_timestamp = int(entry[0] - entry[0] % (interval * 60))
                    if agg_timestamp in result_dict:
                        result_dict[agg_timestamp]['h'] = max(result_dict[agg_timestamp]['h'], entry[2])
                        result_dict[agg_timestamp]['l'] = min(result_dict[agg_timestamp]['l'], entry[3])
                        result_dict[agg_timestamp]['c'] = entry[4]
                        result_dict[agg_timestamp]['v'] += entry[5]
                        result_dict[agg_timestamp]['bv'] += entry[6]
                    else:
                        result_dict[agg_timestamp] = {
                            'o': entry[1],
                            'h': entry[2],
                            'l': entry[3],
                            'c': entry[4],
                            'v': entry[5],
                            'bv': entry[6]
                        }

                for agg_timestamp in result_dict:
                    if agg_timestamp >= preliminary_ticks[-1][0] - lookback * 60:
                        new_row =  (agg_timestamp,
                                    result_dict[agg_timestamp]['o'],
                                    result_dict[agg_timestamp]['h'],
                                    result_dict[agg_timestamp]['l'],
                                    result_dict[agg_timestamp]['c'],
                                    result_dict[agg_timestamp]['v'],
                                    result_dict[agg_timestamp]['bv'])
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

    def get_available_balance(self, currency, force_update = False):
        if not self._available_balances or force_update:
            self.load_available_balances()
        return self._available_balances.get(currency, 0)
