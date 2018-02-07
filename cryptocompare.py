import collections
import os.path
import re
import time

import browsermobproxy
import selenium.webdriver


class Exchange(object):
    def __init__(self, url):
        self.url = url
        self.entries = None

    # TODO: Leave this connection open and allow refreshing
    def crawl_cryptocompare(self):
        path_to_bin = os.path.join(
            'C:\\', 'Users', 'Gobi', 'Downloads', 'browsermob-proxy-2.1.4', 'bin', 'browsermob-proxy')
        server = browsermobproxy.Server(path_to_bin)
        server.start()
        proxy = server.create_proxy()
        options = selenium.webdriver.ChromeOptions()
        options.add_argument('--proxy-server=%s' % proxy.proxy)
        driver = selenium.webdriver.Chrome(chrome_options=options)
        proxy.new_har(options={'captureHeaders': True, 'captureContent': True, 'captureBinaryContent': True})
        driver.get(self.url)
        proxy.wait_for_traffic_to_stop(1, 10)
        entries = (Entry(entry) for entry in proxy.har['log']['entries']
                   if 'streamer' in entry['request']['url'])
        time.sleep(10)
        driver.close()
        self.entries = [entry for entry in entries if entry.trades]

    def compare(self, other_exchange):
        pass

    def __repr__(self):
        return "<Exchange %s>" % self.entries


class Entry(object):
    trade_re = re.compile('\[(.*?)\]', re.DOTALL)

    def __init__(self, entry):
        self.entry = entry
        self.trades = None
        if self.starts_with_number():
            self.parse_trades()

    def starts_with_number(self):
        try:
            text = self.entry['response']['content']['text']
            return text and text[0].isnumeric()
        except KeyError:
            return False

    @staticmethod
    def parse_trade(frame):
        data = frame.split('~')
        try:
            rate = float(data[5])
            coin = data[2]
            base = data[3]
            coins = (coin, base)
            if base < coin:
                coins = (base, coin)
                rate = 1.0 / rate
            trade = Trade(exchange=data[1],
                          coins=coins,
                          rate=rate,
                          net_worth=data[10])
        except IndexError:
            return None
        except ValueError:
            print(data)
            raise
        return trade

    def parse_trades(self):
        text = self.entry['response']['content']['text']
        trades = Entry.trade_re.findall(text)
        trades = [Entry.parse_trade(trade) for trade in trades]
        self.trades = [trade for trade in trades if trade]

    def __repr__(self):
        return "<Entry trades:%s>" % self.trades


Trade = collections.namedtuple("Trade", ['exchange', 'coins', 'rate', 'net_worth'])

if __name__ == '__main__':
    url = "https://www.cryptocompare.com/exchanges/okex/overview"
    exchange = Exchange(url)
    exchange.crawl_cryptocompare()
