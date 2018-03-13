#!/usr/bin/env python
# Copyright (C) 2018 IBM Corp. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
_replicator_mock_tests_

replicator module - Mock unit tests for the Replicator class
"""

import mock
import unittest

from cloudant.database import CouchDatabase
from cloudant.replicator import Replicator

from tests.unit.iam_auth_tests import MOCK_API_KEY


class ReplicatorDocumentValidationMockTests(unittest.TestCase):
    """
    Replicator document validation tests
    """

    def setUp(self):
        self.repl_id = 'rep_test'

        self.server_url = 'http://localhost:5984'
        self.user_ctx = {
            'name': 'foo',
            'roles': ['erlanger', 'researcher']
        }

        self.source_db = 'source_db'
        self.target_db = 'target_db'

    def test_using_admin_party_source_and_target(self):
        # setup mocks
        m_admin_party_client = mock.MagicMock()
        type(m_admin_party_client).admin_party = mock.PropertyMock(
            return_value=True)
        type(m_admin_party_client).server_url = mock.PropertyMock(
            return_value=self.server_url)

        m_replicator = mock.MagicMock()
        type(m_replicator).creds = mock.PropertyMock(return_value=None)
        m_admin_party_client.__getitem__.return_value = m_replicator

        # create source/target databases
        src = CouchDatabase(m_admin_party_client, self.source_db)
        tgt = CouchDatabase(m_admin_party_client, self.target_db)

        # trigger replication
        rep = Replicator(m_admin_party_client)
        rep.create_replication(src, tgt, repl_id=self.repl_id)

        kcall = m_replicator.create_document.call_args_list
        self.assertEquals(len(kcall), 1)
        args, kwargs = kcall[0]
        self.assertEquals(len(args), 1)

        expected_doc = {
            '_id': self.repl_id,
            'source': {'url': '/'.join((self.server_url, self.source_db))},
            'target': {'url': '/'.join((self.server_url, self.target_db))}
        }

        self.assertDictEqual(args[0], expected_doc)
        self.assertTrue(kwargs['throw_on_exists'])

    def test_using_basic_auth_source_and_target(self):
        test_basic_auth_header = 'abc'

        # setup mocks
        m_basic_auth_client = mock.MagicMock()
        type(m_basic_auth_client).admin_party = mock.PropertyMock(
            return_value=False)
        type(m_basic_auth_client).server_url = mock.PropertyMock(
            return_value=self.server_url)
        type(m_basic_auth_client).is_iam_authenticated = mock.PropertyMock(
            return_value=False)

        m_replicator = mock.MagicMock()
        m_basic_auth_client.__getitem__.return_value = m_replicator
        m_basic_auth_client.basic_auth_str.return_value = test_basic_auth_header

        # create source/target databases
        src = CouchDatabase(m_basic_auth_client, self.source_db)
        tgt = CouchDatabase(m_basic_auth_client, self.target_db)

        # trigger replication
        rep = Replicator(m_basic_auth_client)
        rep.create_replication(
            src, tgt, repl_id=self.repl_id, user_ctx=self.user_ctx)

        kcall = m_replicator.create_document.call_args_list
        self.assertEquals(len(kcall), 1)
        args, kwargs = kcall[0]
        self.assertEquals(len(args), 1)

        expected_doc = {
            '_id': self.repl_id,
            'user_ctx': self.user_ctx,
            'source': {
                'headers': {'Authorization': test_basic_auth_header},
                'url': '/'.join((self.server_url, self.source_db))
            },
            'target': {
                'headers': {'Authorization': test_basic_auth_header},
                'url': '/'.join((self.server_url, self.target_db))
            }
        }

        self.assertDictEqual(args[0], expected_doc)
        self.assertTrue(kwargs['throw_on_exists'])

    def test_using_iam_auth_source_and_target(self):
        # setup mocks
        m_session = mock.MagicMock()
        type(m_session).api_key = mock.PropertyMock(
            return_value=MOCK_API_KEY)

        m_iam_auth_client = mock.MagicMock()
        type(m_iam_auth_client).admin_party = mock.PropertyMock(
            return_value=False)
        type(m_iam_auth_client).server_url = mock.PropertyMock(
            return_value=self.server_url)
        type(m_iam_auth_client).r_session = mock.PropertyMock(
            return_value=m_session)
        type(m_iam_auth_client).is_iam_authenticated = mock.PropertyMock(
            return_value=True)

        m_replicator = mock.MagicMock()
        m_iam_auth_client.__getitem__.return_value = m_replicator

        # create source/target databases
        src = CouchDatabase(m_iam_auth_client, self.source_db)
        tgt = CouchDatabase(m_iam_auth_client, self.target_db)

        # trigger replication
        rep = Replicator(m_iam_auth_client)
        rep.create_replication(
            src, tgt, repl_id=self.repl_id, user_ctx=self.user_ctx)

        kcall = m_replicator.create_document.call_args_list
        self.assertEquals(len(kcall), 1)
        args, kwargs = kcall[0]
        self.assertEquals(len(args), 1)

        expected_doc = {
            '_id': self.repl_id,
            'user_ctx': self.user_ctx,
            'source': {
                'auth': {'iam': MOCK_API_KEY},
                'url': '/'.join((self.server_url, self.source_db))
            },
            'target': {
                'auth': {'iam': MOCK_API_KEY},
                'url': '/'.join((self.server_url, self.target_db))
            }
        }

        self.assertDictEqual(args[0], expected_doc)
        self.assertTrue(kwargs['throw_on_exists'])
