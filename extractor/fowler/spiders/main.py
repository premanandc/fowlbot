import scrapy


class FowlerSpider(scrapy.Spider):
    name = 'fowler'
    allowed_domains = ['martinfowler.com']
    start_urls = ['https://martinfowler.com/tags/']

    def parse(self, response, **kwargs):
        for article in response.css('div.title-list > p > a'):
            link: str = article.css('a').attrib['href']
            full_link_url = f'https://{FowlerSpider.allowed_domains[0]}{link}' if link.startswith('/') else link
            internal = full_link_url.startswith('https://martinfowler.com')
            video = 'videos.html' in full_link_url
            html = full_link_url.endswith('html')
            yield {
                'name': article.css('::text').get(),
                'link': full_link_url[:-1] if full_link_url.endswith('/') else full_link_url,
                'internal': internal,
                'html': html and not video,
                'video': video
            }

