# Crypto-Trader

The goal of this project is to create an open, usable interface enabling a more
comfortable simultaneous usage of multiple crypto exchanges, for example, by
showing aggregated balances across exchanges. As an additional benefit (that is
already available), you can monitor arbitrage opportunities across exchanges.

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

The project is currently not ready for release, but you are welcome to try what
is already written (real-time arbitrage checks) and to submit your suggestions.

## Donations are welcome:

**BTC**: 39qHV6AVQMxynRx6kRQVD9R4PrkyQKxPhK

## Current Status of Exchange API implementations

| Exchange | Public REST API | Private REST API | Websockets | Comments |
| -------- | --------------- | ---------------- | ---------- | -------- |
| Binance  | NR              | NR               | NI         | -------- |
| Bittrex  | NR              | NR               | NI         | -------- |
| Hotbit   | NR              | NI               | NI         | -------- |
| Kucoin   | NR              | NR               | NI         | -------- |
| KucoinV2 | Fine            | NR               | NI         | Signing issues with post requests that have 2 or more data parameters |
| Poloniex | Fine            | Fine             | NI         | -------- |

- NR - Needs review (and development)
- NI - Not implemented (yet)
