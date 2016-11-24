#!/bin/env python
from argparse import ArgumentParser
import sys
from hashkov.twitter import Twitter
from hashkov.chain import MarkovChain
from hashkov import text_pipeline
import os
import pickle
import random


def get_argument_parser():
    '''
    Build and return an argument parser.
    '''
    parser = ArgumentParser(description='Tweet Markov chain generated tweets.'
                                        ' See README.md for more')
    parser.add_argument('-a', '--app-key', dest='app_key',
                        help='The app key', required=True)
    parser.add_argument('-c', '--app-secret', dest='app_secret',
                        help='The app secret', required=True)
    parser.add_argument('-k', '--access-token', dest='access_token',
                        help='The access token')
    parser.add_argument('-s', '--access-secret', dest='access_secret',
                        help='The access secret')
    parser.add_argument('-l', '--lang', dest='lang',
                        help='The language to tweet in', default='en')
    parser.add_argument('-p', '--pickle', dest='pickle', default=None,
                        help='Optionally, a file to save the chain '
                             'so that it does better next time')
    parser.add_argument('-w', '--woeid', dest='woeid', default=4118, type=int,
                        help='For use with -d. The woeid that the trending'
                        ' hashtag should be from')
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        help='Force the hashtag to appear in the tweet '
                             '(by starting it off with it)')
    parser.add_argument('-n', '--ngram', dest='ngram', default=2, type=int,
                        help='How many words to consider as a token.'
                             ' Default 2')
    hashtag_parser = parser.add_mutually_exclusive_group(required=True)
    hashtag_parser.add_argument('-t', '--hashtag', dest='hashtag',
                                help='The hashtag to tweet to')
    hashtag_parser.add_argument('-d', '--autonomous', dest='autonomous',
                                help='Whether to run in autonomous mode.'
                                ' Incompatible with -t', action='store_true')
    return parser


def build_pipeline(opts):
    '''
    Build a text pipeline.
    '''
    pipeline = text_pipeline.HashtagCleaner()
    (pipeline.attach_next(text_pipeline.MentionCleaner())
             .attach_next(text_pipeline.UrlCleaner())
             .attach_next(text_pipeline.WhitespaceCleaner())
             .attach_next(text_pipeline.Tokenizer(opts.ngram)))
    return pipeline


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


def get_hashtag(twitter, opts):
    '''
    Figure out a hashtag to use.
    '''
    if opts.autonomous:
        trending = twitter.get_trending(opts.woeid)
        if not trending:
            return None
        return random.choice(trending)
    return opts.hashtag

def generate_tweet(chain, opts, hashtag):
    start = ''
    if opts.force:
        if not hashtag.startswith('#'):
            hashtag = '#' + hashtag
        hashtag = hashtag.replace('#', '#_').lower()
        keys = chain.get_possible_starts()
        keys = [k for k in keys if hashtag in k]
        start = random.choice(keys)
    # 40 words should be more than enough to get us a nice tweet
    tweet = chain.sample(20, start)
    result = []
    for token in tweet:
        if len(' '.join(result)) + len(token) < 140:
            result.append(token)
    tweet = ' '.join(result)
    return tweet


def main():
    parser = get_argument_parser()
    opts = parser.parse_args()
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
    hashtag = get_hashtag(twitter, opts)
    if hashtag is None:
        print('Could not decide on a hashtag. Will now quit')
        return 1
    print("Tweeting to %s" % hashtag)
    tweets = twitter.search_by_hashtag(hashtag, 10, opts.lang)
    pipeline = build_pipeline(opts)
    tweets = [pipeline.process(tweet) for tweet in tweets]
    chain = get_chain(opts)
    chain.train(tweets)
    start = ''
    tweet = generate_tweet(chain, opts, hashtag)
    twitter.tweet(tweet)
    print("I Tweeted: %s" % tweet)
    save_chain(chain, opts)
    return 0

if __name__ == '__main__':
    sys.exit(main())
