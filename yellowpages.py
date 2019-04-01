import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.crawler import CrawlerProcess
import requests
import re
import MySQLdb
import os
from lxml import html
from w3lib.html import remove_tags, remove_tags_with_content
import time
import pickle
from functions import createCsv, readFiles, createFolders
import random
from urllib import parse
import sys


class MySpider(scrapy.Spider):
    name = "yellowpages"
    site = "https://www.yellowpages.com"

    custom_settings = {
        'LOG_LEVEL': 'INFO',
        # 'LOG_ENABLED': 'False',
        'CONCURRENT_REQUESTS': '32',
        'CONCURRENT_REQUESTS_PER_DOMAIN': '32',
    }
    searchPrefix = "/search"

    def __init__(self, vertical, location):
        self.vertical = vertical
        self.location = location
        self.data = []
        self.records_scraped = 0

    def start_requests(self):
        print("Vertical: %s, Location: %s" % (self.vertical, self.location))
        data = {"geo_location_terms": self.location,
                "search_terms": self.vertical}

        url = self.site + "%s?" % self.searchPrefix + parse.urlencode(data)
        yield scrapy.Request(url, callback=self.parse_items)

    def parse_items(self, response):
        urls = response.xpath(
            "//div[@class='scrollable-pane']//div[contains(@class, 'srp-listing')]/div[@class='v-card']/*[@class='info']/h2/a/@href").extract()

        for url in urls:
            if "http" not in url:
                url = self.site + url
                yield scrapy.Request(url, callback=self.parse_item)

        pagination = response.xpath(
            "//a[contains(@class, 'next')]/@href").extract()
        if pagination:
            yield scrapy.Request(self.site + pagination[0], callback=self.parse_items)

    def parse_item(self, response):
        # Info scraped

        scrapedUrl = response.url

        telNumber = response.xpath(
            "//p[@class='phone']/text()").extract() or ["Empty"]

        website = response.xpath(
            "//a[contains(@class, 'website-link')]/@href").extract() or ["Empty"]

        email = response.xpath(
            "//a[@class='email-business']/@href").extract() or ["Empty"]

        name = response.xpath(
            "//div[@class='sales-info']/h1/text()").extract() or ["Empty"]

        facebookUrl = ['empty']

        city, state = self.location.split(",")
        city = [city]
        state = [state]

        zipNumber = response.xpath(
            "//p[@class='address']/span[4]/text()").extract() or ["Empty"]

        scraped = list(map(lambda x: x[0], [
            name, website, facebookUrl, email, telNumber, city, state, zipNumber]))

        scraped.append(scrapedUrl)
        print(self.records_scraped)
        self.records_scraped += 1
        self.data.append(scraped)

    def closed(self, reason):
        print("processing data")
        try:
            with open("./listDump/%s_%s" % (self.vertical, self.location), "wb") as fp:
                pickle.dump(self.data, fp)
        except Exception as e:
            print(e)
            pass
        createCsv(self.data, self.vertical, self.location)


def main(vertical, location):
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    })
    process.crawl(MySpider, vertical, location)
    process.start()


if __name__ == "__main__":
    location = sys.argv[1]
    vertical = sys.argv[2]
    main(vertical, location)
