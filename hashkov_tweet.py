#!/bin/env python
from argparse import ArgumentParser
import sys
from hashkov.twitter import Twitter
from hashkov.chain import MarkovChain
from hashkov import text_pipeline
import os
import pickle


def build_pipeline():
    '''
    Build a text pipeline.
    '''
    pipeline = text_pipeline.HashtagCleaner()
    (pipeline.attach_next(text_pipeline.MentionCleaner())
             .attach_next(text_pipeline.UrlCleaner())
             .attach_next(text_pipeline.WhitespaceCleaner())
             .attach_next(text_pipeline.Tokenizer(1)))
    return pipeline


def get_argument_parser():
    '''
    Build and return an argument parser.
    '''
    parser = ArgumentParser(description='Tweet Markov chain generated tweets.'
                                        ' See README.md for more')
    parser.add_argument('-t', '--hashtag', dest='hashtag',
                        help='The hashtag to tweet to')
    parser.add_argument('-a', '--app-key', dest='app_key',
                        help='The app key')
    parser.add_argument('-c', '--app-secret', dest='app_secret',
                        help='The app secret')
    parser.add_argument('-k', '--access-token', dest='access_token',
                        help='The access token')
    parser.add_argument('-s', '--access-secret', dest='access_secret',
                        help='The access secret')
    parser.add_argument('-l', '--lang', dest='lang',
                        help='The language to tweet in', default='en')
    parser.add_argument('-p', '--pickle', dest='pickle', default=None,
                        help='Optionally, somewhere to save the chain '
                             'so that it does better next time')
    return parser


def get_chain(opts):
    '''
    Build or unpickle the markov chain.
    '''
    if opts.pickle is not None and os.path.isfile(opts.pickle):
        with open(opts.pickle, 'rb') as f:
            chain = pickle.load(f)
        return chain
    return MarkovChain()


def save_chain(chain, opts):
    '''
    Pickle the markov chain given, if desired
    '''
    if opts.pickle is not None:
        with open(opts.pickle, 'wb') as f:
            pickle.dump(chain, f)


def main():
    parser = get_argument_parser()
    opts = parser.parse_args()
    if any([getattr(opts, i) is None for i in
            ['hashtag', 'app_key', 'app_secret']]):
        parser.print_usage()
        return 1
    twitter = Twitter(opts.app_key, opts.app_secret)
    if any([getattr(opts, i) is None for i in
            ['access_token', 'access_secret']]):
        (token, url) = twitter.request_request_token()
        print("Please go to %s and input the pin that you get here." % url)
        pin = input('Pin: ')
        (key, secret) = twitter.request_access_token(pin)
        print("Your access token is:\nKey: %s\nSecret: %s\n" % (key, secret))
    else:
        twitter.set_access_token(opts.access_token, opts.access_secret)
    tweets = twitter.search_by_hashtag(opts.hashtag, 10, opts.lang)
    pipeline = build_pipeline()
    tweets = [pipeline.process(tweet) for tweet in tweets]
    chain = get_chain(opts)
    chain.train(tweets)
    # 40 words should be more than enough to get us a nice tweet
    tweet = chain.sample(20)
    result = []
    for token in tweet:
        if len(' '.join(result)) + len(token) < 140:
            result.append(token)
    tweet = ' '.join(result)
    # twitter.tweet(tweet)
    print("I Tweeted: %s" % tweet)
    save_chain(chain, opts)
    return 0

if __name__ == '__main__':
    sys.exit(main())
