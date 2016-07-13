#!/usr/bin/env python3

import namespaces
from abstract_worker import AbstractWorker
from clarifai.client import ClarifaiApi
from rdflib import URIRef, Literal, Namespace, XSD
from worker_util import create_annotation


ogp = URIRef('http://ogp.me/ns#tag:')
mcas = Namespace('http://s16a/vocab/mcas/1.0/')


class ClarifaiWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/clarifai'

    def process_data(self, url):
        url = url.decode('utf-8')
        annotations_filename = self.get_model_filename(url)

        clarifai_api = ClarifaiApi()
        response = clarifai_api.tag_image_urls(url)

        annotations = self.get_new_model()

        result = response['results'][0]['result']['tag']
        for tag, prob in zip(result['classes'], result['probs']):
            print('Tag: ' + tag + ' Prob: ' + str(prob))
            # model.add((tags, ogp + tag.replace(' ', '_'), Literal(prob)))
            annotation = create_annotation(
                                        (namespaces.oa.confidence, Literal(prob, datatype=XSD.decimal)),
                                        target=URIRef(url),
                                        body=Literal(tag, datatype=XSD.string),
                                        annotator=Literal('Clarif.ai', datatype=XSD.string))

        annotations += annotation
        self.write_and_merge_model(annotations, annotations_filename)


if __name__ == '__main__':
    worker = ClarifaiWorker()
    worker.start_worker()
