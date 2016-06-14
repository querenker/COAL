from abstract_worker import AbstractWorker
from json import loads
from langdetect import detect, detect_langs, lang_detect_exception
from rdflib import URIRef, Literal, Namespace, BNode
from worker_util import get_cache_filename


ogp = URIRef('http://ogp.me/ns#language:')
mcas = Namespace('http://s16a/vocab/mcas/1.0/')


class PdfTextLangdetectWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextlangdetect'

    def process_data(self, url):
        url = url.decode('utf-8')
        filename = url
        model_filename = get_cache_filename(url)
        json_filename = model_filename + '.data.txt.json'
        model = self.get_new_model()
        model_filename = self.get_model_filename(url)

        data_uri = URIRef(url)
        tags = BNode()

        model.add((data_uri, mcas.pdftextlangdetect, tags))

        with open(json_filename, 'r') as json_file:
            langinfo, total = self.get_language_info(loads(json_file.read()))

        for language in langinfo.keys():
            percentage = langinfo[language] / total
            if percentage >= 0.2:
                print('language: ' + language + ' percentage: ' + str(langinfo[language] / total))
                model.add((tags, ogp + language, Literal(langinfo[language] / total)))

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
