#!/usr/bin/env python3

import sys
from PyPDF2 import PdfFileReader

def get_info_for_file(filepath):
    reader = PdfFileReader(open(filepath, 'rb'))
    info = reader.getDocumentInfo()
    out = []
    for key in info:
        if info[key]:
            out.append((key[1:], info[key]))
    return out

def main():
    filepath = sys.argv[1]
    info = get_info_for_file(filepath)
    for key, value in info:
        print(key)
        print(value)

if __name__ == '__main__':
    main()
