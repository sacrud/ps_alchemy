#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
from pyramid.events import ApplicationCreated
from pyramid_sacrud.routes import resources_preparing_factory
from sqlalchemy.ext.declarative.api import DeclarativeMeta

from .resources import ListResource


def models_preparing(app):
    """ Wrap all sqlalchemy model in settings.
    """

    def wrapper(resource, parent):
        if isinstance(resource, DeclarativeMeta):
            resource = ListResource(resource)
        if not getattr(resource, '__parent__', None):
            resource.__parent__ = parent
        return resource

    resources_preparing_factory(app, wrapper)


def includeme(config):
    config.add_subscriber(models_preparing, ApplicationCreated)

    config.include('ps_crud')
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("templates")
    config.scan('.views')

    # deform
    config.include('sacrud_deform')
    config.add_static_view('deform_static', 'deform:static')
