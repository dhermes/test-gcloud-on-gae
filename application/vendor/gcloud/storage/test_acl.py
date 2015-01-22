import unittest2


class Test_ACLEntity(unittest2.TestCase):

    def _getTargetClass(self):
        from gcloud.storage.acl import _ACLEntity
        return _ACLEntity

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor_default_identifier(self):
        TYPE = 'type'
        entity = self._makeOne(TYPE)
        self.assertEqual(entity.type, TYPE)
        self.assertEqual(entity.identifier, None)
        self.assertEqual(entity.get_roles(), set())

    def test_ctor_explicit_identifier(self):
        TYPE = 'type'
        ID = 'id'
        entity = self._makeOne(TYPE, ID)
        self.assertEqual(entity.type, TYPE)
        self.assertEqual(entity.identifier, ID)
        self.assertEqual(entity.get_roles(), set())

    def test___str__no_identifier(self):
        TYPE = 'type'
        entity = self._makeOne(TYPE)
        self.assertEqual(str(entity), TYPE)

    def test___str__w_identifier(self):
        TYPE = 'type'
        ID = 'id'
        entity = self._makeOne(TYPE, ID)
        self.assertEqual(str(entity), '%s-%s' % (TYPE, ID))

    def test_grant_simple(self):
        TYPE = 'type'
        ROLE = 'role'
        entity = self._makeOne(TYPE)
        found = entity.grant(ROLE)
        self.assertTrue(found is entity)
        self.assertEqual(entity.get_roles(), set([ROLE]))

    def test_grant_duplicate(self):
        TYPE = 'type'
        ROLE1 = 'role1'
        ROLE2 = 'role2'
        entity = self._makeOne(TYPE)
        entity.grant(ROLE1)
        entity.grant(ROLE2)
        entity.grant(ROLE1)
        self.assertEqual(entity.get_roles(), set([ROLE1, ROLE2]))

    def test_revoke_miss(self):
        TYPE = 'type'
        ROLE = 'nonesuch'
        entity = self._makeOne(TYPE)
        found = entity.revoke(ROLE)
        self.assertTrue(found is entity)
        self.assertEqual(entity.get_roles(), set())

    def test_revoke_hit(self):
        TYPE = 'type'
        ROLE1 = 'role1'
        ROLE2 = 'role2'
        entity = self._makeOne(TYPE)
        entity.grant(ROLE1)
        entity.grant(ROLE2)
        entity.revoke(ROLE1)
        self.assertEqual(entity.get_roles(), set([ROLE2]))

    def test_grant_read(self):
        TYPE = 'type'
        entity = self._makeOne(TYPE)
        entity.grant_read()
        self.assertEqual(entity.get_roles(), set([entity.READER_ROLE]))

    def test_grant_write(self):
        TYPE = 'type'
        entity = self._makeOne(TYPE)
        entity.grant_write()
        self.assertEqual(entity.get_roles(), set([entity.WRITER_ROLE]))

    def test_grant_owner(self):
        TYPE = 'type'
        entity = self._makeOne(TYPE)
        entity.grant_owner()
        self.assertEqual(entity.get_roles(), set([entity.OWNER_ROLE]))

    def test_revoke_read(self):
        TYPE = 'type'
        entity = self._makeOne(TYPE)
        entity.grant(entity.READER_ROLE)
        entity.revoke_read()
        self.assertEqual(entity.get_roles(), set())

    def test_revoke_write(self):
        TYPE = 'type'
        entity = self._makeOne(TYPE)
        entity.grant(entity.WRITER_ROLE)
        entity.revoke_write()
        self.assertEqual(entity.get_roles(), set())

    def test_revoke_owner(self):
        TYPE = 'type'
        entity = self._makeOne(TYPE)
        entity.grant(entity.OWNER_ROLE)
        entity.revoke_owner()
        self.assertEqual(entity.get_roles(), set())


