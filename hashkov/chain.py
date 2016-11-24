'''
Provides the Markov Chain implementation.
'''
import random


class MarkovChain(object):
    '''
    A Markov chain.
    '''
    def __init__(self):
        '''
        Construct the Markov chain.
        '''
        self.memory = {}

    def train(self, samples):
        '''
        Train the markov chain with a list of samples.
        Each sample itself is a list of tokens that the chain
        will look at.
        '''
        for sample in samples:
            prev = ''  # The start
            for token in sample:
                prev_mem = self.memory.setdefault(prev.lower(), [])
                prev_mem.append(token)
                prev = token

    def sample(self, length):
        '''
        Sample the chain, returning a list of tokens of the length given.
        '''
        def inner_sample(length, token):
            if not length:
                return [token]
            token_mem = self.memory.get(token.lower())
            if token_mem is None or len(token_mem) == 0:
                return [token]  # Chain's over folks
            next_token = random.choice(token_mem)
            return [token] + inner_sample(length - 1, next_token)
        return inner_sample(length, '')
