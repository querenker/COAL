#!/usr/bin/env python3

from abstract_worker import AbstractWorker
from json import loads
from langdetect import detect, lang_detect_exception
from rdflib import URIRef, Literal
from rdflib.namespace import XSD
from worker_util import get_cache_filename, create_annotation_for_model


class PdfTextLangdetectWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextlangdetect'

    def process_data(self, url):
        url = url.decode('utf-8')
        model_filename = get_cache_filename(url)
        json_filename = model_filename + '.data.txt.json'
        model = self.get_new_model()
        model_filename = self.get_model_filename(url)

        # model.add((BNode(), namespaces.mcas.pdftextlangdetect, tags))

        with open(json_filename, 'r') as json_file:
            langinfo, total = self.get_language_info(loads(json_file.read()))

        for language in langinfo.keys():
            percentage = langinfo[language] / total
            if percentage >= 0.2:
                print('language: ' + language + ' percentage: ' + str(langinfo[language] / total))
                # model.add((tags, namespaces.dcterms.language, Literal(langinfo[language] / total)))
                create_annotation_for_model(model,
                                            target=URIRef(url),
                                            body=Literal(language, datatype=XSD.string),
                                            annotator=Literal('LangDetect', datatype=XSD.string))

        self.write_and_merge_model(model, model_filename)

    def get_language_info(self, text_dict):
        langinfo = {}
        total = 0
        for paragraph in text_dict:
            title = paragraph['title']
            content = paragraph['content']
            for sentence in content:
                try:
                    language = detect(sentence)
                    total += 1
                    if language in langinfo.keys():
                        langinfo[language] += 1
                    else:
                        langinfo[language] = 1
                except lang_detect_exception.LangDetectException:
                    pass
        return (langinfo, total)


if __name__ == '__main__':
    worker = PdfTextLangdetectWorker()
    worker.start_worker()
