from abstract_worker import AbstractWorker
from subprocess import call
from worker_util import get_cache_filename


class PdfMetadataExtractionWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextextraction'

    def process_data(self, url):
        url = url.decode('utf-8')
        model_filename = get_cache_filename(url)
        pdf_filename = model_filename + '.data'
        text_filename = model_filename + '.txt'

        call(['pdftotext', pdf_filename, text_filename])


if __name__ == '__main__':
    worker = PdfMetadataExtractionWorker()
    worker.start_worker()
