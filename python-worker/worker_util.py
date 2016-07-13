#!/usr/bin/env python3

import hashlib
import datetime
import re
import namespaces
from dateutil.tz import tzutc, tzoffset
from rdflib import BNode, RDF, Graph


def get_cache_filename(url):
    base_path = 'cache/'
    base_ext = '.ttl'
    hash = hashlib.md5()
    hash.update(url.encode('utf-8'))
    return base_path + hash.hexdigest()[:32] + base_ext


def create_annotation(*custom_properties, target, body, annotator):
    model = Graph() 
    annotationNode = BNode()
    model.add((annotationNode, RDF.type, namespaces.oa.Annotation))
    model.add((annotationNode, namespaces.oa.hasTarget, target))
    model.add((annotationNode, namespaces.oa.hasBody, body))
    model.add((annotationNode, namespaces.oa.annotatedBy, annotator))
    for rdf_property in custom_properties:
        model.add((annotationNode, rdf_property[0], rdf_property[1]))
    return model

# pdf date conversion code taken from http://stackoverflow.com/a/26796646
pdf_date_pattern = re.compile(''.join([
    r"(D:)?",
    r"(?P<year>\d\d\d\d)",
    r"(?P<month>\d\d)",
    r"(?P<day>\d\d)",
    r"(?P<hour>\d\d)",
    r"(?P<minute>\d\d)",
    r"(?P<second>\d\d)",
    r"(?P<tz_offset>[+-zZ])?",
    r"(?P<tz_hour>\d\d)?",
    r"'?(?P<tz_minute>\d\d)?'?"]))


def pdf_transform_date(date_str):
    """
    Convert a pdf date such as "D:20120321183444+07'00'" into a usable datetime
    http://www.verypdf.com/pdfinfoeditor/pdf-date-format.htm
    (D:YYYYMMDDHHmmSSOHH'mm')
    :param date_str: pdf date string
    :return: datetime object
    """
    global pdf_date_pattern
    match = re.match(pdf_date_pattern, date_str)
    if match:
        date_info = match.groupdict()

        for k, v in date_info.items():  # transform values
            if v is None:
                pass
            elif k == 'tz_offset':
                date_info[k] = v.lower()  # so we can treat Z as z
            else:
                date_info[k] = int(v)

        if date_info['tz_offset'] in ('z', None):  # UTC
            date_info['tzinfo'] = tzutc()
        else:
            multiplier = 1 if date_info['tz_offset'] == '+' else -1
            date_info['tzinfo'] = tzoffset(None, multiplier*(3600 * date_info['tz_hour'] + 60 * date_info['tz_minute']))

        for k in ('tz_offset', 'tz_hour', 'tz_minute'):  # no longer needed
            del date_info[k]

        return datetime.datetime(**date_info)
