import bs4
from urllib.parse import urlparse

# !forexbrokers
# !cryptocompare
# bitcoinexchangeguide
# reddit.com
# bitcointalk.org
# bestbitcoinexchange.com
# Goals: Get ratings, get maker and taker fees. get keywords?
# Prefer blog/studies then reviews

# May be a bit to custom
def parse_forex(soup):
    review = soup.find(class_='center_box borker_box hreview-aggregate')
    children = list(review.children)
    rating_line = [child.text for child in children if 'RATING' in str(child)][0].split('/')
    rating = rating_line[0].split()[-1]
    tables = review.find_all("table")
    fees = tables[0]
    company = tables[1]
    pros = tables[-1]
    review_count = rating_line[1].split()[0]
    comments = [review.text.split('\n') for review in soup.find_all(class_='review')]
    return rating, fees, company, pros, review_count, comments

def parse_cryptocompare(soup):
    print (soup)
    rating = soup.find({"itemprop":"ratingValue"}).text
    review_count = soup.find({"itemprop":"reviewCount"}).text
    review = soup.find_all({"role":"tabpanel"})
    comments = soup.find_all(class_='itempost')
    return rating, review_count, review, comments


def parse_reviews(search_results):
    parsers = {
        #'www.forexbrokerz.com': parse_forex,
        'www.cryptocompare.com': parse_cryptocompare,
    }
    for result in search_results:
        domain = urlparse(result.url).netloc
        try:
            soup = bs4.BeautifulSoup(result.text, 'lxml')
            print (result.url, parsers[domain](soup))
            raise
        except KeyError:
            pass
