# -*- coding: utf-8 -*-
import scrapy
import re
from urllib import parse
from MovieInfoCrawler.items import MovieInfoItemLoader, MovieinfocrawlerItem
from MovieInfoCrawler.util.utils import get_md5


class MovieinfoSpider(scrapy.Spider):
    name = 'movieInfo'
    allowed_domains = ['www.dy2018.com']
    start_urls = ['http://www.dy2018.com/', ]

    def parse(self, response):
        all_urls = response.css('a::attr("href")').extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith('https') else False, all_urls)
        for url in all_urls:
            match_obj = re.match(r'.*dy2018.com/i/(\d+.html)$', url)
            if match_obj:
                url = match_obj.group(0)
                yield scrapy.Request(url, callback=self.parse_detail)
                # break
            else:
                yield scrapy.Request(url)

    def parse_detail(self,  response):
        # 提取片名,年代,类别, url. ,封面图, 封面图存储目录, 下载链接(magnet:?xt开头),评分
        # 封面图url
        img_url = response.xpath('//div[@id="Zoom"]/p[1]/img/@src').extract_first('')
        item_loader = MovieInfoItemLoader(item=MovieinfocrawlerItem(), response=response)
        p_list = response.xpath('//p/text()').extract()
        # 过滤空白p标签
        p_list =list( filter(lambda p: True if p.strip() != '' else False, p_list))
        # switch语句??
        for p in p_list:
            # title
            if re.match(r'^(◎译|◎片)', p):
                item_loader.add_value('title', p)
                continue
            # 上映时间
            if re.match(r'^(◎上)', p):
                item_loader.add_value('age', p)
                continue
            # 豆瓣评分
            if re.match(r'^(◎豆)', p):
                douban_score = p.replace('◎', '').replace('\u3000', '').replace('豆瓣评分', '')
                item_loader.add_value('douban_score', douban_score)
                continue
            # IMDb评分
            if re.match(r'^(◎I)', p):
                IMDb_score = p.replace('◎', '').replace('\u3000', '').replace('IMDb评分','')
                item_loader.add_value('IMDb_score', IMDb_score)
                continue
            # 简介
            if re.match(r'^(◎简)', p):
                index = p_list.index(p)
                p = p_list[index+1]
                introduction = p.strip()
                item_loader.add_value('introduction', introduction)
                continue
            #类型
            if re.match(r'^(◎类)', p):
                item_loader.add_value('type', p)
                continue
        # url
        item_loader.add_value('url', response.url)
        # url_obj_id
        item_loader.add_value('url_object_id', get_md5(response.url))
        # 封面图
        item_loader.add_value('front_img_url', img_url)
        # 下载链接
        a_list = response.xpath('//a/text()').extract()
        all_download_url = []
        for download_url in a_list:
            if re.match(r'^((magnet)|(thunder))', download_url):
                download_url = download_url.strip()
                all_download_url.append(download_url)
                item_loader.add_value('download_url', all_download_url)
        movieinfo_item = item_loader.load_item()
        yield movieinfo_item