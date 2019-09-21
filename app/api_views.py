# Module Imports
from app import api,ent_df
from app.get_tags import get_entity_tags

# Package Imports
from flask_restplus import Resource,reqparse
from flask import render_template,request,jsonify,url_for,redirect
import requests
import json

# Arguments for metrics,eval,and predict api post requests
parser = reqparse.RequestParser()
parser.add_argument('text',type=str)

@api.route("/get_tags")
class tagger(Resource):
    def post(self):
        '''returns model predictions for a defined sample'''
        args = parser.parse_args()
        text = str(args['text'])
        entity_tags = get_entity_tags(text,ent_df)
        return entity_tags