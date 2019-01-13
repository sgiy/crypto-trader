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

    def get_request(self, url):
        result = {}
        try:
            result = requests.get(self.BASE_URL + url)
        except Exception as e:
            self.print_exception('ERROR getting URL 1: ' + self.BASE_URL + url + ". " + str(e))
            return self.get_request(url)
        try:
            return result.json()
        except Exception as e:
            self.print_exception('ERROR getting URL 2: ' + self.BASE_URL + url + ". " + str(e))
            print(result)
            return self.get_request(url)

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

    #################################
    ### Exchange specific methods ###
    #################################

    def get_all_currencies(self):
        return self.get_request('public?command=returnCurrencies')

    def get_all_markets(self):
        return self.get_request('public?command=returnTicker')

    def get_balances(self):
        balances = self.trading_api_request("returnBalances")
        return balances

    def get_complete_balances(self):
        balances = self.trading_api_request("returnCompleteBalances",{'account':'all'})
        if balances.get('error', None) is not None:
            self.print_exception(balances.get('error'))
            return self.get_complete_balances()
        else:
            return balances

    def get_order_book(self, market, depth = '5'):
        url = "public?command=returnOrderBook&currencyPair=" + market + "&depth=" + depth
        return self.get_request(url)

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
                    'Enabled': 1 - max(currencies[currency]['delisted'],currencies[currency]['frozen'])
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

                self.update_market(entry, local_base, local_curr, float(all_markets[entry]['highestBid']), float(all_markets[entry]['lowestAsk']), all_markets[entry]['isFrozen'] == '0')
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

        results = { 'Tradeable': 1-float(raw_results['isFrozen']), 'Bid': {}, 'Ask': {} }
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

    def load_ticks(self, market_name, interval, lookback):
        # TODO:
        pass







    # Public API Requests
    def get_all_order_books(self, depth = '5'):
        return self.get_order_book('all', depth)

    # Private API Requests
    def init_fees(self):
        fee_info = self.trading_api_request("returnFeeInfo")
        self._makerFee = float(fee_info['makerFee'])
        self._takerFee = float(fee_info['takerFee'])

    def get_deposits_withdrawals(self):
        return self.trading_api_request("returnDepositsWithdrawals",{'start':'1483142400','end':'9999999999'})
