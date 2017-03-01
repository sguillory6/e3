import random
import string


class RandomWords:
    """
    Generate random words using the un*x word package
    """
    WORDS = "/usr/share/dict/words"

    def __init__(self, use_dictionary=False):
        if use_dictionary:
            try:
                with open(self.WORDS, "r") as words:
                    self.words = filter(lambda x: not x.endswith("'s"), words.read().splitlines())
            except StandardError:
                raise IOError("Unable to open words file: '%s'" % self.WORDS)
        else:
            self.words = None

    def random_word(self):
        if self.words:
            return random.choice(self.words)
        else:
            return self.random_string(10)

    def random_sentence(self, no_words=2):
        if self.words:
            return ' '.join(random.choice(self.words) for _ in range(no_words))
        else:
            return ' '.join(self.random_string(15) for _ in range(no_words))

    @staticmethod
    def random_string(word_len, source=string.lowercase):
        return ''.join(random.choice(source) for _ in range(word_len))
