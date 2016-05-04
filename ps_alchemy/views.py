import json
import logging

import deform
import colander
import peppercorn
import sqlalchemy
import transaction
from pyramid.view import view_config, view_defaults
from sacrud.common import pk_list_to_dict
from pyramid.compat import escape, text_type
from pyramid_sacrud import PYRAMID_SACRUD_VIEW
from pyramid.renderers import render_to_response
from sqlalchemy.orm.exc import NoResultFound
from paginate_sqlalchemy import SqlalchemyOrmPage
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid_sacrud.exceptions import SacrudException
from pyramid_sacrud.localization import _ps

from .paginator import get_paginator
from .resources import (
    ListResource,
    CreateResource,
    DeleteResource,
    MassActionResource
)


def preprocessing_value(key, value, form):
    for groups in form.children:
        for column in groups:
            if column.name == key:
                if not text_type(value).isdigit() and isinstance(
                        column.typ,
                        (colander.Int, colander.Integer,
                         colander.Float, colander.Decimal)):
                    value = sqlalchemy.sql.null()
                elif value is colander.null:
                    value = ""
                return value


@view_defaults(permission=PYRAMID_SACRUD_VIEW)
class CRUD(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def commit(self):
        try:
            self.context.dbsession.commit()
        except AssertionError:
            transaction.commit()

    def abort(self):
        try:
            self.context.dbsession.rollback()
        except AssertionError:
            transaction.abort()

    def list_view_response(self):
        return HTTPFound(
            location='/' + self.request.sacrud_prefix + '/' +
            self.request.resource_path(
                self.context.get_list_resource(self.context)
            )
        )

    def flash_message(self, message, status="success"):
        if hasattr(self.request, 'session'):
            self.request.session.flash([message, status])


class Read(CRUD):

    @view_config(
        request_method='GET',
        context=ListResource,
        route_name=PYRAMID_SACRUD_VIEW,
    )
    def list_view(self):
        rows = self.context.sacrud.read()
        try:
            paginator_attr = get_paginator(
                self.request, self.context.items_per_page
            )
        except ValueError:
            raise HTTPNotFound
        params = {
            'paginator': SqlalchemyOrmPage(rows, **paginator_attr)
        }
        return render_to_response(
            self.context.renderer, params, request=self.request
        )


class Create(CRUD):

    @view_config(
        request_method='GET',
        context=CreateResource,
        route_name=PYRAMID_SACRUD_VIEW
    )
    def edit_form_get_view(self):
        params = {'form': self.context.form(self.request).render()}
        return render_to_response(
            self.context.renderer, params, request=self.request
        )

    @view_config(
        request_method='POST',
        context=CreateResource,
        route_name=PYRAMID_SACRUD_VIEW
    )
    def edit_form_post_view(self):
        form = self.context.form(self.request)
        params = {'form': form.render()}

        def get_reponse(form=None):
            if form:
                params['form'] = form
            return render_to_response(
                self.context.renderer, params, request=self.request
            )

        if 'form.submitted' in self.request.params:
            controls = self.request.POST.items()
            pstruct = peppercorn.parse(controls)

            # Validate form
            try:
                deserialized = form.validate_pstruct(pstruct).values()
            except deform.ValidationFailure as e:
                return get_reponse(e.render())
            data = {k: preprocessing_value(k, v, form)  # TODO: optimize it
                    for d in deserialized
                    for k, v in d.items()}

            # Update object
            try:
                if self.context.obj:
                    obj = self.context.sacrud._add(self.context.obj, data)
                    flash_action = 'updated'
                else:
                    obj = self.context.sacrud.create(data)
                    flash_action = 'created'
                name = obj.__repr__()
                self.context.dbsession.flush()
            except SacrudException as e:
                self.flash_message(e.message, status=e.status)
                return get_reponse()
            except Exception as e:
                self.abort()
                logging.exception("Something awful happened!")
                raise e

            self.commit()

            # Make response
            self.flash_message(_ps(
                u"You ${action} object of ${name}",
                mapping={'action': flash_action, 'name': escape(name or '')}
            ))
            return self.list_view_response()
        return get_reponse()


class Delete(CRUD):

    @view_config(
        request_method='POST',
        context=DeleteResource,
        route_name=PYRAMID_SACRUD_VIEW
    )
    def delete_view(self):
        if not hasattr(self.context, 'obj'):
            raise HTTPNotFound
        self.context.dbsession.delete(self.context.obj)
        self.commit()
        self.flash_message(
            _ps("You have removed object of ${name}",
                mapping={'name': escape(text_type(self.context.obj) or '')}))
        return self.list_view_response()

    @view_config(
        request_method='POST',
        context=MassActionResource,
        request_param='mass_action=delete',
        route_name=PYRAMID_SACRUD_VIEW
    )
    def mass_delete_view(self):
        items_list = self.request.POST.getall('selected_item')
        primary_keys = [pk_list_to_dict(json.loads(item))
                        for item in items_list]
        objects = self.context.sacrud.read(*primary_keys)
        try:
            if hasattr(objects, 'delete'):
                object_names = [escape(x.__repr__() or '') for x in objects]
                objects.delete()
            else:
                object_names = [escape(objects.__repr__() or ''), ]
                self.request.dbsession.delete(objects)
        except (NoResultFound, KeyError):
            raise HTTPNotFound
        except SacrudException as e:
            self.flash_message(e.message, status=e.status)
        except Exception as e:
            transaction.abort()
            logging.exception("Something awful happened!")
            raise e
        transaction.commit()
        self.flash_message(_ps("You delete the following objects:"))
        [self.flash_message(obj) for obj in object_names]
        return self.list_view_response()
