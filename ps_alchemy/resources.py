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
from pyramid.location import lineage
from pyramid.threadlocal import get_current_registry

import sqlalchemy
from sacrud.action import CRUD
from sacrud.common import pk_to_list, pk_list_to_dict, get_attrname_by_colname
from sacrud_deform import SacrudForm
from sqlalchemy.orm import sessionmaker, scoped_session
from pyramid_sacrud.interfaces import ISacrudResource


class BaseResource(object):

    breadcrumb = True

    def __init__(
            self, table, dbsession=None, name=None, **kwargs
    ):
        self.table = table
        self.kwargs = kwargs
        self._dbsession = dbsession
        self.__name__ = name or getattr(self, '__name__', None)

    @property
    def verbose_name(self):
        return getattr(self.table, 'verbose_name', self.table.__tablename__)

    @property
    def _columns(self):
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

        return list(Column(col) for col in columns)

    @classmethod
    def _get_id(cls, obj, json=True):
        return pk_to_list(obj, json)

    @property
    def ps_crud(self):
        update = self.get_update_resource
        delete = self.get_delete_resource
        create = self.get_create_resource()
        mass_action = self.get_mass_action_resource()
        return {
            "get_id": self._get_id,
            "columns": self._columns,
            "crud": {
                "mass_action": mass_action,
                "create": create,
                "update": update,
                "delete": delete,
            }
        }

    @property
    def dbsession(self):
        if not self._dbsession:
            self._dbsession = self._default_dbsession
        return self._dbsession

    @dbsession.setter
    def dbsession(self, dbsession):
        self._dbsession = dbsession

    @property
    def _default_dbsession(self):
        registry = get_current_registry()
        engine = sqlalchemy.engine_from_config(registry.settings)
        session = scoped_session(
            sessionmaker(extension=ZopeTransactionExtension())
        )
        session.configure(bind=engine)
        return session

    @property
    def sacrud(self):
        return CRUD(self.dbsession, self.table, commit=False)

    def get_mass_action_resource(self):
        resource = MassActionResource(self.table, self.dbsession)
        resource.__parent__ = self
        return resource

    def get_list_resource(self, resource):
        for context in lineage(resource):
            if isinstance(context, ListResource):
                return context

    def get_create_resource(self):
        resource = CreateResource(self.table, self.dbsession)
        resource.__parent__ = self
        return resource

    def get_update_resource(self, obj=None):
        resource = UpdateResource(self.table, dbsession=self.dbsession)
        resource.__parent__ = self
        if obj:
            pk = pk_to_list(obj)
            for key in pk:
                resource = resource[str(key)]
        return resource

    def get_delete_resource(self, obj=None):
        resource = DeleteResource(self.table, dbsession=self.dbsession)
        resource.__parent__ = self.get_list_resource(self)
        if obj:
            pk = pk_to_list(obj)
            for key in pk:
                resource = resource[str(key)]
        return resource


@implementer(ISacrudResource)
class ListResource(BaseResource):

    title = 'Alchemy view'
    renderer = '/ps_alchemy/crud/list.jinja2'

    def __init__(self, table, dbsession=None):
        self.__name__ = table.__tablename__
        super(ListResource, self).__init__(
            table, dbsession=dbsession
        )

    @property
    def items_per_page(self):
        return int(
            get_current_registry().settings.get(
                'ps_alchemy.items_per_page', 5
            )
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
            resource = self.__class__(self.table, self.dbsession, name)
            resource.__parent__ = self
            return resource
        elif len(primary_key) == pk_len:
            try:
                obj = self.sacrud.read(pk_list_to_dict(primary_key)).one()
            except sqlalchemy.orm.exc.NoResultFound:
                return None
            resource.obj = obj
            resource.__parent__ = self
            return resource


class UpdateResource(PrimaryKeyResource):

    __name__ = 'update'

    def __getitem__(self, name):
        resource = CreateResource(self.table, self.dbsession, name)
        return self._getitem(resource, name)


class DeleteResource(PrimaryKeyResource):

    __name__ = 'delete'

    def __getitem__(self, name):
        resource = DeleteResource(self.table, self.dbsession, name)
        return self._getitem(resource, name)


class MassActionResource(BaseResource):

    __name__ = 'mass_action'
