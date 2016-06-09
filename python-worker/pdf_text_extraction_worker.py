from abstract_worker import AbstractWorker
from os import path
from subprocess import call
from worker_util import get_cache_filename


class PdfTextExtractionWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextextraction'

    def process_data(self, url):
        url = url.decode('utf-8')
        model_filename = get_cache_filename(url)
        pdf_filename = model_filename + '.data'
        text_filename = model_filename + '.txt'

        call(['pdftotext', pdf_filename, text_filename])

        self.send_to_queue('http://s16a.org/vocab/mcas/1.0/pdftextformatting',
                           path.abspath(text_filename))


if __name__ == '__main__':
    worker = PdfTextExtractionWorker()
    worker.start_worker()
