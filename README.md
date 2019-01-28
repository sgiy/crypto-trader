# Crypto-Trader

The goal of this project is to create an open, usable interface enabling a more
comfortable simultaneous usage of multiple crypto exchanges, for example, by
showing aggregated balances across exchanges. As an additional benefit (that is
already available), you can monitor arbitrage opportunities across exchanges.
This project and information obtained using it does not constitute an investment
advise. Use at your own risk.

Using the GUI for trading on exchanges requires user to create API keys for
those exchanges and to input them in program's configuration. The source code of
the program has to be open to enable user code audit to make sure that the api
keys and the secrets are used only in the manner specified by the relevant
exchange and are not accessible to third parties. If you do not plan to use the
GUI to submit withdrawal requests, then is recommended that the exchange API
keys are created with access only to trading. Additionally, it is recommended
limiting api access to user's ip address if possible in exchange account - this
provides additional protection to the funds. API keys can be supplied in the
main config.py file (in the root folder), or in a separate config_private.py
file (this file is not distributed and is supposed to be your personal file with
the syntax matching config.py). It is recommended to maintain your keys or other
personal settings, like window size, in config_private.py, since then you will
not overwrite them when pulling in latest code).

The project is not yet ready for release, but you are welcome to use what is
already written and to submit your suggestions.

## If you like the project, please consider participating and/or donating:

**BTC**: 39qHV6AVQMxynRx6kRQVD9R4PrkyQKxPhK

## Currently implemented views:
- Balances - Shows aggregate balances in BTC and USD terms across exchanges.
- ExchangeArbitrage - Shows realtime cross exchange arbitrage opportunities
    (Cross exchange arbitrage represents cases when an offer of a pair on one
    exchange at a lower price than a bid on another exchange).
- ExchangeArbitrageCircle - Shows realtime circle arbitrage opportunities (
    Circle arbitrage represents cases where on the same exchange one can
    buy currency2 for currency1, then buy currency3 with this
    currency2, then sell currency3 for currency1 in a way that in the end they
    have more currency1 than they had before these trades).
- ViewTwoExchangeOrderBooks - Allows to see order books from two exchanges in
    the same window. This is useful for investigating cross exchange arbitrage
    opportunities.

## Current Status of Exchange API Wrappers

| Exchange | Public REST API | Private REST API | Websockets | Comments |
| -------- | --------------- | ---------------- | ---------- | -------- |
| Binance  | Good            | Good             | NI         | -------- |
| Bittrex  | Good            | Good             | NI         | -------- |
| Hotbit   | Good            | NA               | NI         | -------- |
| Kucoin   | Good            | Good             | NI         | -------- |
| Poloniex | Good            | Good             | NI         | -------- |

- NR - Needs review (and development)
- NI - Not implemented (yet)
- NA - Not Available. Exchange does not have specific API (e.g. websockets)
