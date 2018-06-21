# -*- coding: utf-8 -*-
__author__ = 'Mr.loser'

from elasticsearch_dsl import DocType, Text, Keyword, connections, Completion
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
es_connection = connections.create_connection(host='192.168.1.110')


class CustomAnalzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalzer('ik_max_word', filter=['lowercase'])


class MovieInfo(DocType):
    suggest = Completion()
    title = Text(analyzer=ik_analyzer)
    douban_score = Keyword()
    IMDb_score = Keyword()
    age = Keyword()
    introduction = Text(analyzer=ik_analyzer)
    type=Text(analyzer=ik_analyzer)
    url = Keyword()
    front_img_path = Keyword()
    download_url =Keyword()

    class Meta:
        index = 'movie'


if __name__ == '__main__':
    MovieInfo.init()