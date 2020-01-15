# Packages
import pandas as pd
import re 
import spacy
from spacy import displacy
import numpy as np
import en_core_web_sm

# Local Imports
from app.get_tags import get_entity_tags,drop_subsets
from app import ent_df

def add_cust_ents(text,ent_df):
    '''Uses list of medical entities to tag their locations within a block of text.'''
    cust_ents = get_entity_tags(text,ent_df)
    ent_types = ["CONDITION","SYMPTOM","DRUG","UNIT","ROUTE"]
    cust_ents = [[x[0],x[1],x[2]] for x in cust_ents if x[2] in ent_types]
    return cust_ents

def add_doc_ents(text,nlp):
    '''Uses a NER model (nlp) to identify numeric and time based entities in a block of text.'''
    doc = nlp(text)
    ent_types = ["CARDINAL","QUANTITY","TIME","ORDINAL","PERCENT"]
    doc_ents = [[ent.start_char,ent.end_char,ent.label_] for ent in doc.ents if ent.label_ in ent_types]
    return doc_ents

def get_hybrid_tags(text,ent_df,nlp):
    '''Combines custom medical entity tagger with pretrained NER model to tag medical, numeric and time based entities'''
    cust_ents = add_cust_ents(text,ent_df)
    doc_ents = add_doc_ents(text,nlp)
    ents = sorted(cust_ents+doc_ents,key=lambda x: (x[0], x[1]))
    ents = drop_subsets(ents)
    return ents