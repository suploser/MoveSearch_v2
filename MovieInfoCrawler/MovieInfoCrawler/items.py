# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from  MovieInfoCrawler.models.movieModel import MovieInfo, es_connection
import redis
redis_cli = redis.StrictRedis(host='192.168.1.109', password='123456qx')


def gen_suggest(index, info):
    used_words = set()
    suggest = []
    for text, weight in info:
        if text:
            words = es_connection.indices.analyze(index=index, body=text, params={'analyzer':'ik_max_word', 'filter':['lowercase']})
            analyzed_words = set([word['token'] for word in words['tokens'] if len(word['token']) > 1])
            new_words = analyzed_words-used_words
            # 去除重复建议词
            if len(new_words) > 0:
                used_words = set(list(set(new_words))+list(set(used_words)))
        if new_words:
            suggest.append({'input': list(new_words), 'weight':weight})
    return suggest


def remove_o(value):
    value = value.replace('◎', '').replace('\u3000', '')
    return value


def get_clean_title(value):
    # 正则替换
    value = re.sub(r'(片|译)名',  '',  value).split('/')
    return value


def get_clean_age(value):
    return value.replace('上映日期','')


def get_clean_type(value):
    value = value.replace('类别', '')
    return value.strip()


def do_nothing(values):
    return values


class MovieInfoItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class MovieinfocrawlerItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(remove_o, get_clean_title),
    )
    introduction = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    type = scrapy.Field(
        input_processor=MapCompose(remove_o, get_clean_type)
    )
    age = scrapy.Field(
        input_processor=MapCompose(remove_o, get_clean_age)
    )
    front_img_url = scrapy.Field(
        output_processor=do_nothing
    )
    front_img_path = scrapy.Field()
    douban_score = scrapy.Field()
    IMDb_score = scrapy.Field()
    download_url = scrapy.Field(
      output_processor=do_nothing
    )

    def save_to_es(self):
        dy_2018 = MovieInfo()
        dy_2018.title = self.get('title','')
        dy_2018.type = self.get('type','')
        dy_2018.url = self.get('url')
        dy_2018.introduction = self.get('introduction', '无介绍')
        dy_2018.age = self.get('age','未知')
        dy_2018.douban_score = self.get('douban_score', '该站暂未提供评分')
        dy_2018.IMDb_score = self.get('IMDb_score', '该站暂未提供评分')
        dy_2018.front_img_path = self.get('front_img_path')
        dy_2018.download_url = self.get('download_url', '暂无下载链接')
        dy_2018.meta.id = self.get('url_object_id')
        dy_2018.suggest = gen_suggest(MovieInfo._doc_type.index, ((dy_2018.title, 10), (dy_2018.type, 8),))
        dy_2018.save()
        redis_cli.incr('movie_count')


def remove_blank(value):
    return value.strip()


class MeijuttItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    type = scrapy.Field()
    introduction = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_blank)
    )
    age = scrapy.Field()
    front_img_url = scrapy.Field( )
    front_img_path = scrapy.Field()
    download_url = scrapy.Field(
        output_processor=do_nothing
    )