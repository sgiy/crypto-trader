import time
import hmac
import hashlib
import urllib
import requests
import pprint

from Exchange import Exchange

class Poloniex(Exchange):
    def __init__(self, APIKey='', Secret=''):
        super().__init__(APIKey, Secret)
        self.BASE_URL = 'https://poloniex.com/'
        self._precision = 8

    def get_request(self, url):
        try:
            result = requests.get(self.BASE_URL + url)
            return result.json()
        except Exception as e:
            self.print_exception(str(e))
            return {}

    def trading_api_request(self, command, req={}):
        try:
            req['command'] = command
            req['nonce'] = int(time.time()*1000000)
            post_data = urllib.parse.urlencode(req)
            sign = hmac.new(self.Secret.encode(), post_data.encode(), hashlib.sha512).hexdigest()

            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }

            result = requests.post(self.BASE_URL + 'tradingApi', data = req, headers = headers).json()
            if 'error' in result:
                print(result['error'])
                return self.trading_api_request(command, req)
            return result
        except Exception as e:
            self.print_exception(str(e))
            return {}

    ########################################
    ### Exchange specific public methods ###
    ########################################

    def get_all_markets(self):
        """
            Call: https://poloniex.com/public?command=returnTicker
        """
        return self.get_request('public?command=returnTicker')

    def get_all_markets_24h_volume(self):
        """
            Call: https://poloniex.com/public?command=return24hVolume
        """
        return self.get_request('public?command=return24hVolume')

    def get_order_book(self, market, depth = '5'):
        """
            Call: https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_NXT&depth=10
        """
        url = "public?command=returnOrderBook&currencyPair=" + market + "&depth=" + depth
        return self.get_request(url)

    def get_all_order_books(self, market, depth = '5'):
        return self.get_order_book('all',depth)

    def get_trade_history(self, market, start, end):
        """
            Returns the past 200 trades for a given market, or up to 50,000
            trades between a range specified in UNIX timestamps by the "start"
            and "end" GET parameters.

            Call: https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_NXT&start=1410158341&end=1410499372
        """
        url = "public?command=returnTradeHistory&currencyPair=" + market + "&start=" + start + "&end=" + end
        return self.get_request(url)

    def get_chart_data(self, market, start, end, period):
        """
            Returns candlestick chart data. Required GET parameters are
            "currencyPair", "period" (candlestick period in seconds; valid
            values are 300, 900, 1800, 7200, 14400, and 86400), "start", and
            "end". "Start" and "end" are given in UNIX timestamp format and used
            to specify the date range for the data returned.

            Call: https://poloniex.com/public?command=returnChartData&currencyPair=BTC_XMR&start=1405699200&end=9999999999&period=14400
        """
        url = "public?command=returnChartData&currencyPair=" + market + "&start=" + start + "&end=" + end + "&end=" + period
        return self.get_request(url)

    def get_all_currencies(self):
        """
            Returns information about currencies.

            Call: https://poloniex.com/public?command=returnCurrencies
        """
        return self.get_request('public?command=returnCurrencies')

    def get_loan_orders(self, currency):
        """
            Returns the list of loan offers and demands for a given currency,
            specified by the "currency" GET parameter.

            Call: https://poloniex.com/public?command=returnLoanOrders&currency=BTC
        """
        return self.get_request('public?command=returnLoanOrders&currency=' + currency)

    ########################################
    ### Exchange specific private methods ##
    ########################################

    def get_balances(self):
        """
            Returns all of your available balances.
        """
        return self.trading_api_request("returnBalances")

    def get_available_balances(self, account = 'all'):
        """
            Returns your balances sorted by account. You may optionally specify
            the "account" POST parameter if you wish to fetch only the balances
            of one account.
        """
        return self.trading_api_request("returnAvailableAccountBalances",{'account': account})

    def get_complete_balances(self, account = None):
        """
            Returns all of your balances, including available balance, balance
            on orders, and the estimated BTC value of your balance.
        """
        request = {}
        if account is not None:
            request['account'] = account
        return self.trading_api_request("returnCompleteBalances", request)

    def get_deposit_addresses(self):
        """
            Returns all of your available balances.
        """
        return self.trading_api_request("returnDepositAddresses")

    def generate_deposit_address(self, currency):
        """
            Generates a new deposit address for the currency specified by the
            "currency" POST parameter.
        """
        return self.trading_api_request("generateNewAddress",{'currency':currency})

    def get_deposits_and_withdrawals(self, start, end):
        """
            Returns your deposit and withdrawal history within a range,
            specified by the "start" and "end" POST parameters, both of which
            should be given as UNIX timestamps.
        """
        return self.trading_api_request("returnDepositsWithdrawals",{'start':start,'end':end})

    def get_open_orders(self, market):
        """
            Returns your open orders for a given market, specified by the
            "currencyPair" POST parameter, e.g. "BTC_XCP". Set "currencyPair"
            to "all" to return open orders for all markets.
        """
        return self.trading_api_request("returnOpenOrders",{'currencyPair':market})

    def get_all_open_orders(self):
        """
            Returns your open orders for a given market, specified by the
            "currencyPair" POST parameter, e.g. "BTC_XCP". Set "currencyPair" to
            "all" to return open orders for all markets.
        """
        return self.get_open_orders('all')

    def get_private_trade_history(self, market, start, end, limit = '10000'):
        """
            Returns your trade history for a given market, specified by the
            "currencyPair" POST parameter. You may specify "all" as the
            currencyPair to receive your trade history for all markets. You may
            optionally specify a range via "start" and/or "end" POST parameters,
            given in UNIX timestamp format; if you do not specify a range, it
            will be limited to one day. You may optionally limit the number of
            entries returned using the "limit" parameter, up to a maximum of
            10,000. If the "limit" parameter is not specified, no more than 500
            entries will be returned.
        """
        parameters = {
            'currencyPair': market,
            'limit':        limit,
        }
        if start is not None and end is not None:
            parameters['start'] = start
            parameters['end'] = end

        return self.trading_api_request("returnOpenOrders", parameters)

    def get_private_all_trade_history(self, start, end, limit = '10000'):
        return self.get_private_trade_history('all', start, end, limit)

    def get_order_trades(self, orderNumber):
        """
            Returns all trades involving a given order, specified by the
            "orderNumber" POST parameter. If no trades for the order have
            occurred or you specify an order that does not belong to you, you
            will receive an error. See the documentation here for how to use the
            information from returnOrderTrades and returnOrderStatus to
            determine various status information about an order.
        """
        return self.trading_api_request("returnOrderTrades",{'orderNumber':orderNumber})

    def get_order_status(self, orderNumber):
        """
            Returns the status of a given order, specified by the "orderNumber"
            POST parameter. If the specified orderNumber is not open, or it is
            not yours, you will receive an error.
        """
        return self.trading_api_request("returnOrderStatus",{'orderNumber':orderNumber})

    def submit_trade(self, direction, market, price, amount, trade_type):
        request =   {
                        'currencyPair': market,
                        'rate': "{0:.8f}".format(price),
                        'amount': "{0:.8f}".format(amount)
                    }
        if trade_type == 'ImmediateOrCancel':
            request['immediateOrCancel'] = '1'

        results = self.trading_api_request(direction, request)

        amount_traded = 0
        for trade in results['resultingTrades']:
            amount_traded += float(trade['amount'])
        return {
                'Amount': amount_traded,
                'OrderNumber': results['orderNumber']
            }

    def cancel_order(self, orderNumber):
        """
            Cancels an order you have placed in a given market. Required POST
            parameter is "orderNumber". If successful, the method will return:
            {
              "success": 1
            }
        """
        return self.trading_api_request("cancelOrder",{'orderNumber':orderNumber})

    def move_order(self, orderNumber, rate, amount = None):
        """
            Cancels an order and places a new one of the same type in a single
            atomic transaction, meaning either both operations will succeed or
            both will fail. Required POST parameters are "orderNumber" and
            "rate"; you may optionally specify "amount" if you wish to change
            the amount of the new order. "postOnly" or "immediateOrCancel" may
            be specified for exchange orders.
        """
        request =   {
                        'orderNumber': orderNumber,
                        'rate': "{0:.8f}".format(rate)
                    }
        if amount is not None:
            request['amount'] = "{0:.8f}".format(amount)
        return self.trading_api_request("moveOrder", request)

    def withdraw(self, currency, amount, address, paymentId = None):
        """
            Immediately places a withdrawal for a given currency, with no email
            confirmation. In order to use this method, the withdrawal privilege
            must be enabled for your API key. Required POST parameters are
            "currency", "amount", and "address". For XMR withdrawals, you may
            optionally specify "paymentId".
        """
        request =   {
                        'currency': currency,
                        'amount': "{0:.8f}".format(amount),
                        'address': address
                    }
        if paymentId is not None:
            request['paymentId'] = paymentId
        return self.trading_api_request("withdraw", request)

    def get_fees(self):
        """
            If you are enrolled in the maker-taker fee schedule, returns your
            current trading fees and trailing 30-day volume in BTC. This
            information is updated once every 24 hours.
        """
        return self.trading_api_request("returnFeeInfo")

    #######################
    ### Generic methods ###
    #######################
    def load_currencies(self):
        currencies = self.get_all_currencies()
        self._currencies = {}
        for currency in currencies:
            try:
                self._currencies[currency] = {
                    'Name': currencies[currency]['name'],
                    'Enabled': 1 - max( currencies[currency]['delisted'],
                                        currencies[currency]['frozen'])
                }
            except Exception as e:
                self.print_exception(str(e))

        return self._currencies

    def load_markets(self):
        self._markets = {}
        self._active_markets = {}
        all_markets = self.get_all_markets()

        for entry in all_markets:
            try:
                local_base = entry[0:entry.find('_')]
                local_curr = entry[entry.find('_')+1:]

                self.update_market(
                        entry,
                        local_base,
                        local_curr,
                        float(all_markets[entry]['highestBid']),
                        float(all_markets[entry]['lowestAsk']),
                        all_markets[entry]['isFrozen'] == '0'
                    )
            except Exception as e:
                self.print_exception(str(entry) + ". " + str(e))
        return self._active_markets

    def load_available_balances(self):
        available_balances = self.get_balances()
        self._available_balances = {}
        for currency in available_balances:
            self._available_balances[currency] = float(available_balances[currency])
        return self._available_balances

    def load_balances_btc(self):
        balances = self.get_complete_balances()
        self._complete_balances_btc = {}
        for currency in balances:
            self._complete_balances_btc[currency] = {
                'Available': float(balances[currency]['available']),
                'OnOrders': float(balances[currency]['onOrders']),
                'Total': float(balances[currency]['available']) + float(balances[currency]['onOrders']),
                'BtcValue': float(balances[currency]['btcValue'])
            }
        return self._complete_balances_btc

    def load_order_book(self, market, depth = 5):
        raw_results = self.get_order_book(market, str(depth))
        take_bid = min(depth, len(raw_results['bids']))
        take_ask = min(depth, len(raw_results['asks']))

        results = {
            'Tradeable': 1-float(raw_results['isFrozen']),
            'Bid': {},
            'Ask': {}
        }
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

    def load_ticks(self, market_name, interval, lookback):
        # TODO:
        pass
