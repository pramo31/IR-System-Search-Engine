from bs4 import BeautifulSoup
from utils.Utils import *


class HtmlParser:

    def __init__(self, html_doc):
        self.soup = BeautifulSoup(html_doc, 'html.parser')

    def get_all_text(self):
        text = self.soup.get_text()
        text = re.sub('\n', ' ', text)
        text = re.sub('\s+', ' ', text)
        return text

    def get_all_outgoing_urls(self, cur_url):
        urls = {}
        links = self.soup.find_all('a')
        for link in links:
            url = link.get('href')
            if url:
                url = re.sub(r'\s', '', url)
                if re.match(r'^[#]', url):
                    continue
                if re.match(r'^[/.]', url):
                    url = cur_url + url
                url = defrag_url(url)
                if is_valid_crawlable(url, r'^https', r'.*uic.edu.*',
                                      r'^(?!.*[.](xlsx|docx|gif|doc|xls|jpeg|mp3|png|jpg|pdf)$).*$',
                                      r'^((?!(print=|login\.uic\.edu|login\.uillinois\.edu)).)*$'):
                    urls[http_secure_url(canonicalize_url(url))] = url
        return urls