class Test_ACL(unittest2.TestCase):

    def _getTargetClass(self):
        from gcloud.storage.acl import ACL
        return ACL

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        acl = self._makeOne()
        self.assertEqual(acl.entities, {})
        self.assertFalse(acl.loaded)

    def test__ensure_loaded(self):
        acl = self._makeOne()

        def _reload():
            acl._really_loaded = True

        acl.reload = _reload
        acl._ensure_loaded()
        self.assertTrue(acl._really_loaded)

    def test_reset(self):
        TYPE = 'type'
        ID = 'id'
        acl = self._makeOne()
        acl.loaded = True
        acl.entity(TYPE, ID)
        acl.reset()
        self.assertEqual(acl.entities, {})
        self.assertFalse(acl.loaded)

    def test___iter___empty_eager(self):
        acl = self._makeOne()
        acl.loaded = True
        self.assertEqual(list(acl), [])

    def test___iter___empty_lazy(self):
        acl = self._makeOne()

        def _reload():
            acl.loaded = True

        acl.reload = _reload
        self.assertEqual(list(acl), [])
        self.assertTrue(acl.loaded)

    def test___iter___non_empty_no_roles(self):
        TYPE = 'type'
        ID = 'id'
        acl = self._makeOne()
        acl.loaded = True
        acl.entity(TYPE, ID)
        self.assertEqual(list(acl), [])

    def test___iter___non_empty_w_roles(self):
        TYPE = 'type'
        ID = 'id'
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.entity(TYPE, ID)
        entity.grant(ROLE)
        self.assertEqual(list(acl),
                         [{'entity': '%s-%s' % (TYPE, ID), 'role': ROLE}])

    def test___iter___non_empty_w_empty_role(self):
        TYPE = 'type'
        ID = 'id'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.entity(TYPE, ID)
        entity.grant('')
        self.assertEqual(list(acl), [])

    def test_entity_from_dict_allUsers_eager(self):
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.entity_from_dict({'entity': 'allUsers', 'role': ROLE})
        self.assertEqual(entity.type, 'allUsers')
        self.assertEqual(entity.identifier, None)
        self.assertEqual(entity.get_roles(), set([ROLE]))
        self.assertEqual(list(acl),
                         [{'entity': 'allUsers', 'role': ROLE}])
        self.assertEqual(list(acl.get_entities()), [entity])

    def test_entity_from_dict_allAuthenticatedUsers(self):
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.entity_from_dict({'entity': 'allAuthenticatedUsers',
                                       'role': ROLE})
        self.assertEqual(entity.type, 'allAuthenticatedUsers')
        self.assertEqual(entity.identifier, None)
        self.assertEqual(entity.get_roles(), set([ROLE]))
        self.assertEqual(list(acl),
                         [{'entity': 'allAuthenticatedUsers', 'role': ROLE}])
        self.assertEqual(list(acl.get_entities()), [entity])

    def test_entity_from_dict_string_w_hyphen(self):
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.entity_from_dict({'entity': 'type-id', 'role': ROLE})
        self.assertEqual(entity.type, 'type')
        self.assertEqual(entity.identifier, 'id')
        self.assertEqual(entity.get_roles(), set([ROLE]))
        self.assertEqual(list(acl),
                         [{'entity': 'type-id', 'role': ROLE}])
        self.assertEqual(list(acl.get_entities()), [entity])

    def test_entity_from_dict_string_wo_hyphen(self):
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        self.assertRaises(ValueError,
                          acl.entity_from_dict,
                          {'entity': 'bogus', 'role': ROLE})
        self.assertEqual(list(acl.get_entities()), [])

    def test_has_entity_miss_str_eager(self):
        acl = self._makeOne()
        acl.loaded = True
        self.assertFalse(acl.has_entity('nonesuch'))

    def test_has_entity_miss_str_lazy(self):
        acl = self._makeOne()

        def _reload():
            acl.loaded = True

        acl.reload = _reload
        self.assertFalse(acl.has_entity('nonesuch'))
        self.assertTrue(acl.loaded)

    def test_has_entity_miss_entity(self):
        from gcloud.storage.acl import _ACLEntity
        TYPE = 'type'
        ID = 'id'
        entity = _ACLEntity(TYPE, ID)
        acl = self._makeOne()
        acl.loaded = True
        self.assertFalse(acl.has_entity(entity))

    def test_has_entity_hit_str(self):
        TYPE = 'type'
        ID = 'id'
        acl = self._makeOne()
        acl.loaded = True
        acl.entity(TYPE, ID)
        self.assertTrue(acl.has_entity('%s-%s' % (TYPE, ID)))

    def test_has_entity_hit_entity(self):
        TYPE = 'type'
        ID = 'id'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.entity(TYPE, ID)
        self.assertTrue(acl.has_entity(entity))

    def test_get_entity_miss_str_no_default_eager(self):
        acl = self._makeOne()
        acl.loaded = True
        self.assertEqual(acl.get_entity('nonesuch'), None)

    def test_get_entity_miss_str_no_default_lazy(self):
        acl = self._makeOne()

        def _reload():
            acl.loaded = True

        acl.reload = _reload
        self.assertEqual(acl.get_entity('nonesuch'), None)
        self.assertTrue(acl.loaded)

    def test_get_entity_miss_entity_no_default(self):
        from gcloud.storage.acl import _ACLEntity
        TYPE = 'type'
        ID = 'id'
        entity = _ACLEntity(TYPE, ID)
        acl = self._makeOne()
        acl.loaded = True
        self.assertEqual(acl.get_entity(entity), None)

    def test_get_entity_miss_str_w_default(self):
        DEFAULT = object()
        acl = self._makeOne()
        acl.loaded = True
        self.assertTrue(acl.get_entity('nonesuch', DEFAULT) is DEFAULT)

    def test_get_entity_miss_entity_w_default(self):
        from gcloud.storage.acl import _ACLEntity
        DEFAULT = object()
        TYPE = 'type'
        ID = 'id'
        entity = _ACLEntity(TYPE, ID)
        acl = self._makeOne()
        acl.loaded = True
        self.assertTrue(acl.get_entity(entity, DEFAULT) is DEFAULT)

    def test_get_entity_hit_str(self):
        TYPE = 'type'
        ID = 'id'
        acl = self._makeOne()
        acl.loaded = True
        acl.entity(TYPE, ID)
        self.assertTrue(acl.has_entity('%s-%s' % (TYPE, ID)))

    def test_get_entity_hit_entity(self):
        TYPE = 'type'
        ID = 'id'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.entity(TYPE, ID)
        self.assertTrue(acl.has_entity(entity))

    def test_add_entity_miss_eager(self):
        from gcloud.storage.acl import _ACLEntity
        TYPE = 'type'
        ID = 'id'
        ROLE = 'role'
        entity = _ACLEntity(TYPE, ID)
        entity.grant(ROLE)
        acl = self._makeOne()
        acl.loaded = True
        acl.add_entity(entity)
        self.assertTrue(acl.loaded)
        self.assertEqual(list(acl),
                         [{'entity': 'type-id', 'role': ROLE}])
        self.assertEqual(list(acl.get_entities()), [entity])

    def test_add_entity_miss_lazy(self):
        from gcloud.storage.acl import _ACLEntity
        TYPE = 'type'
        ID = 'id'
        ROLE = 'role'
        entity = _ACLEntity(TYPE, ID)
        entity.grant(ROLE)
        acl = self._makeOne()

        def _reload():
            acl.loaded = True

        acl.reload = _reload
        acl.add_entity(entity)
        self.assertTrue(acl.loaded)
        self.assertEqual(list(acl),
                         [{'entity': 'type-id', 'role': ROLE}])
        self.assertEqual(list(acl.get_entities()), [entity])
        self.assertTrue(acl.loaded)

    def test_add_entity_hit(self):
        from gcloud.storage.acl import _ACLEntity
        TYPE = 'type'
        ID = 'id'
        KEY = '%s-%s' % (TYPE, ID)
        ROLE = 'role'
        entity = _ACLEntity(TYPE, ID)
        entity.grant(ROLE)
        acl = self._makeOne()
        acl.loaded = True
        before = acl.entity(TYPE, ID)
        acl.add_entity(entity)
        self.assertTrue(acl.loaded)
        self.assertFalse(acl.get_entity(KEY) is before)
        self.assertTrue(acl.get_entity(KEY) is entity)
        self.assertEqual(list(acl),
                         [{'entity': 'type-id', 'role': ROLE}])
        self.assertEqual(list(acl.get_entities()), [entity])

    def test_entity_miss(self):
        TYPE = 'type'
        ID = 'id'
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.entity(TYPE, ID)
        self.assertTrue(acl.loaded)
        entity.grant(ROLE)
        self.assertEqual(list(acl),
                         [{'entity': 'type-id', 'role': ROLE}])
        self.assertEqual(list(acl.get_entities()), [entity])

    def test_entity_hit(self):
        TYPE = 'type'
        ID = 'id'
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        before = acl.entity(TYPE, ID)
        before.grant(ROLE)
        entity = acl.entity(TYPE, ID)
        self.assertTrue(entity is before)
        self.assertEqual(list(acl),
                         [{'entity': 'type-id', 'role': ROLE}])
        self.assertEqual(list(acl.get_entities()), [entity])

    def test_user(self):
        ID = 'id'
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.user(ID)
        entity.grant(ROLE)
        self.assertEqual(entity.type, 'user')
        self.assertEqual(entity.identifier, ID)
        self.assertEqual(list(acl),
                         [{'entity': 'user-%s' % ID, 'role': ROLE}])

    def test_group(self):
        ID = 'id'
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.group(ID)
        entity.grant(ROLE)
        self.assertEqual(entity.type, 'group')
        self.assertEqual(entity.identifier, ID)
        self.assertEqual(list(acl),
                         [{'entity': 'group-%s' % ID, 'role': ROLE}])

    def test_domain(self):
        ID = 'id'
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.domain(ID)
        entity.grant(ROLE)
        self.assertEqual(entity.type, 'domain')
        self.assertEqual(entity.identifier, ID)
        self.assertEqual(list(acl),
                         [{'entity': 'domain-%s' % ID, 'role': ROLE}])

    def test_all(self):
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.all()
        entity.grant(ROLE)
        self.assertEqual(entity.type, 'allUsers')
        self.assertEqual(entity.identifier, None)
        self.assertEqual(list(acl),
                         [{'entity': 'allUsers', 'role': ROLE}])

    def test_all_authenticated(self):
        ROLE = 'role'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.all_authenticated()
        entity.grant(ROLE)
        self.assertEqual(entity.type, 'allAuthenticatedUsers')
        self.assertEqual(entity.identifier, None)
        self.assertEqual(list(acl),
                         [{'entity': 'allAuthenticatedUsers', 'role': ROLE}])

    def test_get_entities_empty_eager(self):
        acl = self._makeOne()
        acl.loaded = True
        self.assertEqual(acl.get_entities(), [])

    def test_get_entities_empty_lazy(self):
        acl = self._makeOne()

        def _reload():
            acl.loaded = True

        acl.reload = _reload
        self.assertEqual(acl.get_entities(), [])
        self.assertTrue(acl.loaded)

    def test_get_entities_nonempty(self):
        TYPE = 'type'
        ID = 'id'
        acl = self._makeOne()
        acl.loaded = True
        entity = acl.entity(TYPE, ID)
        self.assertEqual(acl.get_entities(), [entity])

    def test_reload_raises_NotImplementedError(self):
        acl = self._makeOne()
        self.assertRaises(NotImplementedError, acl.reload)

    def test_save_raises_NotImplementedError(self):
        acl = self._makeOne()
        self.assertRaises(NotImplementedError, acl.save)

    def test_clear(self):
        acl = self._makeOne()
        self.assertRaises(NotImplementedError, acl.clear)


