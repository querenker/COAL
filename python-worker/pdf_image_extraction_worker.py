#!/usr/bin/env python3

from abstract_worker import AbstractWorker
from os import path, makedirs
from subprocess import call
from worker_util import get_cache_filename


class PdfImageExtractionWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdfimageextraction'

    def process_data(self, url):
        url = url.decode('utf-8')
        model_filename = get_cache_filename(url)
        pdf_filename = model_filename + '.data'
        images_dir = pdf_filename + '-images/'

        if not path.exists(images_dir):
            makedirs(images_dir)

        call(['pdfimages', '-png', pdf_filename, images_dir])

        self.send_to_queue('http://s16a.org/vocab/mcas/1.0/clarifai', url)


if __name__ == '__main__':
    worker = PdfImageExtractionWorker()
    worker.start_worker()
