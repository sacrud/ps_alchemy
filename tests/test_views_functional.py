#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2014 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Functional tests for views
"""
from .conftest import User, Group, Tree


def is_table_exist(table_name, engine):
    return engine.dialect.has_table(engine.connect(), table_name)


def user_fixture(dbsession, ids=(1,)):
    for id in ids:
        user = User(id=id, name="some user %s" % id)
        dbsession.add(user)
    dbsession.commit()


class TestHome:

    def test_sa_home(self, functional):
        res = functional.app.get('/admin/', status=200)
        assert 'auth' in str(res.body)
        assert 'user' in str(res.body)
        assert 'goods' in str(res.body)


class TestCreate:

    def test_sa_create(self, functional):
        functional.app.get('/admin/auth/user/create/', status=200)

    def test_sa_create_table_not_exist(self, functional):
        functional.app.get('/admin/not_exist_table/create/', status=404)
        assert is_table_exist('not_exist_table', functional.engine) is False

    def test_sa_create_post(self, functional):
        post = [
            ('form.submitted', '1'),
            ('__formid__', 'deform'),
            ('__start__', ':mapping'),
            ('id', '1'),
            ('name', 'foo bar baz'),
            ('__end__', ':mapping')
        ]
        functional.app.post('/admin/auth/user/create/', post, status=302)
        user = functional.dbsession.query(User)\
            .order_by(User.id.desc()).first()
        assert user.name == 'foo bar baz'

    def test_sa_create_update_none_repr_obj(self, functional):
        post = [
            ('form.submitted', '1'),
            ('__formid__', 'deform'),
            ('__start__', ':mapping'),
            ('name', 'foo'),
            ('__end__', ':mapping')
        ]
        functional.app.post('/admin/Catalouge/groups/create/',
                            post, status=302)
        group = functional.dbsession.query(Group).count()
        assert group > 0

        post = [
            ('form.submitted', '1'),
            ('__formid__', 'deform'),
            ('__start__', ':mapping'),
            ('id', 2),
            ('__end__', ':mapping')
        ]
        functional.app.post('/admin/Catalouge/groups/update/id/1/',
                            post, status=302)
        group = functional.dbsession.query(Group).count()
        assert group > 0

# def test_sa_create_an_existing_obj(self, functional):
#     functional.drop_db()
#     functional.create_db()
#     post = [
#         ('form.submitted', '1'),
#         ('__formid__', 'deform'),
#         ('__start__', ':mapping'),
#         ('id', 1),
#         ('__end__', ':mapping')
#     ]
#     for x in range(10):
#         functional.app.post('/admin/Catalouge/groups/create/',
#                             post, status=302)
#     group = functional.dbsession.query(Group).count()
#     assert group > 0
#     with pytest.raises(IntegrityError):
#         functional.app.post('/admin/Catalouge/groups/create/',
#                             post, status=302)


class TestList:

    def test_sa_list(self, functional):
        functional.app.get('/admin/auth/user/', status=200)
        functional.app.get('/admin/Catalouge/groups/', status=200)

    def test_sa_update(self, functional):
        functional.dbsession.add(
            User(id=1, name='admin')
        )
        functional.dbsession.commit()
        functional.app.get('/admin/auth/user/update/id/1/name/admin',
                           status=200)

    def test_sa_update_not_found(self, functional):
        functional.app.get('/admin/auth/user/update/id/100500/name/foo',
                           status=404)

    def test_sa_update_bad_pk(self, functional):
        functional.app.get('/admin/auth/user/update/', status=404)
        functional.app.get('/admin/auth/user/update/id', status=404)
        functional.app.get('/admin/auth/user/update/not_pk/1', status=404)
        functional.app.get('/admin/auth/user/update/id/1/foo/2', status=404)

    def test_sa_update_table_not_exist(self, functional):
        functional.app.get('/admin/not_exist_table/update/id/100500',
                           status=404)
        assert is_table_exist('not_exist_table', functional.engine) is False

    def test_sa_update_post(self, functional):
        functional.dbsession.add(
            User(id=1, name='no_name')
        )
        functional.dbsession.commit()
        post = [
            ('form.submitted', '1'),
            ('__formid__', 'deform'),
            ('__start__', ':mapping'),
            ('sex', 'male'),
            ('name', 'foo bar baz'),
            ('__end__', ':mapping')
        ]
        functional.app.post('/admin/auth/user/update/id/1/name/no_name',
                            post, status=302)
        user = functional.dbsession.query(User).filter_by(id=1).one()
        assert user.name == 'foo bar baz'

    def test_sa_update_post_bad_data(self, functional):
        functional.dbsession.add(
            User(id=1, name='no_name')
        )
        functional.dbsession.commit()
        post = [
            ('form.submitted', '1'),
            ('__formid__', 'deform'),
            ('__start__', ':mapping'),
            ('id', 111),
            ('age', ''),
            ('sex', 'male'),
            ('name', 'some user 1'),
            ('__end__', ':mapping')
        ]
        functional.app.post('/admin/auth/user/update/id/1/name/no_name',
                            post, status=302)
        user = functional.dbsession.query(User).filter_by(id=111).one()
        assert user.name == 'some user 1'


class TestDelete:

    def test_delete_user(self, functional):
        functional.dbsession.add(
            User(id=1, name='foo')
        )
        functional.dbsession.commit()
        functional.app.post('/admin/auth/user/delete/id/1/name/foo',
                            status=302)
        user = functional.dbsession.query(User).filter_by(id=1).all()
        assert len(user) == 0

    def test_delete_not_found_user(self, functional):
        functional.app.post('/admin/auth/user/delete/id/100500', status=404)
        user = functional.dbsession.query(User).filter_by(id=100500).all()
        assert len(user) == 0

    def test_sa_delete_bad_pk(self, functional):
        functional.dbsession.add(
            User(id=1, name='foo')
        )
        functional.dbsession.commit()
        functional.app.get('/admin/auth/user/delete/', status=404)
        functional.app.get('/admin/auth/user/delete/id', status=404)
        functional.app.get('/admin/auth/user/delete/not_pk/1', status=404)
        functional.app.get('/admin/auth/user/delete/id/1/foo/2', status=404)

    def test_delete_not_exist_table(self, functional):
        functional.app.get('/admin/not_exist_table/delete/id/1', status=404)
        assert is_table_exist('not_exist_table', functional.engine) is False

    def test_sa_list_delete_actions(self, functional):
        ids = range(1, 100)
        user_fixture(functional.dbsession, ids=ids)
        deleted_ids = range(11, 25)
        items_list = [u'["id", %s, "name", "some user %s"]' % (id, id)
                      for id in deleted_ids]
        functional.app.post(
            '/admin/auth/user/mass_action/',
            {'selected_item': items_list, 'mass_action': 'delete'},
            status=302
        )
        count = functional.dbsession.query(User).filter(
            User.id.in_(deleted_ids)
        ).count()
        assert count == 0
        count = functional.dbsession.query(User).filter(
            User.id.in_(ids)
        ).count()
        assert count == len(ids) - len(deleted_ids)

    def test_sa_list_delete_cascade_actions(self, functional):
        functional.dbsession.add(Tree(id=1))
        functional.dbsession.add(Tree(id=2, parent_id=1))
        functional.dbsession.add(Tree(id=3, parent_id=2))
        functional.dbsession.add(Tree(id=4, parent_id=1))
        functional.dbsession.add(Tree(id=5))
        functional.dbsession.commit()

        deleted_ids = (1, 3, 4)
        items_list = [u'["id", %s]' % id for id in deleted_ids]
        functional.app.post(
            '/admin/foo/tree/mass_action/',
            {'selected_item': items_list, 'mass_action': 'delete'},
            status=302
        )
        objects = [x.id for x in functional.dbsession.query(Tree).all()]
        assert 1 not in objects
        assert 2 in objects
        assert 3 not in objects
        assert 4 not in objects
        assert 5 in objects
