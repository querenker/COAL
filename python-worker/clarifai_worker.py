#!/usr/bin/env python3

import namespaces
from abstract_worker import AbstractWorker
from clarifai.client import ClarifaiApi
from rdflib import URIRef, Literal, Namespace, XSD
from worker_util import create_annotation, get_cache_filename
import os


ogp = URIRef('http://ogp.me/ns#tag:')
mcas = Namespace('http://s16a/vocab/mcas/1.0/')


class ClarifaiWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/clarifai'

    def process_data(self, url):
        url = url.decode('utf-8')
        annotations_filename = self.get_model_filename(url)
        model_filename = get_cache_filename(url)
        pdf_filename = model_filename + '.data'
        images_dir = pdf_filename + '-images/'

        clarifai_api = ClarifaiApi()

        annotations = self.get_new_model()

        for file in os.listdir(images_dir):
            if file.endswith(".png"):
                response = clarifai_api.tag_images(open(images_dir + file, 'rb'))
                result = response['results'][0]['result']['tag']
                for tag, prob in zip(result['classes'], result['probs']):
                    print('Tag: ' + tag + ' Prob: ' + str(prob))
                    annotation = create_annotation(
                                                (namespaces.oa.confidence, Literal(prob, datatype=XSD.decimal)),
                                                target=URIRef(url) + '#image' + file,
                                                body=Literal(tag, datatype=XSD.string),
                                                annotator=Literal('Clarif.ai', datatype=XSD.string))

                annotations += annotation
        self.write_and_merge_model(annotations, annotations_filename)


if __name__ == '__main__':
    worker = ClarifaiWorker()
    worker.start_worker()
