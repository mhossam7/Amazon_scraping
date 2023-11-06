import json
import scrapy
from urllib.parse import urljoin
import re
from amazon.items import AmazonItem


class AmazonSearchProductSpider(scrapy.Spider):
    name = "amazon_search_product"

    def start_requests(self):
        keyword_list = ['laptops']
        for keyword in keyword_list:
            amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page=1'
            yield scrapy.Request(url=amazon_search_url, callback=self.discover_product_urls,
                                 meta={'keyword': keyword, 'page': 1})

    def discover_product_urls(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword']

        ## Discover Product URLs
        search_products = response.css("div.s-result-item[data-component-type=s-search-result]")
        for product in search_products:
            relative_url = product.css("h2>a::attr(href)").get()
            product_url = urljoin('https://www.amazon.com', relative_url)
            yield scrapy.Request(url=product_url, callback=self.parse_product_data,
                                 meta={'keyword': keyword, 'page': page})

        ## Get All Pages
        if page == 1:
            available_pages = response.xpath(
                '//*[contains(@class, "s-pagination-item")][not(has-class("s-pagination-separator"))]/text()'
            ).getall()

            last_page = available_pages[-1]
            for page_num in range(2, int(last_page)):
                amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page={page_num}'
                yield scrapy.Request(url=amazon_search_url, callback=self.discover_product_urls,
                                     meta={'keyword': keyword, 'page': page_num})

    def parse_product_data(self, response):
        image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", response.text)[0])
        variant_data = re.findall(r'dimensionValuesDisplayData"\s*:\s* ({.+?}),\n', response.text)
        feature_bullets = [bullet.strip() for bullet in response.css("#feature-bullets li ::text").getall()]
        price = response.xpath('//div[@class="a-section"]//span[@aria-hidden="true"]//*[@class = "a-price-symbol"]/text()').getall()
        Amazon_Item = AmazonItem()

        if len(price) == 3:

            price = response.css('.a-price .a-offscreen ::text').get("")

            Amazon_Item["url"] = response.url
            Amazon_Item["name"] = response.css("#productTitle::text").get("").strip()
            Amazon_Item["price"] = price
            Amazon_Item["stars"] = response.css("i[data-hook=average-star-rating] ::text").get("")
            Amazon_Item["Rating"] = response.xpath('//*[@id = "acrCustomerReviewText"]//text()').get("")
            Amazon_Item["feature_bullets"] = feature_bullets
            Amazon_Item["images"] = image_data
            Amazon_Item["variant_data"] = variant_data

            yield Amazon_Item

