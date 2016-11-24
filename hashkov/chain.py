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

    def sample(self, length, start_token=''):
        '''
        Sample the chain, returning a list of tokens of the length given.
        Optionally, force it to start with the token given.
        '''
        if not length:
            return [start_token]
        token_mem = self.memory.get(start_token.lower())
        if token_mem is None or len(token_mem) == 0:
            return [start_token]  # Chain's over folks
        next_token = random.choice(token_mem)
        return [start_token] + self.sample(length - 1, next_token)

    def get_possible_starts(self):
        '''
        Return the keys of the memory, thus the possible starting
        tokens.
        Note that these are always in lowercase because of implementation
        details.
        '''
        return self.memory.keys()
