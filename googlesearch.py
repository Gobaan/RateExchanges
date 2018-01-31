'''
Created on May 5, 2017

@author: anthony
@updated: Gobaan Raveendran
@Description: Updates this library from using urlib to using sessions and caching
'''
import requests_cache
import requests
import urllib.parse
import math
import re
from bs4 import BeautifulSoup
from threading import Thread
from collections import deque
from time import sleep
from datetime import timedelta

expire_after = timedelta(days=7)
requests_cache.install_cache('google_cache', expire_after=expire_after)
class GoogleSearch(object):
    USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/ 58.0.3029.81 Safari/537.36"
    SEARCH_URL = "https://google.com/search"
    RESULT_SELECTOR = ".srg h3.r a"
    TOTAL_SELECTOR = "#resultStats"
    RESULTS_PER_PAGE = 10
    DEFAULT_HEADERS = {
        'user-agent': USER_AGENT,
        'accept-language': 'en-US,en;q=0.5',
    }

    def __init__(self):
        self.session = requests.session()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    # Performs a google search query and fetches the pages that are returned
    def search(self, query, num_results=10, prefetch_pages=True, prefetch_threads=10, language="en"):
        search_results = []
        pages = int(math.ceil(num_results / float(GoogleSearch.RESULTS_PER_PAGE)))
        fetcher_threads = deque([])
        total = None
        for i in range(pages) :
            start = i * GoogleSearch.RESULTS_PER_PAGE
            google_response = self.session.get(GoogleSearch.SEARCH_URL + "?q=" +
                                               urllib.parse.quote(query) + "&hl=" +
                                               language + ("" if start == 0 else ("&start=" + str(start))),
                                               headers=GoogleSearch.DEFAULT_HEADERS)
            soup = BeautifulSoup(google_response.text, "lxml")
            if total is None:
                total_text = next(soup.select(GoogleSearch.TOTAL_SELECTOR)[0].children).encode('utf-8')
                total = int(re.sub("[',\. ]", "", re.search("(([0-9]+[',\. ])*[0-9]+)", str(total_text)).group(1)))

            results = self.parse_results(soup.select(GoogleSearch.RESULT_SELECTOR))
            if len(search_results) + len(results) > num_results:
                del results[num_results - len(search_results):]

            search_results += results
            if prefetch_pages:
                for result in results:
                    while True:
                        running = 0
                        for thread in fetcher_threads:
                            if thread.is_alive():
                                running += 1
                        if running < prefetch_threads:
                            break
                        sleep(1)
                    fetcher_thread = Thread(target=result.get_text)
                    fetcher_thread.start()
                    fetcher_threads.append(fetcher_thread)
        for thread in fetcher_threads:
            thread.join()
        return SearchResponse(search_results, total)
        
    def parse_results(self, results):
        search_results = []
        for result in results:
            url = result["href"]
            title = result.text
            search_results.append(SearchResult(title, url))
        return search_results


class SearchResponse:
    def __init__(self, results, total):
        self.results = results
        self.total = total


class SearchResult:
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.text = None

    def get_text(self):
        if self.text is None:
            response = requests.get(self.url)
            self.text = response.text
        return self.text
    
    def __str__(self):
        return  str(self.__dict__)

    def __unicode__(self):
        return unicode(self.__str__())

    def __repr__(self):
        return self.__str__()

if __name__ == "__main__":
    import sys
    with GoogleSearch() as search:
        print (search)
        query = " ".join(sys.argv[1:])
        if not len(query):
            query = "python"
        count = 10
        print ("Fetching first " + str(count) + " results for \"" + query + "\"...")
        response = search.search(query, count)
        print ("TOTAL: " + str(response.total) + " RESULTS")
        for idx, search_result in enumerate(response.results):
            print("RESULT #" + str(idx) + ": " + search_result.url)
