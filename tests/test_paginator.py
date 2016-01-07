#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

from pyramid.testing import DummyRequest
from ps_alchemy.paginator import get_paginator, get_current_page


def test_get_current_page():
    request = DummyRequest()
    page = get_current_page(request)
    assert page == 1
    request.GET['page'] = 5
    page = get_current_page(request)
    assert page == 5


def test_get_paginator():
    request = DummyRequest()
    paginator = get_paginator(request)
    assert paginator['items_per_page'] == 10
    assert paginator['page'] == 1

    request.GET['page'] = 100500
    paginator = get_paginator(request, 20)
    assert paginator['items_per_page'] == 20
    assert paginator['page'] == 100500
