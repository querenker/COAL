import subprocess
import os
import glob
import tarfile
import shutil
from xml.etree import ElementTree
from pathlib import Path

test_data_directory = 'test-data/'


def extractTarGzFile(filename):
    try:
        tarfile.open(filename, 'r:gz').extractall(test_data_directory).close()
    except:
        return


def remove_unnecessary_files(directory):
    unnecessary_file_type_extensions = 'jpg gif cif hkl wav tif doc'.split()
    for extension in unnecessary_file_type_extensions:
        for file in glob.iglob(directory + '/*/*.' + extension):
            os.remove(file)


def remove_incomplete_data(test_data_directory):
    for directory in glob.glob(test_data_directory + '/*'):
        if len(glob.glob(directory + '/*.pdf')) != 1 or len(glob.glob(directory + '/*.nxml')) != 1:
            shutil.rmtree(directory)


def get_authors_from_xml(xml_document):
    file_directory = Path(xml_document).parent
    xmldoc = ElementTree.parse(xml_document).getroot()
    with open(str(file_directory) + '/authors.txt', 'w') as f: 
        for author in xmldoc.findall('.//contrib'):
            author_given_names = author.find('name/given-names').text
            author_surname = author.find('name/surname').text
            f.write(author_given_names + ' ' + author_surname + '\n')


def get_test_data(ftp_root_directory):
    root_directory = ftp_root_directory
    if ftp_root_directory.startswith('ftp://'):
        root_directory = ftp_root_directory[len('ftp://'):]
    root_directory = root_directory[:root_directory.find('/')]

    if not os.path.exists(root_directory):
        subprocess.run(['wget', '-r', ftp_root_directory])

    for file in glob.iglob('ftp*/**/*.tar.gz', recursive=True):
        extractTarGzFile(file)

    remove_unnecessary_files(test_data_directory)
    remove_incomplete_data(test_data_directory)


if __name__ == '__main__':
    get_test_data('ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/42/43/')
    for xml_file in glob.glob(test_data_directory + '/*/*.nxml'):
        get_authors_from_xml(xml_file)
