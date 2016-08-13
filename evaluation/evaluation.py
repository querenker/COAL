#!/usr/bin/env python3

import os
import sys
import requests
from xml.etree import ElementTree
import subprocess
from unidecode import unidecode

sys.path.insert(0, '../python-worker/')
from author_candidate import AuthorCandidate

test_data_directory = 'test-data'


def compare_results(true_values, test_values, strict_comparison=True, case_sensitive=True):
    assert len(true_values) == len(test_values)
    true_positives = set()
    false_positives = set()
    false_negatives = set()
    for document in true_values:
        true_authors = set(true_values[document])
        find_authors = set(test_values[document])
        if not strict_comparison:
            true_authors = {unidecode(author) for author in true_authors}
            find_authors = {unidecode(author) for author in find_authors}
        if not case_sensitive:
            true_authors = {author.casefold() for author in true_authors}
            find_authors = {author.casefold() for author in find_authors}
        true_positives |= (true_authors & find_authors)
        false_positives |= (find_authors - true_authors)
        false_negatives |= (true_authors - find_authors)
    print("true positive: " + str(len(true_positives)))
    print("false positive: " + str(len(false_positives)))
    print("false negative: " + str(len(false_negatives)))
    # print("-------------------false positive------------")
    # print(', '.join(false_positives))
    # print("-------------------false negative------------")
    # print(', '.join(false_negatives))


def get_authors_from_file(authors_file):
    return {line.strip() for line in open(authors_file, 'r')}


def get_authors_from_cermine_response(xml_response):
    authors = set()
    xmldoc = ElementTree.fromstring(xml_response)
    for author in xmldoc.findall('.//contrib[@contrib-type="author"]'):
        authors.add(author.find('string-name').text)
    return authors


def extract_text(directory):
    subprocess.run('for file in ./test-data/*/*.pdf; do pdftotext $file; done', shell=True)


def get_author_mapping():
    author_mapping = dict()
    for path, _, files in os.walk(test_data_directory):
        if path == test_data_directory:
            continue
        for file in files:
            if file.endswith('.pdf'):
                pdf_file = os.path.join(path, file)
            if file == 'authors.txt':
                authors_file = os.path.join(path, file)
        author_mapping[pdf_file] = get_authors_from_file(authors_file)
    return author_mapping


def perform_cermine_algorithm(test_documents):
    cermine_results = dict()
    for document in test_documents:
        print(document + ' in process...')
        cermine_filename = document[:-3] + 'cermine'
        authors = set()
        if os.path.isfile(cermine_filename):
            print('data found in cache...')
            authors = get_authors_from_file(cermine_filename)
        else:
            data = open(document, 'rb').read()
            r = requests.post('http://cermine.ceon.pl/extract.do', data=data)
            if len(r.text) > 0:
                authors = get_authors_from_cermine_response(r.text)
        cermine_results[document] = authors
        with open(cermine_filename, 'w') as file:
            file.write('\n'.join(authors))
    return cermine_results


def perform_our_algorithm(test_documents):
    with open('../first-names/first_names.txt') as file:
        first_names = {name.strip().casefold() for name in file.read().split('\n')}
    with open('../words.txt') as file:
        known_words = {word.strip().casefold() for word in file.read().split('\n')}
    known_words -= first_names
    stop_words = 'bureau univ school department institut ltd article science abstract research state'.split()

    extract_text(test_data_directory)
    our_results = dict()
    for document in test_documents:
        print(document + ' in process...')
        coal_filename = document[:-3] + 'coal'
        authors = set()
        if os.path.isfile(coal_filename):
            print('data found in cache...')
            authors = get_authors_from_file(coal_filename)
        else:
            pdf_text = document[:-3] + 'txt'
            author_text = open(pdf_text, 'rb').read().decode('utf-8')
            authors = AuthorCandidate.get_authors_from_text(author_text, known_words, first_names, stop_words)
        our_results[document] = authors
        with open(coal_filename, 'w') as file:
            file.write('\n'.join(authors))
    return our_results


if __name__ == '__main__':
    author_mapping = get_author_mapping()
    cermine_results = perform_cermine_algorithm(author_mapping.keys())
    our_results = perform_our_algorithm(author_mapping.keys())
    print('cermine, strict, case sensitive')
    compare_results(author_mapping, cermine_results, strict_comparison=True, case_sensitive=True)
    print('coal, strict, case sensitive')
    compare_results(author_mapping, our_results, strict_comparison=True, case_sensitive=True)
    print('cermine, not strict, case insensitive')
    compare_results(author_mapping, cermine_results, strict_comparison=False, case_sensitive=False)
    print('coal, not strict, case insensitive')
    compare_results(author_mapping, our_results, strict_comparison=False, case_sensitive=False)
