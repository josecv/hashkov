from hashkov.chain import MarkovChain


import unittest


class MarkovChainTest(unittest.TestCase):
    '''
    test the Markov chain implementation
    '''

    def setUp(self):
        self.markov = MarkovChain()

    def test_memory(self):
        '''
        Test that the memory of the markov chain is populated correctly
        '''
        samples = [['a', 'b', 'c']]
        self.markov.train(samples)
        self.assertDictEqual(self.markov.memory,
                             {'': ['a'], 'a': ['b'], 'b': ['c']})
        samples = [['a', 'a', 'c', 'd', 'b']]
        self.markov.train(samples)
        self.assertDictEqual(self.markov.memory,
                             {'': ['a', 'a'], 'a': ['b', 'a', 'c'],
                              'b': ['c'], 'c': ['d'], 'd': ['b']})

    def test_sample(self):
        '''
        Test that we can sample properly.
        '''
        samples = [['a', 'b', 'c']]
        self.markov.train(samples)
        # Only one way to go here
        result = ''.join(self.markov.sample(3))
        self.assertEqual(result, 'abc')
        result = ''.join(self.markov.sample(100))
        self.assertEqual(result, 'abc')
