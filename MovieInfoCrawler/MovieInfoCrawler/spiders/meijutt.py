# -*- coding: utf-8 -*-
import scrapy
import re
from urllib import parse
from MovieInfoCrawler.items import MovieInfoItemLoader, MeijuttItem
from MovieInfoCrawler.util.utils import get_md5

class MeijuttSpider(scrapy.Spider):
    name = 'meijutt'
    allowed_domains = ['www.meijutt.com']
    start_urls = ['http://www.meijutt.com/']

    def parse(self, response):
        all_urls = response.css('a::attr("href")').extract()
        # 过滤掉不是本站的url
        all_urls = filter(lambda x: False if x.startswith('http') or x.startswith('https') else True, all_urls)
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        for url in all_urls:
            match_obj = re.match(r'.*?content/(meiju\d+.html)$', url)
            if match_obj:
                url = match_obj.group(0)
                yield scrapy.Request(url, callback=self.parse_detail)
                break
            # else:
            #     yield scrapy.Request(url)

    def parse_detail(self, response):
        item_loader = MovieInfoItemLoader(item=MeijuttItem(), response=response)
        item_loader.add_xpath('title', '//div[@class="info-title"]/h1/text()')
        item_loader.add_xpath('type', '//div[@class="o_r_contact"]/ul/li[last()]/label[last()]/text()')
        item_loader.add_xpath('introduction', '//div[@class="des_box"]/div/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_xpath('age', '//div[@class="o_r_contact"]/ul/li[7]/text()')
        item_loader.add_xpath('front_img_url', '//div[@class="o_big_img_bg_b"]/img/@src')
        item_loader.add_css('download_url', '.current-tab  .down_part_name a::attr("href")')
        item = item_loader.load_item()
        yield  item
        pass