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

    def setUp(self):
        self.requests = Mock()
        self.oauth_class = Mock()
        self.oauth_object = Mock()
        self.oauth_class.return_value = self.oauth_object
        self.twitter = Twitter(self.app_key, self.app_secret, 
                               self.requests, self.oauth_class)

    def test_original_construction(self):
        self.oauth_class.assert_called_once_with(self.app_key,
                                                 client_secret=self.app_secret)

    def test_request_token(self):
        '''
        Test that we can work the authentication system.
        '''
        request_key = 'request_key'
        request_secret = 'request_secret'
        encoded = parse.urlencode({'oauth_token': request_key,
                                   'oauth_token_secret': request_secret})
        r = Mock()
        r.content = encoded
        self.requests.post.return_value = r
        (got_token, got_url) = self.twitter.request_request_token()
        self.assertEqual(got_token, request_key)
        self.requests.post.assert_called_once_with(url=ANY,
                                                   auth=self.oauth_object)
