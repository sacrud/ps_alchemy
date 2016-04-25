import imp
import os

import pytest
from pyramid import testing
from webtest import TestApp
from sqlalchemy import create_engine
from pyramid_sacrud import CONFIG_RESOURCES
from sqlalchemy.orm import sessionmaker, scoped_session
from pyramid.threadlocal import get_current_registry
from sqlalchemy.ext.declarative import declarative_base

imp.load_source('pyramid_sacrud_example', 'example/ps_alchemy_example.py')

from pyramid_sacrud_example import (  # noqa
    Good,
    main,
    Tree,
    User,
    Group,
    models
)

DIRNAME = os.path.dirname(__file__)
DATABASE_FILE = os.path.join(DIRNAME, 'test.sqlite')
TEST_DATABASE_CONNECTION_STRING = 'sqlite:///%s' % DATABASE_FILE

Base = declarative_base()


class BaseFixture:

    def __init__(self):
        engine = create_engine(TEST_DATABASE_CONNECTION_STRING)
        self.engine = engine
        self.DBSession = scoped_session(sessionmaker(bind=self.engine))
        self.dbsession = self.DBSession(bind=self.engine)

    def setUp(self):
        # bind an individual Session to the connection
        self.create_db()

    def tearDown(self):
        self.drop_db()
        os.remove(DATABASE_FILE)
        self.dbsession.close()

    def drop_db(self):
        Base.metadata.drop_all(bind=self.engine)
        User.__table__.drop(self.engine)
        Group.__table__.drop(self.engine)
        Good.__table__.drop(self.engine)
        Tree.__table__.drop(self.engine)
        self.dbsession.commit()

    def create_db(self):
        Base.metadata.create_all(bind=self.engine)
        User.__table__.create(self.engine, checkfirst=True)
        Group.__table__.create(self.engine, checkfirst=True)
        Good.__table__.create(self.engine, checkfirst=True)
        Tree.__table__.create(self.engine, checkfirst=True)
        self.dbsession.commit()


@pytest.fixture(scope="function")
def unit(request):
    response = BaseFixture()
    response.setUp()
    response.request = testing.DummyRequest()
    response.config = testing.setUp(request=response.request)
    get_current_registry().settings[CONFIG_RESOURCES] = models
    get_current_registry().settings['sqlalchemy.url'] =\
        TEST_DATABASE_CONNECTION_STRING

    def fin():
        response.tearDown()
        testing.tearDown()

    request.addfinalizer(fin)
    return response


@pytest.fixture(scope="function")
def functional(request):
    settings = {
        'sqlalchemy.url': TEST_DATABASE_CONNECTION_STRING,
    }
    app = main({}, **settings)
    response = BaseFixture()
    response.setUp()
    response.app = TestApp(app)

    def fin():
        response.tearDown()

    request.addfinalizer(fin)
    return response
