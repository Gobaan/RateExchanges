import collections
import json
import urllib.parse

import cryptocompare
import googlesearch
import parsers
import utilities

coin_count = collections.Counter(**{
    'OKEx': 222, 'Gate.io': 151, 'HitBTC': 118, 'Liqui': 108, 'Livecoin': 82, 'OpenLedger DEX': 52, 'Huobi': 43,
     'YoBit': 42, 'Bitfinex': 37, 'C-CEX': 34, 'Bittrex': 30, 'Cryptopia': 26, 'Poloniex': 24, 'ZB.COM': 24,
     'Upbit': 24, 'Exrates': 22, 'Kucoin': 19, 'Trade Satoshi': 17, 'Coinbene': 15, 'Exmo': 13, 'EXX': 13, 'AEX': 13,
     'Binance': 12, 'BitShares Asset Exchange': 12, 'SouthXchange': 11, 'Kraken': 10, 'BitFlip': 10, 'WEX': 9,
     'Quoine': 8, 'CEX.IO': 7, 'Bibox': 7, 'Coinut': 7, 'Tidex': 7, 'xBTCe': 6, 'Bitstamp': 5, 'BitBay': 5, 'GDAX': 4,
     'DSX': 4, 'Bitsane': 4, 'BigONE': 4, 'Waves Decentralized Exchange': 4, 'LocalTrade': 4, 'Gatehub': 3,
     'Abucoins': 3, 'BTC-Alpha': 3, 'Lykke Exchange': 3, 'Gemini': 2, 'CoinsBank': 2, 'Bitstamp (Ripple Gateway)': 2,
     'Mr. Exchange': 2, 'Bitlish': 2, 'Bittylicious': 2, 'Coingi': 2, 'NIX-E': 2, 'Gatecoin': 2, 'Ore.Bz': 2, 'BTCC': 1,
     'LakeBTC': 1, 'itBit': 1, 'GetBTC': 1, 'BitMEX': 1, 'bitFlyer': 1, 'Independent Reserve': 1, 'OkCoin Intl.': 1,
     'BitKonan': 1, 'Omni DEX': 1, 'Cobinhood': 1, 'LEOxChange': 1})

market_cap_count = collections.Counter(**{
    'BitMEX': 1115820000, 'Bitfinex': 893217509, 'OKEx': 852615381, 'Binance': 395220130, 'GDAX': 335818600,
     'Huobi': 309909714, 'Bitstamp': 183035940, 'Kraken': 154029176, 'BTCC': 134560000, 'HitBTC': 112302869,
     'ZB.COM': 99620899, 'Gemini': 97199300, 'Poloniex': 95745288, 'Bittrex': 87039763, 'Gate.io': 63728179,
     'Liqui': 39398098, 'LakeBTC': 35415900, 'CoinsBank': 29035660, 'Exmo': 28330909, 'CEX.IO': 25779159,
     'itBit': 23604800, 'WEX': 21933439, 'Livecoin': 20480784, 'Kucoin': 14160563, 'xBTCe': 9937304, 'Quoine': 9297325,
     'GetBTC': 6733320, 'bitFlyer': 5765980, 'BitShares Asset Exchange': 5265111, 'Exrates': 4727140, 'EXX': 3684487,
     'Bibox': 3365227, 'Coinbene': 3003651, 'Upbit': 2844932, 'YoBit': 1969746, 'DSX': 1172189, 'Gatehub': 895163,
    'Cryptopia': 848882, 'Coinut': 380576, 'OkCoin Intl.': 311313, 'Tidex': 92987,
     'Lykke Exchange': 74440, 'OpenLedger DEX': 70701, 'BigONE': 69110, 'Bitsane': 43922,
     'Waves Decentralized Exchange': 37129, 'BTC-Alpha': 29094, 'Mr. Exchange': 23168, 'LocalTrade': 14692,
     'BitFlip': 13616, 'SouthXchange': 13170, 'Independent Reserve': 10060, 'C-CEX': 6288, 'BitBay': 4810,
     'Trade Satoshi': 3700, 'Bitlish': 2615, 'Abucoins': 2567, 'Ore.Bz': 2171, 'AEX': 988, 'BitKonan': 568,
     'Bittylicious': 164, 'Coingi': 58, 'Cobinhood': 54, 'NIX-E': 0, 'Gatecoin': 0, 'Omni DEX': 0, 'LEOxChange': 0})


def fetch_links(exchange_name):
    with googlesearch.GoogleSearch() as searcher:
        query = "%s reviews" % exchange_name
        return searcher.search(query).results


# TODO: count the domains
def count_domain(exchange_name):
    domain_count = collections.Counter()
    for results in fetch_links(exchange_name):
        domain_count.update(set(urllib.parse.urlparse(result.url).netloc for result in results))


if __name__ == "__main__":

    encoder = utilities.get_encoder(cryptocompare.Exchange, cryptocompare.Entry)
    spread = {}
    for name in coin_count:
        links = fetch_links(name)
        reviews = parsers.parse_reviews(links)
        spread[name] = reviews

    with open('sample_crawl.json', 'w') as fp:
        json.dump(spread, fp, cls=encoder, indent=4)

# TODO: Parse a bunch of exchangses and see if we can spread them
# TODO: meta crawl the cryptocompare website
# TODO: Meta crawl blog posts?
# TODO: Meta crawl the original website?
# TODO: Calculate fees, average rating and review keywords
