#!/usr/bin/env python3

import namespaces
from abstract_worker import AbstractWorker
import operator
from os import path
from worker_util import create_annotation, get_cache_filename
from RAKE import rake
from rdflib import URIRef, Literal, Graph
from rdflib.namespace import XSD, RDF
import requests


kea_url = 'http://141.89.225.50/kea-2.0.1/services/annotate'

class PdfTextNamedEntityLinkingWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextnamedentitylinking'

    def process_data(self, url):
        url = url.decode('utf-8')
        annotations = self.get_new_model()
        annotations_filename = self.get_model_filename(url)
        pdf_filename = get_cache_filename(url) + '.data'
        text_filename = pdf_filename + '.txt'

        with open(text_filename, encoding='utf-8') as file:
            text = file.read()

        nif = Graph()
        data_uri = URIRef(url)

        nif.add((data_uri, RDF.type, namespaces.nif.RFC5147String))
        nif.add((data_uri, RDF.type, namespaces.nif.String))
        nif.add((data_uri, RDF.type, namespaces.nif.Context))

        nif.add((data_uri, namespaces.nif.isString, Literal(text, datatype=XSD.String)))

        nif_text = nif.serialize(format='turtle')

        print('lorem')
        response = requests.post(kea_url, data=nif_text)

        print(response.content)
        print('ipsum')

        self.write_and_merge_model(annotations, annotations_filename)


if __name__ == '__main__':
    worker = PdfTextNamedEntityLinkingWorker()
    worker.start_worker()
