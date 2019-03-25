import base64
import hashlib
import hmac
import json
import time
import uuid
from datetime import datetime

import requests

from Exchange import Exchange


class Kucoin(Exchange):
    def __init__(self, APIKey='', Secret='', PassPhrase=''):
        super().__init__(APIKey, Secret, PassPhrase)
        """
            For API details see https://docs.kucoin.com/
        """
        self._BASE_URL = 'https://openapi-v2.kucoin.com'
        self._exchangeInfo = None
        self._tick_intervals = {
            '1min':      1,
            '3min':      3,
            '5min':      5,
            '15min':     15,
            '30min':     30,
            '1hour':     60,
            '2hour':     2 * 60,
            '4hour':     4 * 60,
            '6hour':     6 * 60,
            '8hour':     8 * 60,
            '12hour':    12 * 60,
            '1day':      24 * 60,
            '1week':     7 * 24 * 60
        }

    def public_get_request(self, url):
        try:
            result = requests.get(self._BASE_URL + url).json()
            if result.get('code', None) == '200000':
                return result['data']
            else:
                print(self._BASE_URL + url + ". " + str(result.get('msg')))
                #return self.public_get_request(url)
        except Exception as e:
            print(self._BASE_URL + url + ". " + str(e))
            #return self.public_get_request(url)

    def private_sign_request(self, method, endpoint, body, nonce):
        """
            curl -H "Content-Type:application/json"
                 -H "KC-API-KEY:5c2db93503aa674c74a31734"
                 -H "KC-API-TIMESTAMP:1547015186532"
                 -H "KC-API-PASSPHRASE:Abc123456"
                 -H "KC-API-SIGN:7QP/oM0ykidMdrfNEUmng8eZjg/ZvPafjIqmxiVfYu4="
                 -X POST -d '{"currency":"BTC"}' http://openapi-v2.kucoin.com/api/v1/deposit-addresses

            KC-API-KEY = 5c2db93503aa674c74a31734
            KC-API-SECRET = f03a5284-5c39-4aaa-9b20-dea10bdcf8e3
            KC-API-PASSPHRASE = Abc123456
            TIMESTAMP = 1547015186532
            METHOD = POST
            ENDPOINT = /api/v1/deposit-addresses
            STRING-TO-SIGN = 1547015186532POST/api/v1/deposit-addresses{"currency":"BTC"}
            KC-API-SIGN = 7QP/oM0ykidMdrfNEUmng8eZjg/ZvPafjIqmxiVfYu4=
        """
        strForSign = nonce + method.upper() + endpoint + body
        return base64.b64encode(hmac.new(self._API_SECRET.encode(), strForSign.encode(), hashlib.sha256).digest()).decode()

    def private_request(self, method, endpoint, body={}):
        """
            endpoint = '/v1/KCS-BTC/order',
            command = 'amount=10&price=1.1&type=BUY'

            "KC-API-KEY":           "5c2db93503aa674c74a31734" //The api key as a string.
            "KC-API-SIGN":          "f03a5284-5c39-4aaa-9b20-dea10bdcf8e3" //The base64-encoded signature (see Signing a Message).
            "KC-API-TIMESTAMP":     1547015186532   //A timestamp for your request.
            "KC-API-PASSPHRASE":    "Abc123456"   //The passphrase you specified when creating the API key.
        """
        try:
            nonce = str(int(time.time()*1000))
            request_url = self._BASE_URL + endpoint

            body_str = ''
            if any(body):
                body_str = json.dumps(body, sort_keys=True, separators=(',',':'))

            signature = self.private_sign_request(method, endpoint, body_str, nonce)

            request = {}
            if method == 'get':
                request['params'] = body
            else:
                request['data'] = body_str
            request['headers'] =   {
                                        'Content-Type': 'application/json',
                                        "KC-API-KEY": self._API_KEY,
                                        "KC-API-TIMESTAMP": nonce,
                                        "KC-API-PASSPHRASE": self._API_PASSPHRASE,
                                        "KC-API-SIGN": signature
                                    }
            result = getattr(requests,method)(request_url, **request).json()

            if result.get('code', None) == '200000':
                return result['data']
            else:
                print(request_url + ". " + str(result))
                #return self.private_request(method,endpoint,body)

        except Exception as e:
            print(str(e))
            return {}

    ########################################
    ### Exchange specific public methods ###
    ########################################

    def public_get_base_currencies(self):
        """
            Get base currencies.
            GET /api/v1/markets
            ct['Kucoin'].public_get_base_currencies()
            [
                "BTC",
                "ETH",
                "USDT"
            ]
        """
        return self.public_get_request('/api/v1/markets')

    def public_get_market_definitions(self):
        """
            Get a list of available currency pairs for trading.
            GET /api/v1/symbols
            [{'quoteCurrency': 'BTC',
              'symbol': 'KCS-BTC',
              'quoteMaxSize': '9999999',
              'quoteIncrement': '0.000001',
              'baseMinSize': '0.01',
              'quoteMinSize': '0.00001',
              'enableTrading': True,
              'priceIncrement': '0.00000001',
              'name': 'KCS-BTC',
              'baseIncrement': '0.01',
              'baseMaxSize': '9999999',
              'baseCurrency': 'KCS'},
             {'quoteCurrency': 'BTC',
              'symbol': 'ETH-BTC',
              'quoteMaxSize': '9999999',
              'quoteIncrement': '0.000001',
              'baseMinSize': '0.0001',
              'quoteMinSize': '0.00001',
              'enableTrading': True,
              'priceIncrement': '0.000001',
              'name': 'ETH-BTC',
              'baseIncrement': '0.0001',
              'baseMaxSize': '1000000000',
              'baseCurrency': 'ETH'}]
        """
        return self.public_get_request('/api/v1/symbols')

    def public_get_ticker(self, symbol):
        """
            Ticker include only the inside (i.e. best) bid and ask data , last
            price and last trade size.
            GET /api/v1/market/orderbook/level1?symbol=<symbol>
            {'sequence': '1547728715485',
             'bestAsk': '0.00013',
             'size': '0.351',
             'price': '0.00012',
             'bestBidSize': '2.77587',
             'bestBid': '0.00012',
             'bestAskSize': '2.05255'}
        """
        return self.public_get_request('/api/v1/market/orderbook/level1?symbol=' + symbol)

    def public_get_part_order_book_agg(self, symbol):
        """
            Get a list of open orders for a symbol.
            Level-2 order book includes all bids and asks (aggregated by price),
            this level return only one size for each active price (as if there
            was only a single order for that size at the level). This API will
            return a part of Order Book within 100 depth for each side(ask or bid).
            It is recommended to use in most cases, it is the fastest Order
            Book API, and reduces traffic usage.
            GET /api/v1/market/orderbook/level2_100?symbol=<symbol>
            {'sequence': '1547728715649',
             'asks': [['0.000129', '0.01'],
              ['0.00013', '1.96012'],
              ['0.00014', '23.92009'],
              ['0.000141', '0.01'],
              ['0.000143', '0.01'],
              ['0.5', '0.98608393'],
              ['0.9', '0.12']],
             'bids': [['0.00012', '0.30662'],
              ['0.00011', '18.95473'],
              ['0.000107', '0.00999'],
              ['0.000106', '0.00999']]}
        """
        return self.public_get_request('/api/v1/market/orderbook/level2_100?symbol=' + symbol)

    def public_get_full_order_book_agg(self, symbol):
        """
            Get a list of open orders for a symbol.
            Level-2 order book includes all bids and asks (aggregated by price),
            this level return only one size for each active price (as if there
            was only a single order for that size at the level). This API will
            return data with full depth. It is generally used by professional
            traders because it uses more server resources and traffic, and we
            have strict access frequency control.
            GET /api/v1/market/orderbook/level2?symbol=<symbol>
            {'sequence': '1547728716185',
             'asks': [['0.9', '0.12'],
              ['0.5', '0.98608393'],
              ['0.000144', '0.01'],
              ['0.000143', '0.01'],
              ['0.000141', '0.01'],
              ['0.00014', '23.52082'],
              ['0.00013', '0.69795'],
              ['0.00012', '0.47062']],
             'bids': [['0.00011', '16.60746'], ['0.000107', '0.00999']]}
        """
        return self.public_get_request('/api/v1/market/orderbook/level2?symbol=' + symbol)

    def public_get_full_order_book_atomic(self, symbol):
        """
            Get a list of open orders for a symbol. Level-3 order book includes
            all bids and asks (non-aggregated, each item in Level-3 means a
            single order). Level 3 is non-aggregated and returns the entire
            order book. This API is generally used by professional traders
            because it uses more server resources and traffic, and we have
            strict access frequency control.
            GET /api/v1/market/orderbook/level3?symbol=<symbol>
            {'sequence': '1547728716310',
             'asks': [['5c419328ef83c75456bd615c', '0.9', '0.09'],
              ['5c419938ef83c75456bda415', '0.9', '0.03'],
              ['5c429820ef83c766e41096f0', '0.5', '0.98608393'],
              ...
              ['5c436fdfef83c766e43071a8', '0.00014', '0.58'],
              ['5c436fe1ef83c766e430722b', '0.00013', '0.15015'],
              ['5c436fe5ef83c766e43072a0', '0.00013', '0.88']],
             'bids': [['5c436fe8ef83c766e4307302', '0.00012', '0.37962'],
              ['5c436fe7ef83c766e43072d4', '0.00011', '0.00999'],
              ['5c436fe5ef83c766e4307298', '0.00012', '0.85914'],
              ...
              ['5c436c8bef83c766e4300479', '0.00011', '0.05994'],
              ['5c436c7cef83c766e43002be', '0.00011', '0.3837'],
              ['5c43275fef83c766e42729cf', '0.000107', '0.00999']]}
        """
        return self.public_get_request('/api/v1/market/orderbook/level3?symbol=' + symbol)

    def public_get_trade_histories(self, symbol):
        """
            List the latest trades for a symbol.
            GET /api/v1/market/histories?symbol=<symbol>
            [{'sequence': '1547728716599',
              'side': 'sell',
              'size': '0.10327',
              'price': '0.00012',
              'time': 1547923496182500913},
             {'sequence': '1547728716606',
              'side': 'buy',
              'size': '0.26145',
              'price': '0.00013',
              'time': 1547923497366885430},
             {'sequence': '1547728716608',
              'side': 'buy',
              'size': '0.24',
              'price': '0.00013',
              'time': 1547923497366885430},
             {'sequence': '1547728716610',
              'side': 'buy',
              'size': '0.04',
              'price': '0.00013',
              'time': 1547923497366885430},
             {'sequence': '1547728716612',
              'side': 'buy',
              'size': '0.33767',
              'price': '0.00013',
              'time': 1547923497366885430}]]
        """
        return self.public_get_request('/api/v1/market/histories?symbol=' + symbol)

    def public_get_klines(self, symbol, startAt, endAt, type='5min'):
        """
            Historic rates for a symbol. Rates are returned in grouped buckets
            based on requested type.

            startAt  - Start time, unix timestamp calculated in seconds not millisecond
            endAt    - End time, unix timestamp calculated in seconds not millisecond
            type     - Type of candlestick patterns
            DETAILS
            For each query, the system would return at most 1500 pieces of data.
            To obtain more data, please page the data by time.

            The type field must be one of the following values: {"1min","3min",
                "5min","15min","30min","1hour","2hour","4hour","6hour","8hour",
                "12hour", "1day","1week"}.

            The json data format is as shown below.

            [
              [
                  "1545904980",             //Start time of the candle cycle
                  "0.058",                  //opening price
                  "0.049",                  //closing price
                  "0.058",                  //highest price
                  "0.049",                  //lowest price
                  "0.018",                  //Transaction amount
                  "0.000945"                //Transaction volume
              ],
              [
                  "1545904920",
                  "0.058",
                  "0.072",
                  "0.072",
                  "0.058",
                  "0.103",
                  "0.006986"
              ]
            ]
            RESPONSE ITEMS
            Each bucket is an array of the following information:

            time bucket start time
            open opening price (first trade) in the bucket interval
            close closing price (last trade) in the bucket interval
            high highest price during the bucket interval
            low lowest price during the bucket interval
            volume volume of trading activity during the bucket interval
            turnover Turnover of a period of time. The turnover is the sum of
            the transaction volumes of all orders
            (Turnover of each order=price*quantity).
            GET /api/v1/market/candles?symbol=<symbol>

        """
        return self.public_get_request('/api/v1/market/candles?symbol={0}&startAt={1}&endAt={2}&type={3}'.format(symbol, startAt, endAt, type))

    def public_get_24hr_stats(self, symbol):
        """
            Get 24 hr stats for the symbol. volume is in base currency units.
            open, high, low are in quote currency units.
            GET /api/v1/market/stats
            {'symbol': 'KCS-BTC',
             'high': '0.5',
             'vol': '23207.79102607',
             'low': '0.00009',
             'changePrice': '-0.00001',
             'changeRate': '-0.0769',
             'volValue': '2.95767623942'}
        """
        return self.public_get_request('/api/v1/market/stats/' + symbol)

    def public_get_currencies(self):
        """
            List known currencies.
            GET /api/v1/currencies
            [{'precision': 8, 'name': 'BTC', 'fullName': 'Bitcoin', 'currency': 'BTC'},
             {'precision': 8, 'name': 'ETH', 'fullName': 'Ethereum', 'currency': 'ETH'},
             {'precision': 10, 'name': 'KCS', 'fullName': 'KCS shares', 'currency': 'KCS'},
             {'precision': 8, 'name': 'USDT', 'fullName': 'USDT', 'currency': 'USDT'}]
        """
        return self.public_get_request('/api/v1/currencies')

    def public_get_currency_detail(self, currency):
        """
            Get single currency detail
            GET /api/v1/currencies/{currency}
            {'withdrawalMinFee': '0.001',
             'precision': 10,
             'name': 'KCS',
             'fullName': 'KCS shares',
             'currency': 'KCS',
             'withdrawalMinSize': '0.001',
             'isWithdrawEnabled': False,
             'isDepositEnabled': False}
        """
        return self.public_get_request('/api/v1/currencies/' + currency)

    def public_get_server_time(self):
        """
            Get the API server time.
            GET /api/v1/timestamp
            1547924920579
        """
        return self.public_get_request('/api/v1/timestamp')

    def public_get_all_tickers(self):
        """
            Get all tickers
            Debug: ct['Kucoin'].public_get_all_tickers()
        """
        return self.public_get_request('/api/v1/market/allTickers')

    #########################################
    ### Exchange specific private methods ###
    #########################################

    def private_get_accounts(self, currency = None, account_type = None):
        """
            Get a list of accounts.
            GET /api/v1/accounts?currency=<currency>&type=<type>
            [{'balance': '0.1',
              'available': '0.1',
              'holds': '0',
              'currency': 'BTC',
              'id': '5c435fc9ef83c7101c96f216',
              'type': 'main'},
             {'balance': '500',
              'available': '500',
              'holds': '0',
              'currency': 'KCS',
              'id': '5c435fcaef83c7101c96f261',
              'type': 'main'},
             {'balance': '1',
              'available': '1',
              'holds': '0',
              'currency': 'ETH',
              'id': '5c435fc9ef83c7101c96f215',
              'type': 'main'}]
        """
        request = ''
        if currency is not None:
            request += 'currency=' + currency
        if account_type is not None:
            request += 'type=' + account_type
        if request != '':
            request = '?' + request
        return self.private_request('get', '/api/v1/accounts' + request)

    def private_get_account(self, accountId):
        """
            Information for a single account. Use this endpoint when you know the accountId.
            GET /api/v1/accounts/<accountId>
            {'balance': '0.1',
             'available': '0.1',
             'holds': '0',
             'currency': 'BTC'}
        """
        return self.private_request('get', '/api/v1/accounts/' + accountId)

    def private_create_account(self, account_type, currency):
        """
            Create an Account.
            POST /api/v1/accounts
            'Internal Server Error!'
        """
        return self.private_request('post', '/api/v1/accounts', {
                    'type': account_type,
                    'currency': currency
                })

    def private_get_account_history(self, accountId, startAt, endAt, pageSize= 100, currentPage = 1):
        """
            List account activity. Account activity either increases or decreases
            your account balance. Items are paginated and sorted latest first.
            See the Pagination section for retrieving additional entries after the first page.
            GET /api/v1/accounts/<accountId>/ledgers
            {'totalNum': 1,
             'totalPage': 1,
             'pageSize': 100,
             'currentPage': 1,
             'items': [{'createdAt': 1547919305000,
                       'amount': '0.1',
                       'bizType': 'Deposit',
                       'balance': '0.1',
                       'fee': '0',
                       'context': '',
                       'currency': 'BTC',
                       'direction': 'in'}]}
        """
        return self.private_request('get',
                                        '/api/v1/accounts/{}/ledgers?startAt={}&endAt={}&pageSize={}&currentPage={}'.format(
                                                accountId, startAt, endAt, pageSize, currentPage
                                            ))

    def private_get_account_holds(self, accountId):
        """
            Holds are placed on an account for any active orders or pending
            withdraw requests. As an order is filled, the hold amount is updated.
            If an order is canceled, any remaining hold is removed. For a withdraw,
            once it is completed, the hold is removed.
            GET /api/v1/accounts/<accountId>/holds
        """
        return self.private_request('get', '/api/v1/accounts/' + accountId + '/holds')

    def private_post_inner_transfer(self, clientOid, payAccountId, recAccountId, amount):
        """
            The inner transfer interface is used for assets transfer among the
            accounts of a user and is free of charges on the platform. For example,
            a user could transfer assets for free form the main account to the
            trading account on the platform.
            POST /api/v1/accounts/inner-transfer
        """
        return self.private_request('post', '/api/v1/accounts/inner-transfer', {
                    'clientOid': clientOid,
                    'payAccountId': payAccountId,
                    'recAccountId': recAccountId,
                    'amount': amount,
                })

    def private_submit_new_order(self, side, symbol, price, size, timeInForce, order_type = 'limit'):
        """
            You can place two types of orders: limit and market. Orders can only
            be placed if your account has sufficient funds. Once an order is placed,
            your account funds will be put on hold for the duration of the order.
            How much and which funds are put on hold depends on the order type
            and parameters specified. See the Holds details below. The maximum
            matching orders for a single trading pair in one account is 50
            (stop limit order included).
            POST /api/v1/orders
            Param	type	Description
            clientOid	string	Unique order id selected by you to identify your order e.g. UUID
            type	string	[optional] limit or market (default is limit)
            side	string	buy or sell
            symbol	string	a valid trading symbol code. e.g. ETH-BTC
            remark	string	[optional] remark for the order, length cannot exceed 100 utf8 characters
            stop	string	[optional] Either loss or entry. Requires stopPrice to be defined
            stopPrice	string	[optional] Only if stop is defined. Sets trigger price for stop order
            stp	string	[optional] self trade protect , CN, CO, CB or DC
            LIMIT ORDER PARAMETERS
            Param	type	Description
            price	string	price per base currency
            size	string	amount of base currency to buy or sell
            timeInForce	string	[optional] GTC, GTT, IOC, or FOK (default is GTC)
            cancelAfter	long	[optional] * cancel after n seconds
            postOnly	boolean	[optional] ** Post only flag
            * Requires timeInForce to be GTT
            ** Invalid when timeInForce is GTC, IOC or FOK
            MARKET ORDER PARAMETERS
            Param	type	Description
            size	string	[optional] Desired amount in base currency
            funds	string	[optional] Desired amount of quote currency to use
        """
        clientOid = str(uuid.uuid4())
        request = {
                    'clientOid': clientOid,
                    'type': order_type,
                    'side': side,
                    'symbol': symbol,
                }
        if price is not None:
            request['price'] = price
        if size is not None:
            request['size'] = size
        if timeInForce is not None:
            request['timeInForce'] = timeInForce
        return self.private_request('post', '/api/v1/orders', request)

    def private_cancel_order(self, clientOid):
        """
            Cancel a previously placed order.

            You would receive the request return once the system has received
            the cancellation request. The cancellation request will be processed
            by matching engine in sequence. To know if the request is processed
            (success or not), you may check the order status or update message
            from the pushes.
        """
        request = {
                    'clientOid': clientOid
                }
        return self.private_request('delete', '/api/v1/orders', request)

    def private_cancel_all_orders(self):
        """
            With best effort, cancel all open orders. The response is a list of
            ids of the canceled orders.
        """
        return self.private_request('delete', '/api/v1/orders')

    def private_get_orders(self, request = {}):
        """
            List your current orders.

            Param	Type	Description
            status	string	[optional] active or done, done as default, Only
                list orders for a specific status .
            symbol	string	[optional] Only list orders for a specific symbol.
            side	string	[optional] buy or sell
            type	string	[optional] limit, market, limit_stop or market_stop
            startAt	long	[optional] Start time. Unix timestamp calculated in
                milliseconds, the creation time queried shall posterior to the
                start time.
            endAt	long	[optional] End time. Unix timestamp calculated in
                milliseconds, the creation time queried shall prior to the end
                time.
             [
                  {
                    "id": "5c35c02703aa673ceec2a168",   //orderid
                    "symbol": "BTC-USDT",   //symbol
                    "opType": "DEAL",      // operation type,deal is pending order,cancel is cancel order
                    "type": "limit",       // order type,e.g. limit,markrt,stop_limit.
                    "side": "buy",         // transaction direction,include buy and sell
                    "price": "10",         // order price
                    "size": "2",           // order quantity
                    "funds": "0",          // order funds
                    "dealFunds": "0.166",  // deal funds
                    "dealSize": "2",       // deal quantity
                    "fee": "0",            // fee
                    "feeCurrency": "USDT", // charge fee currency
                    "stp": "",             // self trade prevention,include CN,CO,DC,CB
                    "stop": "",            // stop type
                    "stopTriggered": false,  // stop order is triggered
                    "stopPrice": "0",      // stop price
                    "timeInForce": "GTC",  // time InForce,include GTC,GTT,IOC,FOK
                    "postOnly": false,     // postOnly
                    "hidden": false,       // hidden order
                    "iceberg": false,      // iceberg order
                    "visibleSize": "0",    // display quantity for iceberg order
                    "cancelAfter": 0,      // cancel orders time，requires timeInForce to be GTT
                    "channel": "IOS",      // order source
                    "clientOid": "",       // user-entered order unique mark
                    "remark": "",          // remark
                    "tags": "",            // tag order source
                    "isActive": false,     // status before unfilled or uncancelled
                    "cancelExist": false,   // order cancellation transaction record
                    "createdAt": 1547026471000  // time
                  }
                ]
        """
        if self.has_api_keys():
            return self.private_request('get', '/api/v1/orders', request)
        else:
            return []

    #######################
    ### Generic methods ###
    #######################
    def get_consolidated_currency_definitions(self):
        """
            Loading currencies
            Debug: ct['Kucoin'].get_consolidated_currency_definitions()
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
        currencies = self.public_get_currencies()
        results = {}
        if isinstance(currencies, list):
            for currency in currencies:
                try:
                    results[currency['currency']] = {
                        'Name': currency['fullName'],
                        'DepositEnabled': currency['isDepositEnabled'],
                        'WithdrawalEnabled': currency['isWithdrawEnabled'],
                        'Notice': '',
                        'ExchangeBaseAddress': '',
                        'MinConfirmation': 0,
                        'WithdrawalFee': float(currency.get('withdrawalMinFee', 0)),
                        'WithdrawalMinAmount': float(currency.get('withdrawalMinSize', 0)),
                        'Precision': pow(10,-currency['precision'])
                    }
                except Exception as e:
                    self.log_request_error(str(e))

        return results

    def update_market_definitions(self, force_update = False):
        """
            Used to get the open and available trading markets at Binance along
            with other meta data.
            * force_update = False assumes that self._exchangeInfo was filled
            in recently enough
            Debug: ct['Kucoin'].update_market_definitions()
        """
        symbols = self.public_get_market_definitions()
        if isinstance(symbols, list):
            for market in symbols:
                try:
                    is_active = market.get('enableTrading', False)
                    is_restricted = not is_active

                    self.update_market(
                        market['symbol'],
                        {
                            'LocalBase':        market['quoteCurrency'],
                            'LocalCurr':        market['baseCurrency'],
                            'BaseMinAmount':    float(market.get('quoteMinSize',    0)),
                            'BaseIncrement':    float(market.get('quoteIncrement',  0.00000001)),
                            'CurrMinAmount':    float(market.get('baseMinSize',     0)),
                            'CurrIncrement':    float(market.get('baseIncrement',   0.00000001)),
                            'PriceMin':         0,
                            'PriceIncrement':   float(market.get('priceIncrement',  0.00000001)),
                            'IsActive':         is_active,
                            'IsRestricted':     is_restricted,
                        }
                    )
                except Exception as e:
                    self.log_request_error(str(e))

    def update_market_quotes(self):
        """
            Used to get the market quotes
            Debug: ct['Kucoin'].update_market_quotes()
        """
        all_markets = self.public_get_all_tickers()['ticker']
        if isinstance(all_markets, list):
            for ticker in all_markets:
                try:
                    market_symbol = ticker['symbol']
                    dict = {
                        'BestBid':          float(ticker.get('buy', 0)),
                        'BestAsk':          float(ticker.get('sell', 0)),
                        'CurrVolume':       float(ticker.get('vol', 0)),
                        '24HrHigh':         float(ticker.get('high', 0)),
                        '24HrLow':          float(ticker.get('low', 0)),
                        '24HrPercentMove':  float(ticker.get('changeRate', 0)) * 100,
                        'LastTradedPrice':  float(ticker.get('last', 0)),
                    }
                    self.update_market(
                        market_symbol,
                        dict
                    )
                except Exception as e:
                    self.log_request_error(str(e))

    def update_market_24hrs(self):
        """
            Used to update 24-hour statistics
            Debug: ct['Kucoin'].update_market_24hr()
        """
        self.update_market_quotes()

    def get_consolidated_open_user_orders_in_market(self, market):
        """
            Used to retrieve outstanding orders
            Debug: ct['Kucoin'].get_consolidated_open_user_orders_in_market('LTCBTC')
        """
        open_orders = self.private_get_orders({
            'symbol': market,
            'status': 'active'
        })
        results = []
        for order in open_orders:
            if order['side'] == 'buy':
                order_type = 'Buy'
            else:
                order_type = 'Sell'

            results.append({
                'OrderId': order['id'],
                'OrderType': order_type,
                'OpderOpenedAt': datetime.fromtimestamp(market['createdAt'] / 1000),
                'Price': float(order['price']),
                'Amount': float(order['size']),
                'Total': float(order['dealSize']),
                'AmountRemaining': float(order['dealFunds']),
            })
        return results

    def get_consolidated_recent_market_trades_per_market(self, market):
        """
            Used to update recent market trades at a given market
            Debug: ct['Kucoin'].update_recent_market_trades_per_market('LTCBTC')
        """
        trades = self.public_get_trade_histories(market)
        results = []
        for trade in trades:
            if trade['side'] == 'buy':
                order_type = 'Buy'
            else:
                order_type = 'Sell'

            if float(trade['price']) > 0 and float(trade['size']) > 0:
                results.append({
                    'TradeId': trade['sequence'],
                    'TradeType': order_type,
                    'TradeTime': datetime.fromtimestamp(trade['time'] / 1000000000),
                    'Price': float(trade['price']),
                    'Amount': float(trade['size']),
                    'Total': float(trade['price']) * float(trade['size'])
                })
        return results

    def get_consolidated_klines(self, market_symbol, interval = '5m', lookback = None, startAt = None, endAt = None):
        """
            Klines for a symbol. Data are returned in grouped buckets based on
            requested type.
            Param	Description
            startAt	Start time. Unix timestamp calculated in seconds not
                millisecond
            endAt	End time. Unix timestamp calculated in seconds not
                millisecond
            type	Type of candlestick patterns: 1min, 3min, 5min, 15min,
                30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week
            [
              [
                  "1545904980",             //Start time of the candle cycle
                  "0.058",                  //opening price
                  "0.049",                  //closing price
                  "0.058",                  //highest price
                  "0.049",                  //lowest price
                  "0.018",                  //Transaction amount
                  "0.000945"                //Transaction volume
              ],
            ]
        """
        if lookback is None:
            lookback = 24 * 60
        if startAt is None:
            endAt = int(datetime.now().timestamp())
            startAt = endAt - lookback * 60

        load_chart = self.public_get_klines(market_symbol, startAt, endAt, interval)
        results = []
        for i in load_chart:
            new_row = int(i[0]), float(i[1]), float(i[3]), float(i[4]), float(i[2]), float(i[5]), float(i[6])
            results.append(new_row)
        return results

    def get_consolidated_order_book(self, market, depth = 5):
        raw_results = self.public_get_part_order_book_agg(market)
        take_bid = min(depth, len(raw_results['bids']))
        take_ask = min(depth, len(raw_results['asks']))

        if take_bid == 0 and take_ask == 0:
            results = { 'Tradeable': 0, 'Bid': {}, 'Ask': {} }
        else:
            results = { 'Tradeable': 1, 'Bid': {}, 'Ask': {} }
        for i in range(take_bid):
            results['Bid'][i] = {
                'Price': float(raw_results['bids'][i][0]),
                'Quantity': float(raw_results['bids'][i][1]),
            }
        for i in range(take_ask):
            results['Ask'][i] = {
                'Price': float(raw_results['asks'][i][0]),
                'Quantity': float(raw_results['asks'][i][1]),
            }

        return results





    def load_available_balances(self):
        """
            ct['Kucoin'].load_available_balances()
        """
        available_balances = self.private_get_accounts()
        self._available_balances = {}
        for balance in available_balances:
            currency = balance['currency']
            if currency not in self._available_balances:
                self._available_balances[currency] = 0
            self._available_balances[currency] += float(balance["available"])
        return self._available_balances

    def load_balances_btc(self):
        """
            ct['Kucoin'].load_balances_btc()
        """
        available_balances = self.private_get_accounts()
        self._complete_balances_btc = {}
        for balance in available_balances:
            currency = balance['currency']
            if currency not in self._complete_balances_btc:
                self._complete_balances_btc[currency] = {
                    'Available': 0,
                    'OnOrders': 0,
                    'Total': 0
                }
            self._complete_balances_btc[currency]['Available'] += float(balance['available'])
            self._complete_balances_btc[currency]['OnOrders'] += float(balance['balance']) - float(balance['available'])
            self._complete_balances_btc[currency]['Total'] += float(balance['balance'])
        return self._complete_balances_btc

    def submit_trade(self, direction, market, price, amount, trade_type):
        pass
