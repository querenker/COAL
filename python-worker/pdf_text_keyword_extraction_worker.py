#!/usr/bin/env python3

from abstract_worker import AbstractWorker
from os import path
from worker_util import get_cache_filename
from 


class PdfTextKeywordExtractionWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextkeywordextraction'

    def process_data(self, url):
        url = url.decode('utf-8')
        model_filename = get_cache_filename(url)
        pdf_filename = model_filename + '.data'
        text_filename = pdf_filename + '.txt'

        with open(text_filename) as file:
            text = file.read()


if __name__ == '__main__':
    worker = PdfTextKeywordExtractionWorker()
    worker.start_worker()
