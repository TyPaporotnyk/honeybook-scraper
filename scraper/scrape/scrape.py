from scrapy.crawler import CrawlerProcess

from scraper.scrape.spiders.notificationspider import NotificationSpider

settings = {
    'LOG_LEVEL': 'INFO',

    'DOWNLOAD_DELAY': 5,

    'FAKEUSERAGENT_PROVIDERS' : [
        'scrapy_fake_useragent.providers.FakeUserAgentProvider',
        'scrapy_fake_useragent.providers.FakerProvider',
        'scrapy_fake_useragent.providers.FixedUserAgentProvider',
    ],

    'USER_AGENT' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',

    'ITEM_PIPELINES': {
       'scraper.scrape.pipelines.connpipeline.ConnPipeline': 300,
    }
}

def parse():
    process = CrawlerProcess(settings=settings)

    process.crawl(NotificationSpider)

    process.start()