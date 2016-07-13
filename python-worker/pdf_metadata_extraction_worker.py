#!/usr/bin/env python3

from abstract_worker import AbstractWorker
from PyPDF2 import PdfFileReader
from worker_util import get_cache_filename, pdf_transform_date, create_annotation_for_model
from rdflib import URIRef, Literal, BNode
from rdflib.namespace import XSD, DCTERMS
import namespaces


class PdfMetadataExtractionWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdfmetadataextraction'

    def process_data(self, url):
        url = url.decode('utf-8')
        model_filename = self.get_model_filename(url)
        model = self.get_new_model()

        data_filename = get_cache_filename(url) + '.data'

        data_uri = URIRef(url)
        # tags = BNode()
        # model.add((data_uri, namespaces.mcas.pdfmetadataextraction, tags))

        info = self.__class__.get_info_for_file(data_filename)
        for key, value in info:
            print('Key: ' + key + ' Value: ' + value)
            property = self.__class__.get_property_for_key(key)
            if property:
                if 'Date' in key:
                    model.add((data_uri, property, Literal(pdf_transform_date(value), datatype=XSD.date)))
                else:
                    model.add((data_uri, property, Literal(value, datatype=XSD.string)))
            elif key == '/Keywords':
                create_annotation_for_model(model,
                                            # (namespaces.oa.percentage, Literal(langinfo[language] / total, datatype=XSD.decimal)),
                                            target=URIRef(url),
                                            body=Literal(value, datatype=XSD.string),
                                            annotator=Literal('PdfMetadata', datatype=XSD.string))

        self.write_and_merge_model(model, model_filename)

    def get_info_for_file(filepath):
        reader = PdfFileReader(open(filepath, 'rb'))
        info = reader.getDocumentInfo()
        out = []
        for key in info:
            if info[key]:
                out.append((key, info[key]))

        return out

    def get_property_for_key(key):
        mapping = {
            '/Author': DCTERMS.creator,
            '/CreationDate': DCTERMS.created,
            # '/Keywords': namespaces.dcterms.loremipsum,
            '/ModDate': DCTERMS.modified,
            '/Subject': DCTERMS.subject,
            '/Title': DCTERMS.title
        }
        return mapping.get(key)


if __name__ == '__main__':
    worker = PdfMetadataExtractionWorker()
    worker.start_worker()
