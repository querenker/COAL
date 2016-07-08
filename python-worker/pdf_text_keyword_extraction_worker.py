#!/usr/bin/env python3

from abstract_worker import AbstractWorker
import operator
from os import path
from worker_util import get_cache_filename
from RAKE import rake


class PdfTextKeywordExtractionWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextkeywordextraction'

    def process_data(self, url):
        url = url.decode('utf-8')
        model_filename = get_cache_filename(url)
        pdf_filename = model_filename + '.data'
        text_filename = pdf_filename + '.txt'

        with open(text_filename) as file:
            text = file.read()

        sentence_list = rake.split_sentences(text) # TODO: probably smarter by using nltk / json sentence list?
        stopword_path = path.dirname(path.realpath(__file__)) + '/RAKE/SmartStoplist.txt'
        stopword_pattern = rake.build_stop_word_regex(stopword_path)
        phrase_list = rake.generate_candidate_keywords(sentence_list, stopword_pattern)
        word_scores = rake.calculate_word_scores(phrase_list)
        keyword_candidates = rake.generate_candidate_keyword_scores(phrase_list, word_scores)
        sorted_keywords = sorted(keyword_candidates.items(), key=operator.itemgetter(1), reverse=True)
        total_keywords = len(sorted_keywords)
        print(sorted_keywords[0:(total_keywords // 3)])


if __name__ == '__main__':
    worker = PdfTextKeywordExtractionWorker()
    worker.start_worker()
