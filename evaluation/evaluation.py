import os
import requests
from xml.etree import ElementTree


test_data_directory = 'test-data'


def compare_results(true_values, test_values):
    assert len(true_values) == len(test_values)
    true_positive_count = 0
    false_positive_count = 0
    false_negative_count = 0
    for document in true_values:
        true_authors = true_values[document]
        find_authors = test_values[document]
        true_positive_count += len(true_authors & find_authors)
        false_positive_count += len(find_authors - true_authors)
        false_negative_count += len(true_authors - find_authors)
    print("true positive: " + str(true_positive_count))
    print("false positive: " + str(false_positive_count))
    print("false negative: " + str(false_negative_count))


def get_authors_from_file(authors_file):
    return {line.strip() for line in open(authors_file, 'r')}


def get_author_from_cermine_response(xml_response):
    authors = set()
    xmldoc = ElementTree.fromstring(xml_response)
    for author in xmldoc.findall('.//contrib[@contrib-type="author"]'):
        authors.add(author.find('string-name').text)
    return authors


def get_author_mapping():
    author_mapping = dict()
    for path, _, files in os.walk(test_data_directory):
        if path == test_data_directory:
            continue
        for file in files:
            if file.endswith('.pdf'):
                pdf_file = os.path.join(path, file)
            if file.endswith('.txt'):
                authors_file = os.path.join(path, file)
        author_mapping[pdf_file] = get_authors_from_file(authors_file)
    return author_mapping


def perform_cermine_algorithm(test_documents):
    cermine_results = dict()
    for document in test_documents:
        print(document + ' in process...')
        data = open(document, 'rb').read()
        r = requests.post('http://cermine.ceon.pl/extract.do', data=data)
        cermine_results[document] = get_author_from_cermine_response(r.text)
    return cermine_results


if __name__ == '__main__':
    author_mapping = get_author_mapping()
    cermine_results = perform_cermine_algorithm(author_mapping.keys())
    compare_results(author_mapping, cermine_results)
