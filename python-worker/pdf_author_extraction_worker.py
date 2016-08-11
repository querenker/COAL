#!/usr/bin/env python3

from abstract_worker import AbstractWorker
from author_candidate import AuthorCandidate
from os import path
from subprocess import call
from worker_util import get_cache_filename, create_annotation
from rdflib import URIRef, Literal
from rdflib.namespace import XSD
import re
import namespaces

class PdfAuthorExtractionWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdfauthorextraction'

    def __init__(self):
        self.stop_words = 'bureau univ school department institut ltd'.split()
         # first names borrowed from http://www.quietaffiliate.com/free-first-name-and-last-name-databases-csv-and-sql/
        with open('first_names.csv') as file:
            self.first_names = {name.strip().casefold() for name in file.read().split('\n')[1:]}

    def process_data(self, url):
        url = url.decode('utf-8')
        model = self.get_new_model()
        model_filename = get_cache_filename(url)
        pdf_filename = model_filename + '.data'
        text_filename = pdf_filename + '.txt'

        call(['pdftotext', pdf_filename, text_filename])
        
        with open(text_filename, 'r', encoding='ISO-8859-1') as file:
            text = file.read()

        annotation_filename = self.get_model_filename(url)
        annotations = self.get_new_model()

        for candidate in self.preprocess_input(text):
            candidate.calculate_confidences(self.stop_words, self.first_names)
            if candidate.confidence() >= 0.5:
                annotation = create_annotation(
                                            (namespaces.oa.score, Literal(candidate.confidence(), datatype=XSD.decimal)),
                                            target=URIRef(url),
                                            body=Literal(candidate.candidate_string, datatype=XSD.string),
                                            annotator=Literal('AuthorExtraction', datatype=XSD.string))
                annotations += annotation

        
        self.write_and_merge_model(annotations, annotation_filename)

    def preprocess_input(self, text):
        '''
        returns a list of AuthorCandidates, preprocessed by ignoring
        blank lines and merging multi line entries
        '''
        author_candidates = []
        current_entry = ''
        for line in text.split('\n')[:5]:
            for chunk in re.split(r',| and ', line):
                author_candidates.append(AuthorCandidate(chunk.strip()))
            
        return author_candidates


if __name__ == '__main__':
    worker = PdfAuthorExtractionWorker()
    worker.start_worker()
