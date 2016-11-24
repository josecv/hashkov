# \#hashkov
\#hashkov is a Python 3 program that tweets markov-chain generated tweets with a given #hashtag.

Note that this will convert #hashtag to #\_hashtag. This is because Twitter's ToS forbid tweeting
to trending topics via a robot, and I'm not keen on getting banned.

# Usage
You do need to register a Twitter app for this to work. Once that's done, you can invoke it as:

```
./hashkov_tweet.py -t <HASHTAG> -a <APP_KEY> -c <APP_SECRET>
```

It will give you a url so that you can request a pin for hashkov to get an access token, then print out said token.
Once you do have the token, future invocations can be done as:

```
./hashkov_tweet.py -t <HASHTAG> -a <APP_KEY> -c <APP_SECRET> -k <ACCESS_KEY> -s <ACCESS_SECRET>
```
