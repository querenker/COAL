#!/usr/bin/env python3

from abstract_worker import AbstractWorker
from clarifai.client import ClarifaiApi
from rdflib import URIRef, Literal, Namespace, BNode


ogp = URIRef('http://ogp.me/ns#tag:')
mcas = Namespace('http://s16a/vocab/mcas/1.0/')


class ClarifaiWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/clarifai'

    def process_data(self, url):
        url = url.decode('utf-8')
        model = self.get_new_model()
        model_filename = self.get_model_filename(url)

        clarifai_api = ClarifaiApi()
        response = clarifai_api.tag_image_urls(url)

        data_uri = URIRef(url)
        tags = BNode()

        model.add((data_uri, mcas.clarifai, tags))

        result = response['results'][0]['result']['tag']
        for tag, prob in zip(result['classes'], result['probs']):
            print('Tag: ' + tag + ' Prob: ' + str(prob))
            model.add((tags, ogp + tag.replace(' ', '_'), Literal(prob)))

        self.write_and_merge_model(model, model_filename)


if __name__ == '__main__':
    worker = ClarifaiWorker()
    worker.start_worker()