class Test_BucketACL(unittest2.TestCase):

    def _getTargetClass(self):
        from gcloud.storage.acl import BucketACL
        return BucketACL

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        bucket = object()
        acl = self._makeOne(bucket)
        self.assertEqual(acl.entities, {})
        self.assertFalse(acl.loaded)
        self.assertTrue(acl.bucket is bucket)

    def test_reload_eager_empty(self):
        NAME = 'name'
        ROLE = 'role'
        connection = _Connection({'items': []})
        bucket = _Bucket(connection, NAME)
        acl = self._makeOne(bucket)
        acl.loaded = True
        acl.entity('allUsers', ROLE)
        self.assertTrue(acl.reload() is acl)
        self.assertEqual(list(acl), [])
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'GET')
        self.assertEqual(kw[0]['path'], '/b/%s/acl' % NAME)

    def test_reload_eager_nonempty(self):
        NAME = 'name'
        ROLE = 'role'
        connection = _Connection(
            {'items': [{'entity': 'allUsers', 'role': ROLE}]})
        bucket = _Bucket(connection, NAME)
        acl = self._makeOne(bucket)
        acl.loaded = True
        self.assertTrue(acl.reload() is acl)
        self.assertEqual(list(acl), [{'entity': 'allUsers', 'role': ROLE}])
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'GET')
        self.assertEqual(kw[0]['path'], '/b/%s/acl' % NAME)

    def test_reload_lazy(self):
        NAME = 'name'
        ROLE = 'role'
        connection = _Connection(
            {'items': [{'entity': 'allUsers', 'role': ROLE}]})
        bucket = _Bucket(connection, NAME)
        acl = self._makeOne(bucket)
        self.assertTrue(acl.reload() is acl)
        self.assertEqual(list(acl), [{'entity': 'allUsers', 'role': ROLE}])
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'GET')
        self.assertEqual(kw[0]['path'], '/b/%s/acl' % NAME)

    def test_save_none_set_none_passed(self):
        NAME = 'name'
        connection = _Connection()
        bucket = _Bucket(connection, NAME)
        acl = self._makeOne(bucket)
        self.assertTrue(acl.save() is acl)
        kw = connection._requested
        self.assertEqual(len(kw), 0)

    def test_save_no_arg(self):
        NAME = 'name'
        ROLE = 'role'
        AFTER = [{'entity': 'allUsers', 'role': ROLE}]
        connection = _Connection({'acl': AFTER})
        bucket = _Bucket(connection, NAME)
        acl = self._makeOne(bucket)
        acl.loaded = True
        acl.entity('allUsers').grant(ROLE)
        self.assertTrue(acl.save() is acl)
        self.assertEqual(list(acl), AFTER)
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[0]['data'], {'acl': AFTER})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})

    def test_save_w_arg(self):
        NAME = 'name'
        ROLE1 = 'role1'
        ROLE2 = 'role2'
        STICKY = {'entity': 'allUsers', 'role': ROLE2}
        new_acl = [{'entity': 'allUsers', 'role': ROLE1}]
        connection = _Connection({'acl': [STICKY] + new_acl})
        bucket = _Bucket(connection, NAME)
        acl = self._makeOne(bucket)
        acl.loaded = True
        self.assertTrue(acl.save(new_acl) is acl)
        entries = list(acl)
        self.assertEqual(len(entries), 2)
        self.assertTrue(STICKY in entries)
        self.assertTrue(new_acl[0] in entries)
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[0]['data'], {'acl': new_acl})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})

    def test_clear(self):
        NAME = 'name'
        ROLE1 = 'role1'
        ROLE2 = 'role2'
        STICKY = {'entity': 'allUsers', 'role': ROLE2}
        connection = _Connection({'acl': [STICKY]})
        bucket = _Bucket(connection, NAME)
        acl = self._makeOne(bucket)
        acl.loaded = True
        acl.entity('allUsers', ROLE1)
        self.assertTrue(acl.clear() is acl)
        self.assertEqual(list(acl), [STICKY])
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/%s' % NAME)
        self.assertEqual(kw[0]['data'], {'acl': []})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})


