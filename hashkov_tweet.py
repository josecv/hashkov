#!/bin/env python
from optparse import OptionParser
from hashkov.twitter import Twitter

def build_pipeline():
    '''
    Build a text pipeline.
    '''
    pass

def main():
    parser = OptionParser()
    parser.add_option('-t', '--hashtag', dest='hashtag',
                      help='The hashtag to tweet to', type='string')
    parser.add_option('-a', '--app-key', dest='app_key',
                      help='The app key', type='string')
    parser.add_option('-c', '--app-secret', dest='app_secret',
                      help='The app secret', type='string')
    parser.add_option('-k', '--access-token', dest='access_token',
                      help='The access token', default=None, type='string')
    parser.add_option('-s', '--access-secret', dest='access_secret',
                      help='The access secret', default=None, type='string')
    (opts, args) = parser.parse_args()
    twitter = Twitter(opts['app_key'], opts['app_secret')
    if any([i is None for i in [opts['access_token'], opts['access_secret']]]):
        (token, url) = twitter.request_request_token()
        print("Please go to %s and input the pin that you get here." % url)
        pin = input('Pin: ')
        twitter.request_access_token(pin)
    else:
        twitter.set_access_token(opts['access_token'], opts['access_secret'])
    tweets = twitter.search_by_hashtag(opts['hashtag'])

if __name__ == '__main__':
    main()
