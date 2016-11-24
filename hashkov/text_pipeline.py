'''
Offers a pipeline to clean and tokenize text.
'''
import re
import string


def flatten(l):
    '''
    Flatten the list recursively.
    Note that it does have to be a list and the iterables it contains also have
    to be lists (or they won't be flattened).
    Return a list of all the elements in it.
    '''
    retval = []
    for element in l:
        if isinstance(element, list):
            retval.extend(flatten(element))
        else:
            retval.append(element)
    return retval


class PipelineElement(object):
    '''
    An element in the text pipeline.
    '''
    def __init__(self):
        '''
        Initialize.
        '''
        self.next_element = BaseElement()

    def attach_next(self, next_element):
        '''
        Attach an element to the output end of this pipeline.
        Returns the next element for chaining
        '''
        self.next_element = next_element
        return next_element

    def process(self, text):
        '''
        Toss the text (a string) given down the pipeline.
        Return either a list or a string, depending on whether the
        pipeline split it.
        '''
        result = self._do_process(text)
        if isinstance(result, list):
            for i in range(len(result)):
                result[i] = self.next_element.process(result[i])
            result = flatten(result)
        else:
            result = self.next_element.process(result)
        return result

    def _do_process(self, text):
        '''
        Actually do the processing on the text given.
        '''
        raise Exception('Need to implement method _do_process!')


class BaseElement(PipelineElement):
    '''
    The base pipeline element that doesn't do anything.
    Where the buck stops.
    '''
    def __init__(self):
        '''Initialize.'''
        pass

    def process(self, text):
        '''Do nothing to the text given (and don't recurse deeper'''
        return text


class WhitespaceCleaner(PipelineElement):
    '''
    Cleans up any whitespace in the text to make it uniform.
    '''
    def __init__(self):
        '''Initialize'''
        super(WhitespaceCleaner, self).__init__()
        self.regex = re.compile(r'\s+')

    def _do_process(self, text):
        '''Clean up the text'''
        return self.regex.sub(' ', text)


class PunctuationCleaner(PipelineElement):
    '''
    Cleans up any punctuation in the text
    '''
    def __init__(self, punctuation=None):
        '''Initialize. Will take a string of punctuation if given, else will just use
           string.punctuation'''
        super(PunctuationCleaner, self).__init__()
        if punctuation is None:
            punctuation = string.punctuation
        self.translator = str.maketrans('', '', punctuation)

    def _do_process(self, text):
        '''Clean up the text'''
        return text.translate(self.translator)


class MentionCleaner(PipelineElement):
    '''
    Removes any @mentions from a piece of text
    '''
    def __init__(self):
        '''Initialize.'''
        super(MentionCleaner, self).__init__()
        self.regex = re.compile(r'@\w+')

    def _do_process(self, text):
        '''Clean up the text'''
        return self.regex.sub('', text)


class HashtagCleaner(PipelineElement):
    '''
    Turns hashtags into more kosher automatable versions.
    This is because it's forbidden to have a robot tweet to trending topics.
    '''
    def __init__(self):
        '''Initialize'''
        super(HashtagCleaner, self).__init__()
        self.regex = re.compile(r'(\s+|^)#(([^%s0-9\s][_\w]*)|([_]\w+))' %
                                string.punctuation)

    def _do_process(self, text):
        '''Clean up the text'''
        return self.regex.sub(r'\1#_\2', text)


class Tokenizer(PipelineElement):
    '''
    Tokenizes the input.
    '''
    def __init__(self, degree):
        '''
        Initialize a tokenizer.
        Will make ngrams with the number of words given.
        '''
        super(Tokenizer, self).__init__()
        self.degree = degree

    def _do_process(self, text):
        '''Split up the text.'''
        retval = []
        split = text.split()
        for i in range(0, len(split), self.degree):
            retval.append(" ".join(split[i:i + self.degree]))
        return retval
