import collections
from urllib.parse import urlparse

import bs4

import cryptocompare

# Goals: Get ratings, get maker and taker fees. get keywords?
# Prefer blog/studies then reviews
ForexReview = collections.namedtuple(
    "Forex", ['rating', 'fees', 'company', 'pros', 'review_count', 'comments'])


# May be a bit too custom
# !forexbrokers
def parse_forex(result):
    soup = bs4.BeautifulSoup(result.text, 'lxml')
    review = soup.find(class_='center_box borker_box hreview-aggregate')
    children = list(review.children)
    rating_line = [child.text for child in children if 'RATING' in str(child)][0].split('/')
    rating = rating_line[0].split()[-1]
    tables = [str(table) for table in review.find_all("table")]
    fees = tables[0]
    company = tables[1]
    pros = tables[-1]
    review_count = rating_line[1].split()[0]
    comments = [review.text.split('\n') for review in soup.find_all(class_='review')]
    forex_review = ForexReview(rating=rating,
                               fees=fees,
                               company=company,
                               pros=pros,
                               review_count=review_count,
                               comments=comments)
    return forex_review


# !cryptocompare, (only used for exchange info for now)
def parse_cryptocompare(result):
    exchange = cryptocompare.Exchange(result.url)
    exchange.crawl_cryptocompare()
    return exchange


# ? bitcoinexchangeguide: has 403
def parse_bitcoin_exchange(result):
    soup = bs4.BeautifulSoup(result.text, 'lxml')
    try:
        review = soup.find("td-ss-main-content").text
    except AttributeError:
        return "Failed to find content"
    return review


# !reddit.com
def parse_reddit(result):
    soup = bs4.BeautifulSoup(result.text, 'lxml')
    comments = [child.text for child in
                soup.find_all(class_='usertext-body may-blank-within md-container ')]
    return comments


def parse_reviews(search_results):
    parsers = {
        'www.forexbrokerz.com': parse_forex,
        'www.cryptocompare.com': parse_cryptocompare,
        'bitcoinexchangeguide.com': parse_bitcoin_exchange,
        'www.reddit.com': parse_reddit
    }
    reviews = {}
    for result in search_results:
        domain = urlparse(result.url).netloc
        try:
            print(domain)
            reviews[domain] = parsers[domain](result)
        except KeyError:
            pass
    return reviews
