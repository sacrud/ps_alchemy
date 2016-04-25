#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Tests of views
"""
import imp
from collections import OrderedDict

from ps_alchemy.views import Read, Create
from ps_alchemy.resources import (
    ListResource,
    CreateResource,
    UpdateResource
)
from pyramid.httpexceptions import HTTPFound

from .conftest import User

imp.load_source('pyramid_sacrud_example', 'example/ps_alchemy_example.py')

from pyramid_sacrud_example import add_fixtures  # noqa


class TestList:

    def test_empty_user_table(self, unit):
        context = ListResource(User)
        context.renderer = 'json'
        response = Read(context, unit.request).list_view()
        assert response.json['paginator'] == []

    def test_non_empty_user_table(self, unit):
        add_fixtures(unit.dbsession)
        context = ListResource(User)
        context.renderer = 'json'
        response = Read(context, unit.request).list_view()
        assert response.json['paginator'] == [
            {'name': 'admin'},
            {'name': 'moderator'},
            {'name': 'user1'},
            {'name': 'user2'}
        ]


class TestCreate(object):

    def test_create_get_form(self, unit):
        context = CreateResource(User)
        context.renderer = 'json'
        response = Create(context, unit.request).edit_form_get_view()
        assert len(response.json['form']) > 0

    def test_create_user_form(self, unit):
        unit.drop_db()
        unit.create_db()
        context = CreateResource(User)
        post = [
            ('form.submitted', '1'),
            ('__formid__', 'deform'),
            ('__start__', ':mapping'),
            ('id', '1'),
            ('name', 'foo bar baz'),
            ('__end__', ':mapping')
        ]
        unit.request.POST = OrderedDict(post)
        unit.request.params = OrderedDict(post)
        unit.request.sacrud_prefix = 'sacrud'
        context.renderer = 'json'
        response = Create(context, unit.request).edit_form_post_view()
        assert isinstance(response, HTTPFound)
        user = unit.dbsession.query(User).filter_by(id=1).first()
        assert user.id == 1
        assert user.name == 'foo bar baz'


class UpdateTests(object):

    def test_update_user_form(self, unit):
        context = UpdateResource(User)
        context.renderer = 'json'
        response = Create(context, unit.request).edit_form_get_view()
        assert len(response.json['form']) > 0
