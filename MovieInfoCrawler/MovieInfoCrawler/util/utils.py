# -*- coding: utf-8 -*-
__author__ = 'Mr.loser'

import hashlib


def get_md5(url):
    h = hashlib.md5()
    h.update(url.encode('utf-8'))
    return h.hexdigest()
