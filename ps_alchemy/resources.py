#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Provide SQLAlchemy resource for pyramid_sacrud.
"""
from zope.interface import implementer
from zope.sqlalchemy import ZopeTransactionExtension

import sqlalchemy
from sacrud.action import CRUD
from sacrud.common import pk_to_list, pk_list_to_dict, get_attrname_by_colname
from sacrud_deform import SacrudForm
from sqlalchemy.orm import sessionmaker, scoped_session
from pyramid.location import lineage
from pyramid.threadlocal import get_current_registry
from pyramid_sacrud.interfaces import ISacrudResource


class BaseResource(object):

    breadcrumb = True

    def __init__(
            self, table, parent=None, dbsession=None, name=None, **kwargs
    ):
        self.table = table
        self.kwargs = kwargs
        self.parent = parent
        self._dbsession = dbsession
        self.__name__ = name or getattr(self, '__name__', None)

    @property
    def table_name(self):
        return self.table.__tablename__

    @property
    def verbose_name(self):
        return getattr(self.table, 'verbose_name', self.table_name)

    @property
    def visible_columns(self):
        columns = getattr(self.table, 'sacrud_list_col',
                          self.table.__table__.c)

        class Column(object):
            def __init__(self, column):
                self.column = column

            def value(self, row):
                return getattr(
                    row,
                    get_attrname_by_colname(row, self.column.name)
                )

            @property
            def name(self):
                return getattr(self.column.info, 'verbose_name',
                               self.column.name)

        return (Column(col) for col in columns)

    @classmethod
    def get_pk(cls, obj, json=True):
        return pk_to_list(obj, json)

    @property
    def __parent__(self):
        return self.parent

    @property
    def dbsession(self):
        return self._dbsession or self._default_dbsession

    @dbsession.setter
    def dbsession(self, dbsession):
        self._dbsession = dbsession

    @property
    def _default_dbsession(self):
        engine = sqlalchemy.engine_from_config(get_current_registry().settings)
        DBSession = scoped_session(
            sessionmaker(extension=ZopeTransactionExtension())
        )
        DBSession.configure(bind=engine)
        return DBSession

    @property
    def crud(self):
        return CRUD(self.dbsession, self.table, commit=False)

    def get_list_resource(self, resource):
        for context in lineage(resource):
            if isinstance(context, ListResource):
                return context

    def get_create_resource(self):
        return CreateResource(self.table, self, self.dbsession)

    def get_update_resource(self, obj=None):
        resource = UpdateResource(
            self.table, parent=self, dbsession=self.dbsession)
        if obj:
            pk = pk_to_list(obj)
            for key in pk:
                resource = resource[str(key)]
        return resource

    def get_delete_resource(self, obj=None):
        resource = DeleteResource(
            self.table, parent=self.get_list_resource(self),
            dbsession=self.dbsession
        )
        if obj:
            pk = pk_to_list(obj)
            for key in pk:
                resource = resource[str(key)]
        return resource

    def get_mass_action_resource(self):
        return MassActionResource(self.table, self, self.dbsession)

    @property
    def left_sibling_breadcrumb(self):
        for resource in lineage(self):
            if resource.breadcrumb and resource is not self:
                return resource


@implementer(ISacrudResource)
class ListResource(BaseResource):

    title = 'Alchemy view'
    items_per_page = 5
    renderer = '/ps_alchemy/crud/list.jinja2'

    def __init__(self, table, parent=None, dbsession=None):
        self.__name__ = table.__tablename__
        super(ListResource, self).__init__(
            table, parent=parent, dbsession=dbsession
        )

    def __getitem__(self, name):
        if name == 'create':
            return self.get_create_resource()
        elif name == 'update':
            return self.get_update_resource()
        elif name == 'delete':
            return self.get_delete_resource()
        elif name == 'mass_action':
            return self.get_mass_action_resource()


class CreateResource(BaseResource):

    _obj = None
    _form = None
    title = 'Alchemy create'
    __name__ = 'create'
    renderer = '/ps_alchemy/crud/create.jinja2'

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, obj):
        self._obj = obj
        self.form = SacrudForm(
            obj=self._obj, dbsession=self.dbsession, table=self.table
        )

    @property
    def form(self):
        return self._form or SacrudForm(
            obj=self._obj, dbsession=self.dbsession, table=self.table
        )

    @form.setter
    def form(self, form):
        self._form = form


class PrimaryKeyResource(BaseResource):

    breadcrumb = False

    def get_primary_key(self):
        return list(reversed([
            x.__name__ for x in lineage(self)
            if isinstance(x, PrimaryKeyResource) and
            x.__name__ not in ['update', 'delete']
        ]))

    def _getitem(self, resource, name):
        primary_key = self.get_primary_key()
        primary_key.append(name)
        pk_len = len(self.table.__table__.primary_key) * 2
        if len(primary_key) < pk_len:
            return self.__class__(self.table, self, self.dbsession, name)
        elif len(primary_key) == pk_len:
            try:
                obj = self.crud.read(pk_list_to_dict(primary_key)).one()
            except sqlalchemy.orm.exc.NoResultFound:
                return None
            resource.obj = obj
            return resource


class UpdateResource(PrimaryKeyResource):

    __name__ = 'update'

    def __getitem__(self, name):
        resource = CreateResource(self.table, self, self.dbsession, name)
        return self._getitem(resource, name)


class DeleteResource(PrimaryKeyResource):

    __name__ = 'delete'

    def __getitem__(self, name):
        resource = DeleteResource(self.table, self, self.dbsession, name)
        return self._getitem(resource, name)


class MassActionResource(BaseResource):

    __name__ = 'mass_action'
    breadcrumb = False

    def __getitem__(self, name):
        if name == 'delete':
            return MassDeleteResource(self.table, self, self.dbsession, name)


class MassDeleteResource(BaseResource):

    __name__ = 'delete'
    breadcrumb = False
