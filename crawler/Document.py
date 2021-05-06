class URLDocument:

    def __init__(self, id, url, outgoing_urls=[], html_text=''):
        self.id = id
        self.url = url
        self.outgoing_urls = outgoing_urls
        self.text = html_text