class Test_ObjectACL(unittest2.TestCase):

    def _getTargetClass(self):
        from gcloud.storage.acl import ObjectACL
        return ObjectACL

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_ctor(self):
        key = object()
        acl = self._makeOne(key)
        self.assertEqual(acl.entities, {})
        self.assertFalse(acl.loaded)
        self.assertTrue(acl.key is key)

    def test_reload_eager_empty(self):
        NAME = 'name'
        KEY = 'key'
        ROLE = 'role'
        after = {'items': [{'entity': 'allUsers', 'role': ROLE}]}
        connection = _Connection(after)
        bucket = _Bucket(connection, NAME)
        key = _Key(bucket, KEY)
        acl = self._makeOne(key)
        acl.loaded = True
        self.assertTrue(acl.reload() is acl)
        self.assertEqual(list(acl), after['items'])
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'GET')
        self.assertEqual(kw[0]['path'], '/b/name/o/%s/acl' % KEY)

    def test_reload_eager_nonempty(self):
        NAME = 'name'
        KEY = 'key'
        ROLE = 'role'
        after = {'items': []}
        connection = _Connection(after)
        bucket = _Bucket(connection, NAME)
        key = _Key(bucket, KEY)
        acl = self._makeOne(key)
        acl.loaded = True
        acl.entity('allUsers', ROLE)
        self.assertTrue(acl.reload() is acl)
        self.assertEqual(list(acl), [])

    def test_reload_lazy(self):
        NAME = 'name'
        KEY = 'key'
        ROLE = 'role'
        after = {'items': [{'entity': 'allUsers', 'role': ROLE}]}
        connection = _Connection(after)
        bucket = _Bucket(connection, NAME)
        key = _Key(bucket, KEY)
        acl = self._makeOne(key)
        self.assertTrue(acl.reload() is acl)
        self.assertEqual(list(acl),
                         [{'entity': 'allUsers', 'role': ROLE}])
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'GET')
        self.assertEqual(kw[0]['path'], '/b/name/o/%s/acl' % KEY)

    def test_save_none_set_none_passed(self):
        NAME = 'name'
        KEY = 'key'
        connection = _Connection()
        bucket = _Bucket(connection, NAME)
        key = _Key(bucket, KEY)
        acl = self._makeOne(key)
        self.assertTrue(acl.save() is acl)
        kw = connection._requested
        self.assertEqual(len(kw), 0)

    def test_save_existing_set_none_passed(self):
        NAME = 'name'
        KEY = 'key'
        connection = _Connection({'foo': 'Foo', 'acl': []})
        bucket = _Bucket(connection, NAME)
        key = _Key(bucket, KEY)
        acl = self._makeOne(key)
        acl.loaded = True
        self.assertTrue(acl.save() is acl)
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/name/o/%s' % KEY)
        self.assertEqual(kw[0]['data'], {'acl': []})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})

    def test_save_existing_set_new_passed(self):
        NAME = 'name'
        KEY = 'key'
        ROLE = 'role'
        new_acl = [{'entity': 'allUsers', 'role': ROLE}]
        connection = _Connection({'foo': 'Foo', 'acl': new_acl})
        bucket = _Bucket(connection, NAME)
        key = _Key(bucket, KEY)
        acl = self._makeOne(key)
        acl.loaded = True
        acl.entity('allUsers', 'other-role')
        self.assertTrue(acl.save(new_acl) is acl)
        self.assertEqual(list(acl), new_acl)
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/name/o/%s' % KEY)
        self.assertEqual(kw[0]['data'], {'acl': new_acl})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})

    def test_clear(self):
        NAME = 'name'
        KEY = 'key'
        ROLE = 'role'
        connection = _Connection({'foo': 'Foo', 'acl': []})
        bucket = _Bucket(connection, NAME)
        key = _Key(bucket, KEY)
        acl = self._makeOne(key)
        acl.loaded = True
        acl.entity('allUsers', ROLE)
        self.assertTrue(acl.clear() is acl)
        self.assertEqual(list(acl), [])
        kw = connection._requested
        self.assertEqual(len(kw), 1)
        self.assertEqual(kw[0]['method'], 'PATCH')
        self.assertEqual(kw[0]['path'], '/b/name/o/%s' % KEY)
        self.assertEqual(kw[0]['data'], {'acl': []})
        self.assertEqual(kw[0]['query_params'], {'projection': 'full'})


class _Key(object):

    def __init__(self, bucket, key):
        self.bucket = bucket
        self.key = key

    @property
    def connection(self):
        return self.bucket.connection

    @property
    def path(self):
        return '%s/o/%s' % (self.bucket.path, self.key)


class _Bucket(object):

    def __init__(self, connection, name):
        self.connection = connection
        self.name = name

    @property
    def path(self):
        return '/b/%s' % self.name


class _Connection(object):
    _delete_ok = False

    def __init__(self, *responses):
        self._responses = responses
        self._requested = []
        self._deleted = []

    def api_request(self, **kw):
        from gcloud.storage.exceptions import NotFound
        self._requested.append(kw)

        try:
            response, self._responses = self._responses[0], self._responses[1:]
        except:  # pragma: NO COVER
            raise NotFound('miss')
        else:
            return response
