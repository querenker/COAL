#!/usr/bin/env python3

import namespaces
from abstract_worker import AbstractWorker
import operator
from os import path
from worker_util import create_annotation, get_cache_filename
from RAKE import rake
from rdflib import URIRef, Literal, Graph, BNode
from rdflib.namespace import XSD, RDF, DC
import requests
from json import loads
import re


kea_url = 'http://141.89.225.50/kea-2.0.1/services/annotate'
max_length = 1000

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

        with open(text_filename, encoding='utf-8') as file:
            text = file.read()

        current_char_count = 0
        
        annotations = self.get_new_model()

        for sentence in re.split(r'((\.|\?|\!)(\s))', text):
            nif = Graph()
            data_uri = URIRef(url)
            print(url)
            print(data_uri)

            ref = URIRef(url + '#char=' + str(0) + ',' + str(len(sentence))) # TODO: fix offsets (when supported by server)

            nif.add((ref, RDF.type, namespaces.nif.RFC5147String))
            nif.add((ref, RDF.type, namespaces.nif.String))
            nif.add((ref, RDF.type, namespaces.nif.Context))

            nif.add((ref, namespaces.nif.isString, Literal(sentence, datatype=XSD.String)))
            nif_text = nif.serialize(format='turtle')

            response = requests.post(kea_url, data=nif_text)
            response_graph = Graph()
            response_graph.parse(format='turtle', data=response.content)

            for subject in set(response_graph.subjects()):
                # exceptions are ignored, because reformat_response_graph will fail when the given subject isn't a keyword that is recognized by kea, so that it won't be returned in our results
                try:
                    annotation = self.__class__.reformat_response_graph(response_graph, subject, current_char_count)
                    annotations += annotation
                except:
                    pass
                                                       
            current_char_count += len(sentence) + 2
            if current_char_count > max_length:
                break

        self.write_and_merge_model(annotations, annotations_filename)

    def reformat_response_graph(graph, subject, offset):
        """
        Extracts a subgraph for a single found keyword (if existing), adds an offset to the character positions and returns that graph
        (as a temporary woraround while the kea service doesn't handle offsets correctly)
        """

        # generate new subject considering offset
        match = re.search(r'^(?P<baseurl>.*)#char=(?P<begin>\d+),(?P<end>\d+)$', subject)
        new_subject = URIRef(match.group('baseurl') + '#char=' + str(int(match.group('begin')) + offset) + ',' + str(int(match.group('end')) + offset))

        model = Graph()
        annotationNode = BNode()

        model.add((annotationNode, RDF.type, namespaces.oa.Annotation))
        model.add((annotationNode, namespaces.oa.hasTarget, new_subject))
        model.add((annotationNode, namespaces.oa.hasBody, graph.value(subject, predicate=namespaces.itsrdf.taIdentRef)))
        model.add((annotationNode, namespaces.oa.annotatedBy, graph.value(subject, predicate=DC.creator)))
        
        # model.add((annotationNode, RDF.type, graph.value(subject, predicate=RDF.type)))
        model.add((annotationNode, namespaces.nif.anchorOf, graph.value(subject, predicate=namespaces.nif.anchorOf)))
        model.add((annotationNode, namespaces.nif.beginIndex, graph.value(subject, predicate=namespaces.nif.beginIndex) + offset))
        model.add((annotationNode, namespaces.nif.endIndex, graph.value(subject, predicate=namespaces.nif.endIndex) + offset))
        model.add((annotationNode, namespaces.itsrdf.taConfidence, graph.value(subject, predicate=namespaces.itsrdf.taConfidence)))

        return model


if __name__ == '__main__':
    worker = PdfTextNamedEntityLinkingWorker()
    worker.start_worker()
