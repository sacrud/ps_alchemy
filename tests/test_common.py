#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

import colander
import sqlalchemy
from sqlalchemy import Column, String, Integer
from sacrud_deform import SacrudForm
from ps_alchemy.views import preprocessing_value
from sqlalchemy.ext.declarative import declarative_base


def test_preprocessing_value():

    Base = declarative_base()  # noqa

    class User(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        foo = Column(String)
        bar = Column(Integer)

    form = SacrudForm(None, None, User)
    form.make_appstruct()
    assert preprocessing_value("foo", colander.null, form.schema) == ""
    assert preprocessing_value("foo", "", form.schema) == ""
    assert isinstance(
        sqlalchemy.sql.null(),
        type(preprocessing_value("bar", "", form.schema))
    )
    value = {'foo': 'bar'}
    assert preprocessing_value("foo", value, form.schema) == value
    assert preprocessing_value("foo", u"говядо", form.schema) == u"говядо"
    assert preprocessing_value(
        "foo",
        u'\u0433\u043e\u0432\u044f\u0434\u043e', form.schema) == u"говядо"
