#!/usr/bin/env python3

from abstract_worker import AbstractWorker
from os import path
from subprocess import call
from worker_util import get_cache_filename, create_annotation
from rdflib import URIRef, Literal
from rdflib.namespace import XSD
import namespaces


class PdfTextExtractionWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextextraction'

    def process_data(self, url):
        url = url.decode('utf-8')
        model = self.get_new_model()
        model_filename = get_cache_filename(url)
        model_worker_filename = self.get_model_filename(url)
        pdf_filename = model_filename + '.data'
        text_filename = pdf_filename + '.txt'

        data_uri = URIRef(url)

        call(['pdftotext', pdf_filename, text_filename])
        
        with open(text_filename, 'r', encoding='UTF-8') as file:
            text = file.read()

        # create_annotation_for_model(model,
                                    # # (namespaces.oa.percentage, Literal(langinfo[language] / total, datatype=XSD.decimal)),
                                    # target=URIRef(url),
                                    # body=Literal(text, datatype=XSD.string),
                                    # annotator=Literal('TextExtraction', datatype=XSD.string))

        # self.write_and_merge_model(model, model_filename)
        
        model.add((data_uri, namespaces.oa.fulltext, Literal(text, datatype=XSD.string)))
        self.write_and_merge_model(model, model_worker_filename)
                   
        self.send_to_queue('http://s16a.org/vocab/mcas/1.0/pdftextformatting',
                           url)
        self.send_to_queue('http://s16a.org/vocab/mcas/1.0/pdfauthorextraction',
                           url)
        self.send_to_queue('http://s16a.org/vocab/mcas/1.0/pdftextkeywordextraction',
                           url)
        self.send_to_queue('http://s16a.org/vocab/mcas/1.0/pdftextnamedentitylinking',
                           url)


if __name__ == '__main__':
    worker = PdfTextExtractionWorker()
    worker.start_worker()
