from zope.interface.verify import verifyClass, verifyObject

from sqlalchemy import Column, Integer
from ps_alchemy.resources import ListResource
from pyramid_sacrud.interfaces import ISacrudResource
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TestModel(Base):
    __tablename__ = 'test_model'

    id = Column(Integer, primary_key=True)


class TestInterface(object):

    def test_verify_list_resource(self):
        verifyClass(ISacrudResource, ListResource)
        verifyObject(ISacrudResource, ListResource(TestModel))
