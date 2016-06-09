from abstract_worker import AbstractWorker
from PyPDF2 import PdfFileReader
from worker_util import get_cache_filename
from rdflib import URIRef, Literal, Namespace, BNode


ogp = URIRef('http://ogp.me/ns#pdfmeta:')
mcas = Namespace('http://s16a/vocab/mcas/1.0/')


class PdfMetadataExtractionWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdfmetadataextraction'

    def process_data(self, url):
        url = url.decode('utf-8')
        model_filename = get_cache_filename(url)
        model = self.get_new_model()

        data_filename = model_filename + '.data'

        data_uri = URIRef(url)
        tags = BNode()

        model.add((data_uri, mcas.pdfmetadataextraction, tags))

        info = self.get_info_for_file(data_filename)
        for key, value in info:
            print('Key: ' + key + ' Value: ' + value)
            model.add((tags, ogp + key.replace(' ', '_'), Literal(value)))

        self.write_and_merge_model(model, model_filename)

    def get_info_for_file(self, filepath):
        reader = PdfFileReader(open(filepath, 'rb'))
        info = reader.getDocumentInfo()
        out = []
        for key in info:
            if info[key]:
                out.append((key[1:], info[key]))
        return out

if __name__ == '__main__':
    worker = PdfMetadataExtractionWorker()
    worker.start_worker()
