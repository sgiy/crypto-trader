import requests

class Coinbase:
    def __init__(self, APIKey='', Secret=''):
        self.APIKey = APIKey
        self.Secret = Secret

    def get_request(self, url):
        return requests.get('https://api.gdax.com' + url).json()

    def get_btc_usd_price(self):
        book = self.get_request('/products/BTC-USD/book')
        return (float(book['asks'][0][0]) + float(book['bids'][0][0]))/2
