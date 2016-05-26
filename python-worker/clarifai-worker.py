from abstract_worker import AbstractWorker
from clarifai.client import ClarifaiApi
from worker_util import get_cache_filename
from rdflib import Literal


class ClarifaiWorker(AbstractWorker):

    def process_data(self, url):
        model_filename = get_cache_filename(url)
        model = self.open_model(model_filename)
        data_filename = get_cache_filename(url) + '.data'

        clarifai_api = ClarifaiApi()
        result = clarifai_api.tag_image_urls('url')

        model.add(Literal())
