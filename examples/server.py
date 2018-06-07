#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Coreference resolution server example.
A simple server serving the coreference system.
"""
from __future__ import unicode_literals

import sys
import json
from wsgiref.simple_server import make_server
import falcon
import spacy

IS_PYTHON2 = int(sys.version[0]) == 2
unicode_ = unicode if IS_PYTHON2 else str

class AllResource(object):
    def __init__(self):
        self.nlp = spacy.load('en_coref_sm')
        print("Server loaded")
        self.response = None

    def on_get(self, req, resp):
        self.response = {}

        text_param = req.get_param("text")
        if text_param is not None:
            text = ",".join(text_param) if isinstance(text_param, list) else text_param
            text = unicode_(text)
            doc = self.nlp(text)
            if doc._.has_coref:
                mentions = [{'start':    span.start_char,
                             'end':      span.end_char,
                             'text':     span.text,
                             'resolved': span._.coref_main_mention.text
                            } for span in doc._.coref_mentions]
                clusters = list(list(span.text for span in cluster)
                                for cluster in doc._.coref_clusters)
                resolved = doc._.coref_resolved
                self.response['mentions'] = mentions
                self.response['clusters'] = clusters
                self.response['resolved'] = resolved

        resp.body = json.dumps(self.response)
        resp.content_type = 'application/json'
        resp.append_header('Access-Control-Allow-Origin', "*")
        resp.status = falcon.HTTP_200

if __name__ == '__main__':
    RESSOURCE = AllResource()
    APP = falcon.API()
    APP.add_route('/', RESSOURCE)
    HTTPD = make_server('0.0.0.0', 8000, APP)
    HTTPD.serve_forever()
