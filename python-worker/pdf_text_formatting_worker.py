from abstract_worker import AbstractWorker
from json import dumps
from worker_util import get_cache_filename


class PdfTextFormattingWorker(AbstractWorker):

    queue_name = 'http://s16a.org/vocab/mcas/1.0/pdftextformatting'

    def process_data(self, url):
        url = url.decode('utf-8')
        filename = url
        document = []
        with open(filename, 'r') as text:
            paragraphs = text.read().split('\n\n')
            for paragraph in paragraphs:
                paragraph_entry = {}
                title = self.get_title(paragraph)
                paragraph_entry['title'] = title
                content = (paragraph[len(title) + 1:] if title != '' else paragraph).replace('\n', ' ').split('. ')
                for sententce_index in range(len(content) - 1):
                    content[sententce_index] += '.'
                paragraph_entry['content'] = content
                document.append(paragraph_entry)

        output_filename = filename + '.json'
        with open(output_filename, 'w') as output:
            output.write(dumps(document))

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
