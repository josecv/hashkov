from hashkov.twitter import Twitter, TwitterException
import unittest
from unittest.mock import Mock, ANY, call
from urllib import parse
import os
import json


class TwitterTest(unittest.TestCase):
    '''
    Test the twitter class.
    '''
    app_key = 'app_key'
    app_secret = 'app_secret'
    request_key = 'request_key'
    request_secret = 'request_secret'
    access_key = 'access_key'
    access_secret = 'access_secret'
    pin = 'pin'

    def setUp(self):
        '''
        Set up the test.
        '''
        self.requests = Mock()
        self.oauth_class = Mock()
        self.oauth_object = Mock()
        self.oauth_class.return_value = self.oauth_object
        self.twitter = Twitter(self.app_key, self.app_secret,
                               self.requests, self.oauth_class)

    def test_original_construction(self):
        '''
        Make sure the oauth object has been properly created.
        '''
        self.oauth_class.assert_called_once_with(self.app_key,
                                                 client_secret=self.app_secret)

    def test_request_token(self):
        '''
        Test that we can get a request token.
        '''
        encoded = parse.urlencode({'oauth_token': self.request_key,
                                   'oauth_token_secret': self.request_secret})
        r = Mock()
        r.content = bytearray(encoded, 'utf-8')
        self.requests.post.return_value = r
        (got_token, got_url) = self.twitter.request_request_token()
        self.assertEqual(got_token, self.request_key)
        self.requests.post.assert_called_once_with(url=ANY,
                                                   auth=self.oauth_object)

    def test_access_token(self):
        '''
        Test that we can get an access token.
        '''
        encoded = parse.urlencode({'oauth_token': self.request_key,
                                   'oauth_token_secret': self.request_secret})
        r = Mock()
        r.content = bytearray(encoded, 'utf-8')
        self.requests.post.return_value = r
        self.twitter.request_request_token()
        encoded = parse.urlencode({'oauth_token': self.access_key,
                                   'oauth_token_secret': self.access_secret})
        r.content = bytearray(encoded, 'utf-8')
        self.oauth_class.reset_mock()
        self.requests.post.reset_mock()
        (access_key, access_secret) = (self.twitter.
                                       request_access_token(self.pin))
        self.requests.post.assert_called_once_with(url=ANY,
                                                   auth=self.oauth_object)
        self.assertEqual(access_key, self.access_key)
        self.assertEqual(access_secret, self.access_secret)
        self.oauth_class.assert_any_call(
                self.app_key,
                client_secret=self.app_secret,
                resource_owner_key=self.request_key,
                resource_owner_secret=self.request_secret,
                verifier=self.pin)
        self.oauth_class.assert_called_with(
                self.app_key,
                client_secret=self.app_secret,
                resource_owner_key=self.access_key,
                resource_owner_secret=self.access_secret)

    def test_search_by_hashtag(self):
        '''
        Test the search method.
        '''
        json_path = os.path.join(os.path.dirname(__file__), 'resources',
                                 'search_results.json')
        with open(json_path, 'r') as f:
            text = ''.join(f.readlines())
        r = Mock()
        r.status_code = 200
        r.text = text
        r.json.return_value = json.loads(text)
        self.requests.get.return_value = r
        expected = ['Aggressive Ponytail #freebandnames',
                    'Thee Namaste Nerdz. #FreeBandNames',
                    'Mexican Heaven, Mexican Hell #freebandnames',
                    'The Foolish Mortals #freebandnames']
        q = '#freebandnames'
        results = self.twitter.search_by_hashtag(q)
        self.requests.get.assert_called_once_with(ANY, auth=ANY,
                                                  params={'q': q})
        self.assertEquals(expected, results)


    def test_search_by_hashtag_no_pound(self):
        '''
        Test the search method, when the hashtag doesn't have a #hash.
        '''
        json_path = os.path.join(os.path.dirname(__file__), 'resources',
                                 'search_results.json')
        with open(json_path, 'r') as f:
            text = ''.join(f.readlines())
        r = Mock()
        r.status_code = 200
        r.text = text
        r.json.return_value = json.loads(text)
        self.requests.get.return_value = r
        expected = ['Aggressive Ponytail #freebandnames',
                    'Thee Namaste Nerdz. #FreeBandNames',
                    'Mexican Heaven, Mexican Hell #freebandnames',
                    'The Foolish Mortals #freebandnames']
        q = 'freebandnames'
        results = self.twitter.search_by_hashtag(q)
        self.requests.get.assert_called_once_with(ANY, auth=ANY,
                                                  params={'q': '#' + q})
        self.assertEquals(expected, results)

    def test_search_by_hashtag_paginated(self):
        '''
        Test the search method with pagination.
        '''
        json_path = os.path.join(os.path.dirname(__file__), 'resources',
                                 'search_results.json')
        with open(json_path, 'r') as f:
            text = ''.join(f.readlines())
        r = Mock()
        r.status_code = 200
        r.text = text
        r.json.return_value = json.loads(text)
        self.requests.get.return_value = r
        expected = ['Aggressive Ponytail #freebandnames',
                    'Thee Namaste Nerdz. #FreeBandNames',
                    'Mexican Heaven, Mexican Hell #freebandnames',
                    'The Foolish Mortals #freebandnames',
                    'Aggressive Ponytail #freebandnames',
                    'Thee Namaste Nerdz. #FreeBandNames',
                    'Mexican Heaven, Mexican Hell #freebandnames',
                    'The Foolish Mortals #freebandnames',
                    'Aggressive Ponytail #freebandnames',
                    'Thee Namaste Nerdz. #FreeBandNames',
                    'Mexican Heaven, Mexican Hell #freebandnames',
                    'The Foolish Mortals #freebandnames']

        q = 'freebandnames'
        results = self.twitter.search_by_hashtag(q, 3)
        class ContainsNextPage(str):
            '''To check whether the next_results stuff is given'''
            def __eq__(self, other):
                return other.endswith("?max_id=249279667666817023&"
                                      "q=%23freebandnames&count=4&"
                                      "include_entities=1&result_type=mixed")
        calls = [call(ANY, auth=ANY, params={'q': '#' + q}),
                 call(ContainsNextPage(), auth=ANY),
                 call(ContainsNextPage(), auth=ANY)]
        self.requests.get.assert_has_calls(calls, any_order=True)

    def test_search_by_hashtag_error(self):
        '''
        Test the search method, when twitter returns an error.
        '''
        r = Mock()
        r.status_code = 401
        self.requests.get.return_value = r
        try:
            self.twitter.search_by_hashtag('#WhyTho')
            self.fail('Did not throw on http error')
        except TwitterException:
            pass

    def test_tweet(self):
        '''
        Test the tweet method
        '''
        tweet = 'Test tweet please ignore'
        r = Mock()
        r.status_code = 200
        self.requests.post.return_value = r
        self.twitter.tweet(tweet)
        self.requests.post.assert_called_once_with(ANY, auth=ANY,
                                                   params={'status': tweet})

    def test_tweet_error(self):
        '''
        Test the tweet method when there's an error.
        '''
        r = Mock()
        r.status_code = 401
        self.requests.post.return_value = r
        try:
            self.twitter.tweet('Test tweet please ignore')
            self.fail('Did not throw on http error')
        except TwitterException:
            pass
