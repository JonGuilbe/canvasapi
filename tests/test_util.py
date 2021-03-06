from __future__ import absolute_import, division, print_function, unicode_literals
import unittest

import requests_mock

from canvasapi import Canvas
from canvasapi.course import CourseNickname
from canvasapi.user import User
from canvasapi.util import combine_kwargs, obj_or_id
from tests import settings
from tests.util import register_uris


@requests_mock.Mocker()
class TestUtil(unittest.TestCase):

    def setUp(self):
        self.canvas = Canvas(settings.BASE_URL, settings.API_KEY)

    # combine_kwargs()
    def test_combine_kwargs_empty(self, m):

        result = combine_kwargs()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_combine_kwargs_single(self, m):
        result = combine_kwargs(var='test')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn(('var', 'test'), result)

    def test_combine_kwargs_single_dict(self, m):
        result = combine_kwargs(var={'foo': 'bar'})
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn(('var[foo]', 'bar'), result)

    def test_combine_kwargs_single_list_empty(self, m):
        result = combine_kwargs(var=[])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_combine_kwargs_single_list_single_item(self, m):
        result = combine_kwargs(var=['test'])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn(('var[]', 'test'), result)

    def test_combine_kwargs_single_list_multiple_items(self, m):
        result = combine_kwargs(foo=['bar1', 'bar2', 'bar3', 'bar4'])
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)

        self.assertIn(('foo[]', 'bar1'), result)
        self.assertIn(('foo[]', 'bar2'), result)
        self.assertIn(('foo[]', 'bar3'), result)
        self.assertIn(('foo[]', 'bar4'), result)

        # Ensure kwargs are in correct order
        self.assertTrue(
            result.index(('foo[]', 'bar1'))
            < result.index(('foo[]', 'bar2'))
            < result.index(('foo[]', 'bar3'))
            < result.index(('foo[]', 'bar4'))
        )

    def test_combine_kwargs_multiple_dicts(self, m):
        result = combine_kwargs(
            var1={'foo': 'bar'},
            var2={'fizz': 'buzz'}
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)

        self.assertIn(('var1[foo]', 'bar'), result)
        self.assertIn(('var2[fizz]', 'buzz'), result)

    def test_combine_kwargs_multiple_mixed(self, m):
        result = combine_kwargs(
            var1=True,
            var2={'fizz': 'buzz'},
            var3='foo',
            var4=42,
            var5=['test1', 'test2', 'test3']
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 7)

        self.assertIn(('var1', True), result)
        self.assertIn(('var2[fizz]', 'buzz'), result)
        self.assertIn(('var3', 'foo'), result)
        self.assertIn(('var4', 42), result)
        self.assertIn(('var5[]', 'test1'), result)
        self.assertIn(('var5[]', 'test2'), result)
        self.assertIn(('var5[]', 'test3'), result)

        # Ensure list kwargs are in correct order
        self.assertTrue(
            result.index(('var5[]', 'test1'))
            < result.index(('var5[]', 'test2'))
            < result.index(('var5[]', 'test3'))
        )

    def test_combine_kwargs_nested_dict(self, m):
        result = combine_kwargs(dict={
            'key': {'subkey': 'value'}
        })
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)

        self.assertIn(('dict[key][subkey]', 'value'), result)

    def test_combine_kwargs_multiple_nested_dicts(self, m):
        result = combine_kwargs(
            dict1={
                'key1': {
                    'subkey1-1': 'value1-1',
                    'subkey1-2': 'value1-2'
                },
                'key2': {
                    'subkey2-1': 'value2-1',
                    'subkey2-2': 'value2-2'
                }
            },
            dict2={
                'key1': {
                    'subkey1-1': 'value1-1',
                    'subkey1-2': 'value1-2'
                },
                'key2': {
                    'subkey2-1': 'value2-1',
                    'subkey2-2': 'value2-2'
                }
            }
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 8)

        self.assertIn(('dict1[key1][subkey1-1]', 'value1-1'), result)
        self.assertIn(('dict1[key1][subkey1-2]', 'value1-2'), result)
        self.assertIn(('dict1[key2][subkey2-1]', 'value2-1'), result)
        self.assertIn(('dict1[key2][subkey2-2]', 'value2-2'), result)
        self.assertIn(('dict2[key1][subkey1-1]', 'value1-1'), result)
        self.assertIn(('dict2[key1][subkey1-2]', 'value1-2'), result)
        self.assertIn(('dict2[key2][subkey2-1]', 'value2-1'), result)
        self.assertIn(('dict2[key2][subkey2-2]', 'value2-2'), result)

    def test_combine_kwargs_super_nested_dict(self, m):
        result = combine_kwargs(
            big_dict={'a': {'b': {'c': {'d': {'e': 'We need to go deeper'}}}}}
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertIn(('big_dict[a][b][c][d][e]', 'We need to go deeper'), result)

    def test_combine_kwargs_the_gauntlet(self, m):
        result = combine_kwargs(
            foo='bar',
            fb={
                3: 'fizz',
                5: 'buzz',
                15: 'fizzbuzz'
            },
            true=False,
            life=42,
            basic_list=['foo', 'bar'],
            days_of_xmas={
                'first': {
                    1: 'partridge in a pear tree'
                },
                'second': {
                    1: 'partridge in a pear tree',
                    '2': 'turtle doves',
                },
                'third': {
                    1: 'partridge in a pear tree',
                    '2': 'turtle doves',
                    3: 'french hens'
                },
                'fourth': {
                    1: 'partridge in a pear tree',
                    '2': 'turtle doves',
                    3: 'french hens',
                    '4': 'mocking birds',
                },
                'fifth': {
                    1: 'partridge in a pear tree',
                    '2': 'turtle doves',
                    3: 'french hens',
                    '4': 'mocking birds',
                    '5': 'GOLDEN RINGS'
                }
            },
            super_nest={'1': {'2': {'3': {'4': {'5': {'6': 'tada'}}}}}},
            list_dicts=[
                {
                    'l_d1a': 'val1a',
                    'l_d1b': 'val1b'
                },
                {
                    'l_d2a': 'val2a',
                    'l_d2b': 'val2b'
                }
            ],
            nest_list=[
                ['1a', '1b'],
                ['2a', '2b'],
                ['3a', '3b']
            ]
        )
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 34)

        # Check that all keys were generated correctly
        self.assertIn(('foo', 'bar'), result)
        self.assertIn(('fb[3]', 'fizz'), result)
        self.assertIn(('fb[5]', 'buzz'), result)
        self.assertIn(('fb[15]', 'fizzbuzz'), result)
        self.assertIn(('true', False), result)
        self.assertIn(('life', 42), result)
        self.assertIn(('basic_list[]', 'foo'), result)
        self.assertIn(('basic_list[]', 'bar'), result)
        self.assertIn(('days_of_xmas[first][1]', 'partridge in a pear tree'), result)
        self.assertIn(('days_of_xmas[second][1]', 'partridge in a pear tree'), result)
        self.assertIn(('days_of_xmas[second][2]', 'turtle doves'), result)
        self.assertIn(('days_of_xmas[third][1]', 'partridge in a pear tree'), result)
        self.assertIn(('days_of_xmas[third][2]', 'turtle doves'), result)
        self.assertIn(('days_of_xmas[third][3]', 'french hens'), result)
        self.assertIn(('days_of_xmas[fourth][1]', 'partridge in a pear tree'), result)
        self.assertIn(('days_of_xmas[fourth][2]', 'turtle doves'), result)
        self.assertIn(('days_of_xmas[fourth][3]', 'french hens'), result)
        self.assertIn(('days_of_xmas[fourth][4]', 'mocking birds'), result)
        self.assertIn(('days_of_xmas[fifth][1]', 'partridge in a pear tree'), result)
        self.assertIn(('days_of_xmas[fifth][2]', 'turtle doves'), result)
        self.assertIn(('days_of_xmas[fifth][3]', 'french hens'), result)
        self.assertIn(('days_of_xmas[fifth][4]', 'mocking birds'), result)
        self.assertIn(('days_of_xmas[fifth][5]', 'GOLDEN RINGS'), result)
        self.assertIn(('super_nest[1][2][3][4][5][6]', 'tada'), result)
        self.assertIn(('list_dicts[][l_d1b]', 'val1b'), result)
        self.assertIn(('list_dicts[][l_d1a]', 'val1a'), result)
        self.assertIn(('list_dicts[][l_d2b]', 'val2b'), result)
        self.assertIn(('list_dicts[][l_d2a]', 'val2a'), result)
        self.assertIn(('nest_list[][]', '1a'), result)
        self.assertIn(('nest_list[][]', '1b'), result)
        self.assertIn(('nest_list[][]', '2a'), result)
        self.assertIn(('nest_list[][]', '2b'), result)
        self.assertIn(('nest_list[][]', '3a'), result)
        self.assertIn(('nest_list[][]', '3b'), result)

        # Ensure list kwargs are in correct order
        self.assertTrue(
            result.index(('basic_list[]', 'foo'))
            < result.index(('basic_list[]', 'bar'))
        )
        self.assertTrue(
            result.index(('list_dicts[][l_d1a]', 'val1a'))
            < result.index(('list_dicts[][l_d2a]', 'val2a'))
        )
        self.assertTrue(
            result.index(('list_dicts[][l_d1b]', 'val1b'))
            < result.index(('list_dicts[][l_d2b]', 'val2b'))
        )
        self.assertTrue(
            result.index(('nest_list[][]', '1a'))
            < result.index(('nest_list[][]', '1b'))
            < result.index(('nest_list[][]', '2a'))
            < result.index(('nest_list[][]', '2b'))
            < result.index(('nest_list[][]', '3a'))
            < result.index(('nest_list[][]', '3b'))
        )

    # obj_or_id()
    def test_obj_or_id_int(self, m):
        user_id = obj_or_id(1, 'user_id', (User,))

        self.assertIsInstance(user_id, int)
        self.assertEqual(user_id, 1)

    def test_obj_or_id_str_valid(self, m):
        user_id = obj_or_id("1", 'user_id', (User,))

        self.assertIsInstance(user_id, int)
        self.assertEqual(user_id, 1)

    def test_obj_or_id_str_invalid(self, m):
        with self.assertRaises(TypeError):
            obj_or_id("1a", 'user_id', (User,))

    def test_obj_or_id_obj(self, m):
        register_uris({'user': ['get_by_id']}, m)

        user = self.canvas.get_user(1)

        user_id = obj_or_id(user, 'user_id', (User,))

        self.assertIsInstance(user_id, int)
        self.assertEqual(user_id, 1)

    def test_obj_or_id_obj_no_id(self, m):
        register_uris({'user': ['course_nickname']}, m)

        nick = self.canvas.get_course_nickname(1)

        with self.assertRaises(TypeError):
            obj_or_id(nick, 'nickname_id', (CourseNickname,))
