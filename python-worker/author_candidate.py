import re
from math import sqrt

class AuthorCandidate:
    def __init__(self,
                 candidate_string,
                 stop_word_confidence = 0,
                 known_name_confidence = 0,
                 known_title_confidence = 0,
                 name_pattern_confidence = 0,
                 name_word_count_confidence = 0,
                 digit_word_count_confidence = 0,
                 known_word_confidence = 0):

        self.candidate_string = candidate_string
        self.stop_word_confidence = stop_word_confidence
        self.known_name_confidence = known_name_confidence
        self.known_title_confidence = known_title_confidence
        self.name_pattern_confidence = name_pattern_confidence
        self.name_word_count_confidence = name_word_count_confidence
        self.digit_word_count_confidence = digit_word_count_confidence
        self.known_word_confidence = known_word_confidence

    def score(self):
        return (self.stop_word_confidence * 10) \
            + (self.known_name_confidence * 4) \
            + (self.known_title_confidence * 4) \
            + (self.name_pattern_confidence * 2) \
            + (self.name_word_count_confidence * .5) \
            + (self.digit_word_count_confidence * 1) \
            + (self.known_word_confidence * 1)

    def confidence(self):
        return 1 - (1 / sqrt(max(self.score(), 1)))

    def calculate_confidences(self, stop_words, first_names, known_words):
        self.calculate_stop_word_confidence(stop_words)
        self.calculate_author_pattern_confidence()
        self.calculate_known_name_confidence(first_names)
        self.calculate_known_title_confidence()
        self.calculate_name_word_count_confidence()
        self.calculate_digit_word_count_confidence()
        self.calculate_known_word_confidence(known_words)


    def sanitized_candidate(self):
        print(self)
        author = self.candidate_string
        author = ''.join(c for c in author if c.isalpha() or c in {' ', '.', '-', '’', chr(0x02ca), chr(0x00b4), chr(0x0301)}).strip()
        author = re.sub(r'^\w | \w$', '', author)
        if author.isupper():
            author = author.title()
        return author

    def calculate_stop_word_confidence(self, stop_words):
        'if one stop word is included, the specific confidence becomes 0, otherwise 1'
        self.stop_word_confidence = 0
        for stop_word in stop_words:
            if stop_word in self.candidate_string.casefold():
                self.stop_word_confidence -= 1

    def calculate_author_pattern_confidence(self):
        'based on whether or not the words e.g. begin with an uppercase letter'
        self.name_pattern_confidence = 0
        if len(self.candidate_string) > 0 and all(map(lambda x: x[0].isupper(), self.candidate_string.replace('and', '').split())):
            self.name_pattern_confidence = 1
        if sum(1 for c in self.candidate_string if c.isupper()) == 0:
            self.name_pattern_confidence = -1

    def calculate_known_name_confidence(self, first_names):
        'based on whether or not the candidate includes an entry from a list of known names; name set has to be lowercase'
        # remove digits and split at commas and 'and's
        self.known_name_confidence = 0
        words = re.split(r' |,|and', ''.join([i for i in self.candidate_string if not i.isdigit()]))
        for word in words[:-1]:
            if word and word[0].isupper():
                if len(word) == 2 and word[1] == '.':
                    self.known_name_confidence += 1
                elif word.strip().casefold() in first_names:
                    self.known_name_confidence += 1

    def calculate_known_title_confidence(self):
        'based on whether or not the candidate includes an entry from a list of known titles, like Dr., or Prof.'
        # remove digits and split at commas and 'and's
        self.known_title_confidence = 0
        known_titles = {'dr.', 'prof.', 'b.sc.', 'phd', 'ph.d.', 'dphil'}
        for word in re.split(r' |,|and', ''.join([i for i in self.candidate_string if not i.isdigit()])):
            if word.casefold() in known_titles:
                self.known_title_confidence += 1

    def calculate_name_word_count_confidence(self):
        '''based on the number of words the candidate consists of, a confidence is calculated.
        Normaly a name consists of two words (first and last name) but some more words are also common (multiple first names)'''
        word_count = sum(1 for word in self.candidate_string.split() if len(word) > 0 and word[0].isalpha())
        if word_count < 2:
            self.name_word_count_confidence = -16
        elif word_count == 2:
            self.name_word_count_confidence = 4
        elif word_count == 3:
            self.name_word_count_confidence = 3
        elif word_count == 4:
            self.name_word_count_confidence = 1
        elif word_count == 5:
            self.name_word_count_confidence = 0
        else:
            self.name_word_count_confidence = -2

    def calculate_digit_word_count_confidence(self):
        '''based on the number of digits in the words of the candidate a confidence is calculated.
        Normaly a name does not includ digits, but through the PDF to Text procedure footnote referenced are part of some candidates'''
        self.digit_word_count_confidence = 0
        for word in self.candidate_string.split():
            digit_count = sum(1 for c in word if c.isdigit())
            if digit_count < 2:
                self.digit_word_count_confidence += 0
            elif digit_count == 2:
                self.digit_word_count_confidence += -1
            elif digit_count == 3:
                self.digit_word_count_confidence += -2
            else:
                self.digit_word_count_confidence += -4

    def calculate_known_word_confidence(self, known_words):
        self.known_word_confidence = 0
        words = self.candidate_string.split() 
        for word in words[:-1]:
            if word.casefold() in known_words:
                self.known_word_confidence -= 2
        if words and words[-1].casefold() in known_words:
            self.known_word_confidence -= 1


    def __repr__(self):
        return 'AuthorCandidate(' + str(round(self.confidence(), 3)) + ' \'' + self.candidate_string + '\' [' + \
                 str(self.stop_word_confidence) + ' ' + \
                 str(self.known_name_confidence) + ' ' + \
                 str(self.known_title_confidence) + ' ' + \
                 str(self.name_pattern_confidence) + ' ' + \
                 str(self.name_word_count_confidence) + ' ' + \
                 str(self.known_word_confidence) + ' ' + \
                 str(self.digit_word_count_confidence) + ']' + ')'

    def preprocess_input(text):
        '''
        returns a list of AuthorCandidates, preprocessed by ignoring
        blank lines and merging multi line entries
        '''
        author_candidates = []
        for line in text.split('\n')[:20]:
            line = re.sub(r'\s+', ' ', line)
            for chunk in re.split(r',| and | AND | And | & ', line):
                chunk = re.split(r'( |^)(by|BY|By) |: ', chunk)[-1]
                chunk = re.sub(r' \w$', '', chunk)
                chunk = re.sub(r'^(and|AND|And) | (and|AND|And)$', '', chunk)
                author_candidates.append(AuthorCandidate(chunk.strip()))
        return author_candidates

    def get_authors_from_text(text, known_words, first_names, stop_words, min_confidence=0.5):
        authors = set()
        for candidate in AuthorCandidate.preprocess_input(text):
            candidate.calculate_confidences(stop_words, first_names, known_words)
            if candidate.confidence() >= min_confidence:
                authors.add(candidate.sanitized_candidate())
        return authors
