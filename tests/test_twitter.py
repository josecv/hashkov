from hashkov.twitter import Twitter
import unittest
from unittest.mock import Mock, ANY
from urllib import parse


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
        r.content = encoded
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
        r.content = encoded
        self.requests.post.return_value = r
        self.twitter.request_request_token()
        encoded = parse.urlencode({'oauth_token': self.access_key,
                                   'oauth_token_secret': self.access_secret})
        r.content = encoded
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
