import json
import re

import scrapy


class ArticleSpider(scrapy.Spider):
    name = 'article'
    allowed_domains = ['martinfowler.com']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open('../article_headers.json') as f:
            self.raw_articles = {article['link']: article for article in json.load(f)}

    def start_requests(self):
        yield from [scrapy.Request(url=article['link'], callback=self.parse)
                    for article in self.raw_articles.values() if article['internal'] and not article['video']]

    def parse(self, response, **kwargs):
        yield {
            'name': (self.extract_name(response)),
            'link': response.url[:-1] if response.url.endswith('/') else response.url,
            'date': self.extract_date(response),
            'tags': (self.extract_tags(response)),
            'authors': self.extract_authors(response)
        }

    @staticmethod
    def extract_date(response):
        if response.url.endswith('pdf'):
            return ''
        return response.css('p.date::text').get() or response.css('p.year::text').get() or response.css(
            'p.pubDate::text').get()

    @staticmethod
    def extract_authors(response):
        if response.url.endswith('pdf'):
            return ['Martin Fowler']
        authors = response.css('address.name > a') or response.css(
            'div.author > p.name > a') or response.css('a[rel="author"]') or response.css('p.authors')
        raw_authors = [author.css('::text').get() for author in authors]
        if len(raw_authors) == 1:
            return [author.strip() for author in re.split(r'by|,|and', raw_authors[0]) if author.strip() != ""]
        return raw_authors

    def extract_name(self, response):
        if response.url.endswith('pdf'):
            return self.raw_articles.get(response.url, {'name':  ''})['name']
        return response.css('article > h1 > a::text').get() or response.css('h1::text').get()

    @staticmethod
    def extract_tags(response):
        if response.url.endswith('pdf'):
            return ''
        return [article.css('::text').get() for article in response.css('div.tags > p.tag-link > a')]
