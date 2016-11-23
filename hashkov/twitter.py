'''
Communicates with twitter.
'''
import requests as req_module
from requests_oauthlib import OAuth1
from urllib import parse


class TwitterException(Exception):
    '''
    An exception in case something goes wrong.
    '''

    def __init__(self, response):
        '''
        Initialize the exception with the response given.
        '''
        super(TwitterException, self).__init__("Twitter error %d: %s" %
                                               (response.status_code,
                                                response.text))


class Twitter(object):
    '''
    A twitter client.
    '''

    request_token_url = 'https://api.twitter.com/oauth/request_token'
    authorize_url = 'https://api.twitter.com/oauth/authorize'
    access_token_url = 'https://api.twitter.com/oauth/access_token'
    tweet_url = 'https://api.twitter.com/1.1/statuses/update.json'
    search_url = 'https://api.twitter.com/1.1/search/tweets.json'

    def __init__(self, app_key, app_secret, requests=None, oauth_class=None):
        '''
        Initialize this twitter object with the key/secret given, and use
        the requests module given.
        '''
        if requests is None:
            requests = req_module
        if oauth_class is None:
            oauth_class = OAuth1
        self.oauth_class = oauth_class
        self.requests = requests
        self.app_secret = app_secret
        self.app_key = app_key
        self.oauth = self.oauth_class(app_key, client_secret=app_secret)

    def request_request_token(self):
        '''
        Get a request token from Twitter; return a tuple containing the token
        and the url that the user should visit to get the pin.
        '''
        r = self.requests.post(url=self.request_token_url, auth=self.oauth)
        credentials = parse.parse_qs(r.content)
        self.req_key = credentials.get('oauth_token')[0]
        self.req_secret = credentials.get('oauth_token_secret')[0]
        url = '%s?oauth_token=%s' % (self.authorize_url, self.req_key)
        return (self.req_key, url)

    def request_access_token(self, pin):
        '''
        Get an access token from Twitter. Requires the user-supplied pin. Will
        log the application in, and call set_access_token() on the value.
        Will also return a tuple with the (access_key, access_secret).
        '''
        self.oauth = self.oauth_class(self.app_key,
                                      client_secret=self.app_secret,
                                      resource_owner_key=self.req_key,
                                      resource_owner_secret=self.req_secret,
                                      verifier=pin)
        r = self.requests.post(url=self.access_token_url, auth=self.oauth)
        credentials = parse.parse_qs(r.content)
        access_key = credentials.get('oauth_token')[0]
        access_secret = credentials.get('oauth_token_secret')[0]
        self.set_access_token(access_key, access_secret)
        return (access_key, access_secret)

    def set_access_token(self, key, secret):
        '''
        Set the access key and secret to the token given.
        '''
        self.oauth = self.oauth_class(self.app_key,
                                      client_secret=self.app_secret,
                                      resource_owner_key=key,
                                      resource_owner_secret=secret)

    def search_by_hashtag(self, hashtag):
        '''
        Search tweets by hashtag.
        Return a list of tweets.
        '''
        payload = {'q': hashtag}
        r = self.requests.get(self.search_url, auth=self.oauth, params=payload)
        if r.status_code != 200:
            raise TwitterException(r)
        results = r.json()['statuses']
        results = [i['text'] for i in results]
        return results

    def tweet(self, tweet):
        '''
        Tweet something.
        '''
        payload = {'status': tweet}
        # It seems that this is passed in through the url
        r = self.requests.post(self.tweet_url, auth=self.oauth, params=payload)
        if r.status_code != 200:
            raise TwitterException(r)
