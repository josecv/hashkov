from hashkov import text_pipeline
import unittest


class TextPipelineTest(unittest.TestCase):
    '''Test the text_pipeline module.'''

    def test_whitespace_punctuation(self):
        '''
        Test that the whitespace and punctuation cleaners work.
        Incidentally also tests basic pipeline operation.
        '''
        text = 'Text,  with...\n all kinds\tof\n\t  problems!!'
        expected = 'Text with all kinds of problems'
        cleaner = text_pipeline.WhitespaceCleaner()
        cleaner.attach_next(text_pipeline.PunctuationCleaner())
        result = cleaner.process(text)
        self.assertEqual(result, expected)

    def test_tokenizer(self):
        '''
        Test that the tokenizer works okay.
        '''
        text = 'Text,  that, is,\n gonna be split up... \t by a tokenizer!!'
        expected = ['Text that', 'is gonna', 'be split', 'up by',
                    'a tokenizer']
        cleaner = text_pipeline.WhitespaceCleaner()
        (cleaner.
         attach_next(text_pipeline.Tokenizer(2)).
         attach_next(text_pipeline.PunctuationCleaner()))
        result = cleaner.process(text)
        self.assertEqual(result, expected)

    def test_double_tokenization(self):
        '''
        Test that we can tokenize multiple times, with steps in the middle.
        '''
        text = ('Text,  that, is,\n gonna be split up... \t by a tokenizer!!' +
                ' extra word')
        expected = ['Text that', 'is gonna', 'be split', 'up by',
                    'a tokenizer', 'extra word']
        cleaner = text_pipeline.WhitespaceCleaner()
        (cleaner.
         attach_next(text_pipeline.Tokenizer(4)).
         attach_next(text_pipeline.PunctuationCleaner()).
         attach_next(text_pipeline.Tokenizer(2)))
        result = cleaner.process(text)
        self.assertEqual(result, expected)

    def test_mention_cleaner(self):
        '''
        Test that we can remove @mentions from text.
        '''
        text = "Hello @otheruser i'm mentioning you"
        expected = "Hello i'm mentioning you"
        cleaner = text_pipeline.MentionCleaner()
        cleaner.attach_next(text_pipeline.WhitespaceCleaner())
        result = cleaner.process(text)
        self.assertEqual(result, expected)

    def test_replacer(self):
        '''
        Test the replacer element.
        '''
        text = "Text #with #hashtags we don't #want"
        expected = "Text $with $hashtags we don't $want"
        cleaner = text_pipeline.Replacer('#', '$')
        result = cleaner.process(text)
        self.assertEqual(result, expected)
