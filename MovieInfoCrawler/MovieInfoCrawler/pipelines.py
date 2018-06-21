# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline


class MovieinfocrawlerPipeline(object):
    def process_item(self, item, spider):
        item.save_to_es()
        return item


class DownloadImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        front_img_url = item.get('front_img_url','')
        for status, value in results:
            img_path = value['path']
            item['front_img_path'] = img_path
        return item