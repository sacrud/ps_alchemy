#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.
from pyramid.events import ApplicationCreated
from pyramid_sacrud import CONFIG_MODELS
from pyramid_sacrud.resources import GroupResource
from sqlalchemy.ext.declarative.api import DeclarativeMeta

from .resources import ListResource


def models_preparing(app):
    """ Wrap all sqlalchemy model in settings.
    """
    settings = app.app.registry.settings
    models = settings[CONFIG_MODELS]

    def wrapper(resource, parent):
        if isinstance(resource, DeclarativeMeta):
            return ListResource(resource, parent=parent)
        return resource

    models = [(k, [wrapper(r, GroupResource(k, v)) for r in v])
              for k, v in models]
    settings[CONFIG_MODELS] = models


def includeme(config):
    config.add_subscriber(models_preparing, ApplicationCreated)

    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("templates")
    config.add_static_view('/static', 'ps_alchemy:static')
    config.scan('.views')

    # deform
    config.include('sacrud_deform')
    config.add_static_view('deform_static', 'deform:static')
