#!/usr/bin/env python
# -*- coding: utf-8 -*-

from unittest2 import TestCase
from datetime import datetime
from mock import patch, Mock, ANY

from afp_cli.cli_functions import get_valid_seconds, get_first_role
from afp_cli.client import APICallError


class GetValidSecondsTest(TestCase):

    def test_get_valid_seconds(self):
        future_date = '1970-01-01T00:30:00Z'
        utc_now = datetime(1970, 1, 1)
        self.assertEqual(get_valid_seconds(future_date, utc_now), 30*60)

    @patch('sys.stderr', Mock())
    def test_get_valid_seconds_catches(self):
        future_date = 'NO_SUCH_DATE'
        utc_now = datetime(1970, 1, 1)
        self.assertEqual(get_valid_seconds(future_date, utc_now), 3600)


class GetFirstRoleTests(TestCase):

    def test_with_single_account_and_single_role(self):
        client = Mock()
        client.get_account_and_role_list.return_value = \
            {'ACCOUNT1': ['ROLE1']}
        self.assertEqual('ROLE1', get_first_role(client, 'ACCOUNT1'))

    def test_with_single_account_and_multiple_roles(self):
        client = Mock()
        client.get_account_and_role_list.return_value = \
            {'ACCOUNT1': ['ROLE1', 'ROLE2']}
        self.assertEqual('ROLE1', get_first_role(client, 'ACCOUNT1'))

    def test_with_multiple_accounts_and_multiple_roles(self):
        client = Mock()
        client.get_account_and_role_list.return_value = \
            {'ACCOUNT1': ['ROLE1', 'ROLE2'],
             'ACCOUNT2': ['ROLE3', 'ROLE4']}
        self.assertEqual('ROLE1', get_first_role(client, 'ACCOUNT1'))

    @patch('afp_cli.cli_functions.error')
    def test_excpetion_when_fetching_roles(self, error_mock):
        client = Mock()
        client.get_account_and_role_list.side_effect = APICallError
        get_first_role(client, 'ANY_ACCOUNT')
        error_mock.assert_called_once_with(ANY)

    @patch('afp_cli.cli_functions.error')
    def test_excpetion_when_looking_for_account(self, error_mock):
        client = Mock()
        client.get_account_and_role_list.return_value = \
            {'ACCOUNT1': ['ROLE1']}
        get_first_role(client, 'ACCOUNT2')
        error_mock.assert_called_once_with(ANY)

    @patch('afp_cli.cli_functions.error')
    def test_excpetion_when_looking_for_role(self, error_mock):
        client = Mock()
        client.get_account_and_role_list.return_value = \
            {'ACCOUNT1': []}
        get_first_role(client, 'ACCOUNT1')
        error_mock.assert_called_once_with(ANY)
