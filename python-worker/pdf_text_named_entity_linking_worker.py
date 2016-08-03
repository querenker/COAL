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
from json import loads
import re


kea_url = 'http://141.89.225.50/kea-2.0.1/services/annotate'

class PdfTextNamedEntityLinkingWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextnamedentitylinking'

    def process_data(self, url):
        url = url.decode('utf-8')
        annotations = self.get_new_model()
        annotations_filename = self.get_model_filename(url)
        pdf_filename = get_cache_filename(url) + '.data'
        text_filename = pdf_filename + '.txt'
        model_filename = get_cache_filename(url)
        json_filename = model_filename + '.data.txt.json'

        # with open(json_filename, 'r') as json_file:
            # text_dict = loads(json_file.read())

        # for paragraph in text_dict:
            # title = paragraph['title']
            # content = paragraph['content']

            # for sentence in content:

                # nif = Graph()
                # data_uri = URIRef(url)
                # print(url)
                # print(data_uri)

                # ref = URIRef(url + '#char=0,' + str(len(sentence)))
                # print(ref)


                # nif.add((ref, RDF.type, namespaces.nif.RFC5147String))
                # nif.add((ref, RDF.type, namespaces.nif.String))
                # nif.add((ref, RDF.type, namespaces.nif.Context))

                # nif.add((ref, namespaces.nif.isString, Literal(sentence, datatype=XSD.String)))

                # nif_text = nif.serialize(format='turtle')

                # print('lorem')
                # response = requests.post(kea_url, data=nif_text)

                # print(response.content.decode('utf-8'))
                # print('ipsum')

        with open(text_filename, encoding='utf-8') as file:
            text = file.read()

        current_char_count = 0

        for sentence in re.split(r'((\.|\?|\!)(\s))', text):
            nif = Graph()
            data_uri = URIRef(url)
            print(url)
            print(data_uri)

            ref = URIRef(url + '#char=' + str(current_char_count) + ',' + str(current_char_count + len(sentence)))

            current_char_count += len(sentence) + 2

            print(ref)

            nif.add((ref, RDF.type, namespaces.nif.RFC5147String))
            nif.add((ref, RDF.type, namespaces.nif.String))
            nif.add((ref, RDF.type, namespaces.nif.Context))

            nif.add((ref, namespaces.nif.isString, Literal(sentence, datatype=XSD.String)))

            nif_text = nif.serialize(format='turtle')

            print('lorem')
            response = requests.post(kea_url, data=nif_text)

            print(response.content.decode('utf-8'))
            print('ipsum')
            

        self.write_and_merge_model(annotations, annotations_filename)


if __name__ == '__main__':
    worker = PdfTextNamedEntityLinkingWorker()
    worker.start_worker()
