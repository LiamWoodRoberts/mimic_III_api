# Module Imports
from app import api, ent_df, nlp
from app.get_tags import get_entity_tags, get_drugs_and_conditions
from app.hybrid_model import clean_text, get_hybrid_tags

# Package Imports
from flask_restplus import Resource, reqparse
from flask import render_template, request, jsonify, url_for, redirect
import requests
import json

# Arguments for metrics,eval,and predict api post requests
parser = reqparse.RequestParser()
parser.add_argument('text', type=str)


@api.route("/get_tags")
class tagger(Resource):
    def post(self):
        '''
        Description: Uses a rule based approach to identify medical and numeric entities.

        Input: String of text
        Output: "Spacy Formatted" Entity Tags for text
        '''
        args = parser.parse_args()
        text = str(args['text'])
        entity_tags = get_entity_tags(text, ent_df)
        return entity_tags


@api.route("/drugs_and_conditions")
class drugs_and_conditions(Resource):
    def post(self):
        '''
        Description: Uses rule-based tagger to identify unique drugs and conditions in text.

        Input: String of text
        Output: JSON Dictionary with "DRUGS" and "CONDITIONS" containing lists of respective entities
        '''
        args = parser.parse_args()
        text = str(args["text"])
        entity_tags = get_entity_tags(text, ent_df)
        drugs_and_conditions = get_drugs_and_conditions(entity_tags)
        return drugs_and_conditions


@api.route("/hybrid_tagger")
class hybrid_tagger(Resource):
    def post(self):
        '''
        Description: Uses a pre-trained Spacy and a rule-based model to identify numeric and medical entities

        Input: String of text
        Output: "Spacy Formatted" Entity Tags for text
        '''
        args = parser.parse_args()
        text = str(args["text"])
        tags = get_hybrid_tags(text, ent_df, nlp)
        return tags
