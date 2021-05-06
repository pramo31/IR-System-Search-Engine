import scrapy

from scrapy.crawler import CrawlerProcess
from utils.Utils import *
from crawler.Parser import HtmlParser
from crawler.Document import URLDocument


class CustomCrawler(CrawlerProcess):

    def __init__(self, settings=None, install_root_handler=True):
        super().__init__(settings, install_root_handler)

    def crawl(self, crawler_or_spidercls, *args, **kwargs):
        super().crawl(crawler_or_spidercls, *args, **kwargs)


class UICSpider(scrapy.Spider):

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.start_urls = [url for url in kwargs['start_url']]
        self.allowed_domains = kwargs['allowed_domains']
        self.crawled_documents = kwargs['url_documents']
        self.crawl_limit = kwargs['crawl_limit']
        self.url_idx = 0
        self.visited = set([http_secure_url(canonicalize_url(url)) for url in self.start_urls])
        super().__init__(name, **kwargs)

    def parse(self, response):
        if (self.url_idx % 250 == 0):
            print(f"Processed {self.url_idx} documents")

        headers = response.headers['Content-Type'].decode('utf-8')
        response_url = http_secure_url(canonicalize_url(response.url))

        if response_url not in self.crawled_documents and 'text/html' in headers and \
                pattern_match(response_url, r'^https', r'.*uic.edu.*') \
                and pattern_not_match(response_url,
                                      r'.*(docs\.google\.com|login\.uic\.edu|login\.uillinois\.edu|uofi\.account\.box\.com|print=).*',
                                      r'^.*[.](xlsx|docx|gif|doc|xls|jpeg|mp3|png|jpg|pdf)$'):
            try:
                html_parser = HtmlParser(response.text)
                print(f"Response URL {response_url} of Id {self.url_idx}")
                outgoing_urls = html_parser.get_all_outgoing_urls(fetch_base_url(response_url))
                self.crawled_documents[response_url] = URLDocument(self.url_idx, response_url,
                                                                   list(outgoing_urls.keys()),
                                                                   html_parser.get_all_text())
                self.url_idx += 1

                to_crawl_links = []
                for canonicalized_link, actual_link in outgoing_urls.items():
                    if canonicalized_link in self.visited or len(self.crawled_documents) >= self.crawl_limit:
                        continue
                    self.visited.add(canonicalized_link)
                    to_crawl_links.append(actual_link)
                # print(f"Outgoing Non Repeating URL's: {len(to_crawl_links)}")
                # print(f"PageRank URL's: {outgoing_urls}")
                # print()
                yield from response.follow_all(to_crawl_links, callback=self.parse)
            except AttributeError as ae:
                print(f"Ignoring as Not HTML content: {response_url}")


def run_spider(start_url, allowed_domains, name, crawl_limit, settings):
    process = CustomCrawler(settings)
    url_documents = {}
    print('Crawling')
    process.crawl(UICSpider, name, start_url=start_url, allowed_domains=allowed_domains, url_documents=url_documents,
                  crawl_limit=crawl_limit)
    process.start()
    print(f"Crawled {len(url_documents)} pages")
    # print(url_documents)
    return url_documents
