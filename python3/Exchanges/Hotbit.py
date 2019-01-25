import base64
import time
import hmac
import hashlib
import urllib
import requests

from Exchange import Exchange

import ipdb

class Hotbit(Exchange):
    def __init__(self, APIKey='', Secret=''):
        super().__init__(APIKey, Secret)
        self.BASE_URL = 'https://api.hotbit.io/api/v1'

    def get_request(self, url):
        try:
            result = requests.get(self.BASE_URL + url).json()
            if result.get('error', None) is None:
                self.log_request_success()
                return result
            else:
                self.log_request_error(result['error']['message'])
                if self.retry_count_not_exceeded():
                    return self.get_request(url)
                else:
                    return {}
        except Exception as e:
            self.log_request_error(self.BASE_URL + url + ". " + str(e))
            if self.retry_count_not_exceeded():
                return self.get_request(url)
            else:
                return {}

    def trading_api_request(self, method, endpoint = '', extra = ''):
        """

        """
        try:
            url = self.BASE_URL + endpoint + '?Api_key=' + self.APIKey + '&sign='
            string_to_sign = 'api_key=' + self.APIKey + extra + '&secret_key=' + self.Secret
            signature = hashlib.md5("whatever your string is".encode('utf-8')).hexdigest()
            signature = signature.upper()
            url += signature
            result = getattr(requests, method)(url).json()

            if result.get('error', None) is None:
                self.log_request_success()
                return result
            else:
                self.log_request_error(result['error']['message'])
                if self.retry_count_not_exceeded():
                    return self.trading_api_request(method, endpoint, extra)
                else:
                    return {}

        except Exception as e:
            self.log_request_error(str(e))
            if self.retry_count_not_exceeded():
                return self.trading_api_request(method, endpoint, extra)
            else:
                return {}

    ########################################
    ### Exchange specific public methods ###
    ########################################

    def get_server_time(self):
        """
            Get system time
            ct['Hotbit'].get_server_time()
            Response:
                1520919059
        """
        return self.get_request('/server.time')['result']

    def get_asset_list(self):
        """
            Get all asset types and precisions of the platform, prec is accurate
            to the number of decimal places
            ct['Hotbit'].get_asset_list()
            Response:
                [
                    {
                        "name": "BTC",
                        "prec": 8
                    },
                    ...
                    {
                        "name": "ETH",
                        "prec": 8
                    }
                ]
        """
        return self.get_request('/asset.list')['result']

    def order_history(self, market, side, offset, limit):
        """
            Get a list of deals
            Market: Market name, such as: "BTC/USDT", "BCC/USDT"
            Side: 1 = "sell", 2="buy"
            Offset: Offset position, if set to 0, means that from the beginning
                of the latest business, all transactions recorded to the
                previous time, the total number of pens cannot be greater than
                limit; If set to 1, it means that from the beginning of the new
                business, the total number of transactions in the previous time
                cannot be greater than the limit; and so on.....
            Limit: Returns the maximum number of "records"
            ct['Hotbit'].order_history('ETH/BTC',2,0,100)
            Response:
            {'limit': 100,
            'offset': 0,
            'orders': [{'amount': '10',
                        'ctime': 100000000,
                        'deal_fee': '0',
                        'deal_money': '0',
                        'deal_stock': '0',
                        'id': 100000000,
                        'left': '10',
                        'maker_fee': '0',
                        'market': 'ETHBTC',
                        'mtime': 100000000,
                        'price': '0.033000',
                        'side': 2,
                        'source': 'web',
                        'taker_fee': '0.0000',
                        'type': 1,
                        'user': 100000},
            ...,
            'total': 100}
        """
        return self.get_request('/order.book?market={}&side={}&offset={}&limit={}'.format(market, side, offset, limit))['result']

    def order_book(self, market, limit, interval):
        """
            Get transaction depth
            Market: Market name, such as: "BTC/USDT", "BCC/USDT"
            Limit: Returns the maximum number of "records", values: 1, 5, 10,
                20, 30, 50, 100
            Interval: Price accuracy, value: 0, 0.1, 0.01, 0.001, ...,
                0.000000001
            ct['Hotbit'].order_book('ETH/BTC',5,0.00000001)
            Response:
        		{
        			"asks": [["0.0733858", "0.319"], ["0.0741178", "0.252"], ["0.0742609", "0.03"], ... ["0.1250465", "0.272"]],
        			"bids": [["0.0730197", "0.275"], ["0.0723", "1.052"], ["0.0722876", "0.302"], ... ["2.0e-7", "1"]]
                },
        """
        return self.get_request('/order.depth?&market={}&limit={}&interval={}'.format(market, limit, interval))['result']

    def market_list(self):
        """
            Get a list of deal pairs
            ct['Hotbit'].market_list()
            Response:
                [
                    {
                        "name": "QASHBTC",
                        "stock": "QASH",
                        "money": "BTC",
                        "fee_prec": 4,  #税率精度4位小数
                        "stock_prec": 2, #stock精度
                        "money_prec": 8, #money精度
                        "min_amount": "0.1" #下单最小值
                    },
                    {
                        "name": "QASHETH",
                        "stock": "QASH",
                        "money": "ETH",
                        "fee_prec": 4,
                        "stock_prec": 2,
                        "money_prec": 8,
                        "min_amount": "0.0001"
                    }
                ]
        """
        return self.get_request('/market.list')['result']

    def market_last(self, market):
        """
            Get the latest price for the specified deal pair
            ct['Hotbit'].market_last('ETH/BTC')
            Response:
                "0.07413600"
        """
        return self.get_request('/market.last?market={}'.format(market))['result']

    def market_deals(self, market, limit, last_id):
        """
            Query transaction to transaction record
            Market: Market name, such as: "BTC/USDT", "BCC/USDT"
            Limit: Query limit (limit <= 1000)
            Last_id: Returns transaction data greater than order_id > last_id
            ct['Hotbit'].market_deals('ETH/BTC',5,0.00000001)
            Response:
                [{'amount': '1.0',
                  'id': 1000,
                  'price': '0.03',
                  'time': 1000,
                  'type': 'buy'},
        """
        return self.get_request('/market.deals?market={}&limit={}&last_id={}'.format(market, limit, last_id))['result']

    def market_kline(self, market, start_time, end_time, interval):
        """
            k line query
            Market: Market name, such as: "BTC/USDT", "BCC/USDT"
            Start_time: Start time stamp
            End_time: End timestamp
            Interval: Cycle interval, in seconds, (start time to end time, total
                number of cycles) < 1000
            ct['Hotbit'].market_kline('ETH/BTC',1500000000,1500003000,300)
            Response:
                [[1500000000,
                  '0.03',   // open
                  '0.03',   // close
                  '0.03',   // high
                  '0.03',   // low
                  '33.3',   // volume in currency
                  '1.0',    // volume in base
                  'ETHBTC'],
                  ...
        """
        return self.get_request('/market.kline?market={}&start_time={}&end_time={}&interval={}'.format(
            market, start_time, end_time, interval))['result']

    def market_status(self, market, period):
        """
            Get the current latest price changes, trading volume,
            maximum/minimum price, etc. of the market in the past specified time
            period
            Market: Market name, such as: "BTC/USDT", "BCC/USDT"
            Period: The query period, in seconds. That is, the time to push
                forward from now on, for example: 86400, is the last 24 hours.
            ct['Hotbit'].market_status('ETH/BTC',86400)
            Response:
            {
                "period": 10,
                "last": "0.0743",
                "open": "0.074162",
                "close": "0.0743",
                "high": "0.0743",
                "low": "0.074162",
                "volume": "0.314",
                "deal": "0.023315531"
            }
        """
        return self.get_request('/market.status?market={}&period={}'.format(market, period))['result']

    def market_status_today(self, market):
        """
            Get today's market status
            Market: Market name, such as: "BTC/USDT", "BCC/USDT"
            ct['Hotbit'].market_status_today('ETH/BTC')
            Response:
            {
                "open": "0.074015",
                "last": "0.074287",
                "high": "0.074485",
                "low": "0.073",
                "volume": "1141.63",
                "deal": "83.11985574"
            }
        """
        return self.get_request('/market.status_today?market={}'.format(market))['result']

    def market_status24h(self):
        """
            Get market ups and downs, trading volume, maximum/minimum price,
            etc. in the past 24 hours
            ct['Hotbit'].market_status24h()
            Response:
            {
                "TRXETH": {
                    "period": 86400,
                    "last": "0.00013199",
                    "open": "0.00013523",
                    "close": "0.00013199",
                    "high": "0.00013723",
                    "low": "0.00013199",
                    "volume": "887054.18",
                    "deal": "119.2565600483"
                },
                "ATNETH": {
                    "period": 86400,
                    "last": "0.00069484",
                    "open": "0.00069776",
                    "close": "0.00069484",
                    "high": "0.00069952",
                    "low": "0.00069449",
                    "volume": "153483.514",
                    "deal": "106.97614821094"
                },
                "TNBETH": {
                    "period": 86400,
                    "last": "0.00010258",
                    "open": "0.00009194",
                    "close": "0.00010258",
                    "high": "0.00010538",
                    "low": "0.00008869",
                    "volume": "761802.93",
                    "deal": "73.4726442434"
                },
            ……
                "GVTETH": {
                    "period": 86400,
                    "last": "0.034525",
                    "open": "0.032989",
                    "close": "0.034525",
                    "high": "0.034567",
                    "low": "0.032878",
                    "volume": "612.44",
                    "deal": "20.60413469"
                }
            }
        """
        return self.get_request('/market.status24h')

    def market_summary(self, markets = '[]'):
        """
            Market summary
            Markets: The market name is json array, such as:
                ["BTCUSD", "BCCUSD"], such as an empty array: [], returns all
                markets.
            ct['Hotbit'].market_summary('["BTCUSD", "ETHUSD"]')
            Response:
            [
                {
                    "name": "BTCUSD",
                    "ask_count": 0,
                    "ask_amount": "0",
                    "bid_count": 0,
                    "bid_amount": "0"
                },
                {
                    "name": "ETHUSD",
                    "ask_count": 2,
                    "ask_amount": "28",
                    "bid_count": 2,
                    "bid_amount": "23"
                }
            }
        """
        return self.get_request('/market.summary?markets={}'.format(markets))

    def get_all_tickers(self):
        """
            Get the latest deals for all market trading pairs
            ct['Hotbit'].get_all_tickers()
            Response:
            [{'buy': '0.00000900',
              'close': '0.00000900',
              'high': '0.00000900',
              'last': '0.00000900',
              'low': '0.00000900',
              'open': '0.00000900',
              'sell': '0.00000900',
              'symbol': 'TVNT_BTC',
              'vol': '100000'},
             {'buy': '0.0000060000',
              'close': '0.0000060000',
              'high': '0.0000060000',
              'last': '0.0000060000',
              'low': '0.0000060000',
              'open': '0.0000060000',
              'sell': '0.0000060000',
              'symbol': 'HTB_ETH',
              'vol': '100000'},
        """
        return self.get_request('/allticker')['ticker']


    def get_markets(self):
        """
            ct['Hotbit'].get_markets()
        """
        return requests.get('https://www.hotbit.io/public/markets').json()['Content']

    ########################################
    ### Exchange specific private methods ##
    ########################################

    def get_balances(self, assets):
        """
            Get user assets
            assets: An array of token symbols, an empty array indicating that
                all token assets are acquired ["BTC","ETH"]
            ct['Hotbit'].get_balances('[]')
            Response:{"error": null, "result": 1520919059}
        """
        return requests.trading_api_request('post', '/balance.query', '&assets={}'.format(assets))

    def get_balance_history(self, asset, business, start_time, end_time, offset, limit):
        """
            Get user funds change flow
            asset: Asset name, such as: "BTC", "ETH", etc., "" means all asset
                names
            business: Business name, such as "deposit" or "trade", "" indicates
                all business names
            start_time: Starting time
            end_time: deadline
            offset: Offset position, if set to 0, means that from the beginning
                of the latest business, all transactions recorded to the
                previous time, the total number of pens cannot be greater than
                limit; If set to 1, it means that the total number of
                transactions from the previous time cannot be greater than the
                limit from the beginning of the new business; and so on.
            limit: The maximum number of transactions returned
            ct['Hotbit'].get_balances('[]')
            Response:{"error": null, "result": 1520919059}
        """
        return requests.trading_api_request('post', '/balance.query',
            '&asset={}&business={}&start_time={}&end_time={}&offset={}&limit={}'.format(
                asset, business, start_time, end_time, offset, limit))

    def submit_limit_trade(self, market, side, amount, price):
        """
            Limit trading
            market: Market name, such as: "BTC/USDT", "ETH/USDT"
            side: 1 = "sell", 2="buy"
            amount: The number of applications for the transaction ( note that
                it must be a multiple of the minimum amount )
            price: Trading price
            ct['Hotbit'].submit_limit_trade('ETH/BTCH',1,10,100)
            Response:
            {
                "error": null,
                "result":
            	 {
            	   "id":8688803,    #order-ID
            	    "market":"ETHBTC",
            	    "source":"web",    #数据请求来源标识
            	    "type":1,	       #下单类型 1-限价单
            	    "side":2,	       #买卖方标识 1-卖方，2-买方
            	    "user":15731,
            	    "ctime":1526971722.164765, #订单创建时间
            	    "mtime":1526971722.164765, #订单更新时间
            	    "price":"0.080003",
            	    "amount":"0.4",
            	    "taker_fee":"0.0025",
            	    "maker_fee":"0",
            	    "left":"0.4",
            	    "deal_stock":"0",
            	    "deal_money":"0",
            	    "deal_fee":"0"
                    },
                "id": 1521169460
            }
        """
        return requests.trading_api_request('post', '/order.put_limit',
            '&market={0}&side={1}&amount={2:.8f}&price={3:.8f}'.format(market, side, amount, price))

    def cancel_order(self, market, order_id):
        """
            cancel the deal
            market: Market name, such as: "BTC/USDT", "ETH/USDT"
            order_id: The id of the transaction to cancel. See the result of the
                "order.put_limit" method.
            ct['Hotbit'].cancel_order('ETH/BTCH',8688803)
            Response:
            {
                "error": null,
                "result":
            	 {
            	   "id":8688803,    #order-ID
            	    "market":"ETHBTC",
            	    "source":"web",    #数据请求来源标识
            	    "type":1,	       #下单类型 1-限价单
            	    "side":2,	       #买卖方标识 1-卖方，2-买方
            	    "user":15731,
            	    "ctime":1526971722.164765, #订单创建时间
            	    "mtime":1526971722.164765, #订单更新时间
            	    "price":"0.080003",
            	    "amount":"0.4",
            	    "taker_fee":"0.0025",
            	    "maker_fee":"0",
            	    "left":"0.4",
            	    "deal_stock":"0",
            	    "deal_money":"0",
            	    "deal_fee":"0"
                    },
                "id": 1521169460
            }
        """
        return requests.trading_api_request('post', '/order.cancel',
            '&market={0}&order_id={1}'.format(market, order_id))

    def cancel_order_batch(self, market, order_ids):
        """
            cancel the deal
            market: Market name, such as: "BTC/USDT", "ETH/USDT"
            order_id: To cancel the id of the transaction, the maximum number of
                orders can be canceled. See the return result of the
                "order.put_limit" method.
            ct['Hotbit'].cancel_order_batch('ETH/BTCH',[1,2])
            Response:
            {
                "error": null,
                "result":
            	 [
                        {#正确反馈
                               "id":8688803,    #order-ID
                                "market":"ETHBTC",
                                "source":"web",    #数据请求来源标识
                                "type":1,	       #下单类型 1-限价单
                                "side":2,	       #买卖方标识 1-卖方，2-买方
                                "user":15731,
                                "ctime":1526971722.164765, #订单创建时间
                                "mtime":1526971722.164765, #订单更新时间
                                "price":"0.080003",
                                "amount":"0.4",
                                "taker_fee":"0.0025",
                                "maker_fee":"0",
                                "left":"0.4",
                                "deal_stock":"0",
                                "deal_money":"0",
                                "deal_fee":"0"
                        },
                        {	#发生错误反馈
                            "error": {
            		   "code":10
            		   "message":"order not found"
            		}
            	  	"result":null,
            	         "id": 1521169460
                        }
                    ],
                "id": 1521169460
            }
        """
        return requests.trading_api_request('post', '/order.batch_cancel',
            '&market={0}&order_id={1}'.format(market, order_ids))

    def order_deals(self, order_id, limit):
        """
            Get the details of the completed order
            Order_id: Transaction ID, see the return result of the "order.put_limit" method
            Offset: Equal to 0, indicating that the previous transaction was searched before
            Limit: Returns the maximum number of "records"
            ct['Hotbit'].order_deals(100, 10)
            Response:
            {
                "error": null,
                "result": {
                    "offset": 10,
                    "limit": 10,
                    "records": [
                        {
                            "time": 1521107411.116817,
                            "user": 15643,
                            "id": 1385154,
                            "role": 1,
                            "price": "0.02",
                            "amount": "0.071",
                            "deal": "0.00142",
                            "fee": "0",
                            "deal_order_id": 2337658
                        },
                        {
                            "time": 1521107410.357024,
                            "user": 15643,
                            "id": 1385151,
                            "role": 1,
                            "price": "0.02",
                            "amount": "0.081",
                            "deal": "0.00162",
                            "fee": "0",
                            "deal_order_id": 2337653
                        }
                    ]
                },
                "id": 1521169460
            }
        """
        return requests.trading_api_request('post', '/order.deals',
            '&order_id={0}&limit={1}'.format(order_id, limit))

    def finished_order_details(self, order_id):
        """
            Query completed orders based on order number
            Order_id: Transaction ID, see the return result of the "order.put_limit" method
            ct['Hotbit'].finished_order_details(100)
            Response:
            {
                "error": null,
                "result": {
                    "id": 1,
                    "ctime": 1535545564.4409361,
                    "ftime": 1535545564.525017,
                    "user": 15731,
                    "market": "YCCETH",
                    "source": "test",
                    "type": 1,
                    "side": 2,
                    "price": "0.0000509",
                    "amount": "1",
                    "taker_fee": "0.001",
                    "maker_fee": "0.001",
                    "deal_stock": "1",
                    "deal_money": "0.0000509",
                    "deal_fee": "0.001"
                },
                "id": 1536050997
            }
        """
        return requests.trading_api_request('post', '/order.finished_detail',
            '&order_id={}'.format(order_id))

    def pending_order(self, market, offset, limit):
        """
            Query unimplemented order
            Market: Market name, such as: "BTC/USDT", "BCC/USDT"
            Offset: Offset position, if set to 0, means that from the beginning
                of the latest business, all transactions recorded to the
                previous time, the total number of pens cannot be greater than
                limit; If set to 1, it means that from the beginning of the new
                business, the total number of transactions in the previous time
                cannot be greater than the limit; and so on.....
            Limit: Returns the maximum number of "records"
            ct['Hotbit'].finished_order_details(100)
            Response:
            {
                "error": null,
                "result": {
                    "id": 1,
                    "ctime": 1535545564.4409361,
                    "ftime": 1535545564.525017,
                    "user": 15731,
                    "market": "YCCETH",
                    "source": "test",
                    "type": 1,
                    "side": 2,
                    "price": "0.0000509",
                    "amount": "1",
                    "taker_fee": "0.001",
                    "maker_fee": "0.001",
                    "deal_stock": "1",
                    "deal_money": "0.0000509",
                    "deal_fee": "0.001"
                },
                "id": 1536050997
            }
        """
        return requests.trading_api_request('post', '/order.pending',
            '&market={}&offset={}&limit={}'.format(market, offset, limit))

    def finished_order(self, market, start_time, end_time, offset, limit, side):
        """
            Query the user's completed order
            Market: Market name, such as: "BTC/USDT", "BCC/USDT"
            Start_time: Starting time
            End_time: deadline
            Offset: Offset position, if set to 0, means that from the beginning
                of the latest business, all transactions recorded to the
                previous time, the total number of pens cannot be greater than
                limit; If set to 1, it means that the total number of
                transactions from the previous time cannot be greater than the
                limit from the beginning of the new business; and so on.
            Limit: Returns the maximum number of "records"
            Side: 1 = "sell", 2="buy"
            ct['Hotbit'].finished_order_details(100)
        """
        return requests.trading_api_request('post', '/order.pending',
            '&market={}&offset={}&limit={}'.format(market, offset, limit))

    def user_transaction_history(self, market, offset, limit):
        """
            Query user transaction history
            Market: Market name, such as: "BTC/USDT", "BCC/USDT"
            Offset: Offset position, if set to 0, means that all transactions
                from the previous time, starting from the latest order, the
                total number of transactions cannot be greater than limit; if
                set to 1, it means counting from the next new order, before All
                of the time meets the conditional order record, the total number
                cannot be greater than the limit; and so on.....
            Limit: Query limit (limit <= 1000)
            ct['Hotbit'].finished_order_details(100)
        """
        return requests.trading_api_request('post', '/market.user_deals',
            '&market={}&offset={}&limit={}'.format(market, offset, limit))

    # #######################
    # ### Generic methods ###
    # #######################
    def load_currencies(self):
        self._currencies = {}
        markets = self.get_markets()
        for market in markets:
            try:
                market_name = market['name']
                coins = market_name.split('/')
                self._currencies[coins[0]] = {
                    'Name': market['coin1Name'],
                    'Enabled': 1
                }
                self._currencies[coins[1]] = {
                    'Name': market['coin2Name'],
                    'Enabled': 1
                }
            except Exception as e:
                self.log_request_error(str(e))

        return self._currencies

    def load_markets(self):
        self._markets = {}
        self._active_markets = {}
        open_trading_symbols = self.get_all_tickers()

        for symbol in open_trading_symbols:
            try:
                market_symbol = symbol['symbol']
                local_base = market_symbol.split('_')[1]
                local_curr = market_symbol.split('_')[0]
                self.update_market( market_symbol,
                                    local_base,
                                    local_curr,
                                    float(symbol['buy']),
                                    float(symbol['sell'])
                                    )
            except Exception as e:
                self.log_request_error(str(market_symbol) + ". " + str(e))
        return self._active_markets

    def load_available_balances(self):
        available_balances = self.get_balances()
        self._available_balances = {}
        for balance in available_balances:
            currency = balance['coinType']
            self._available_balances[currency] = balance["balance"]
        return self._available_balances

    def load_balances_btc(self):
        balances = self.get_balances()
        self._complete_balances_btc = {}
        for balance in balances:
            currency = balance['coinType']
            self._complete_balances_btc[currency] = {
                'Available': float(balance["balance"]),
                'OnOrders': float(balance["freezeBalance"]),
                'Total': float(balance["balance"]) + float(balance["freezeBalance"])
            }
        return self._complete_balances_btc

    def load_order_book(self, market, depth = 5):
        raw_results = self.get_order_book(market, str(depth))
        take_bid = min(depth, len(raw_results['BUY']))
        take_ask = min(depth, len(raw_results['SELL']))

        results = { 'Tradeable': 1, 'Bid': {}, 'Ask': {} }
        for i in range(take_bid):
            results['Bid'][i] = {
                'Price': float(raw_results['BUY'][i][0]),
                'Quantity': float(raw_results['BUY'][i][1]),
            }
        for i in range(take_ask):
            results['Ask'][i] = {
                'Price': float(raw_results['SELL'][i][0]),
                'Quantity': float(raw_results['SELL'][i][1]),
            }

        return results
