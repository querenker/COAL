#!/usr/bin/env python3

from abstract_worker import AbstractWorker
from json import dumps
import nltk
from worker_util import get_cache_filename


class PdfTextFormattingWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextformatting'

    def process_data(self, url):
        url = url.decode('utf-8')
        filename = url
        model_filename = get_cache_filename(url)
        txt_filename = model_filename + '.data.txt'
        document = []
        with open(txt_filename, 'r') as text:
            paragraphs = text.read().split('\n\n')
            for paragraph in paragraphs:
                paragraph_entry = {}
                title = self.get_title(paragraph)
                paragraph_entry['title'] = title
                content = nltk.sent_tokenize((paragraph[len(title) + 1:] if title != '' else paragraph))
                paragraph_entry['content'] = content
                document.append(paragraph_entry)

        output_filename = txt_filename + '.json'
        with open(output_filename, 'w') as output:
            output.write(dumps(document))

        self.send_to_queue('http://s16a.org/vocab/mcas/1.0/pdftextlangdetect',
                           url)

    def get_title(self, paragraph):
        sentences = paragraph.split('\n')
        if len(sentences) < 2:
            return ''
        elif len(sentences[0]) * 2 < len(sentences[1]):
            return sentences[0]
        return ''

if __name__ == '__main__':
    worker = PdfTextFormattingWorker()
    worker.start_worker()
