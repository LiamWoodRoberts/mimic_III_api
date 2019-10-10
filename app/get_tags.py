import pandas as pd
import re
import spacy
from spacy import displacy
import numpy as np

def in_text(x,text):
    if f"{x}" in text.lower():
        return True
    else:
        return False
    
def add_ent_matches(text,entities):
        matches = []
        for name,ent_type in entities:
            ent_matches = re.finditer(f"[^a-zA-Z0-9\.]{name}[^a-zA-Z0-9\.]" ,text.lower())
            for match in ent_matches:
                matches.append([match.start()+1,match.end()-1,ent_type,name])
        return matches
    
def add_pattern_matches(text):
    matches = []
    patterns = ["[^a-zA-Z]\d+\.\d+[^a-zA-Z\.]","[^a-zA-Z]\d+\-\d+[^a-zA-Z\.]"]
    for pattern in patterns:
        pat_matches = re.finditer(pattern,text.lower())
        for match in pat_matches:
            matches.append([match.start()+1,match.end()-1,'CARDINAL',match])
    ord_matches = re.finditer(r"\n\d+\.",text.lower())
    for match in ord_matches:
        matches.append([match.start()+1,match.end()-1,'ORDINAL',match])
    return matches

def drop_subsets(matches):
    reduced = []
    last_end = 0

    for i in range(len(matches)-1):
        # starts at same place
        case1 = matches[i+1][0]!= matches[i][0]
        
        # starts at different place but ends at same place
        case2 = matches[i][1] > matches[i-1][1]

        if case1:
            if i:
                past_last = matches[i][1] > last_end
                if case2 and past_last:
                    reduced.append(matches[i])
                    last_end = matches[i][1]
            else:
                reduced.append(matches[i])
    return reduced

def get_ent_locs(text,entities):
    ent_matches = add_ent_matches(text,entities)
    pat_matches = add_pattern_matches(text)
    matches = ent_matches+pat_matches
    matches = sorted(matches,key=lambda x: (x[0], x[1]))
    return drop_subsets(matches)

def show_ents(text,entities):
    ents = [{"start":x[0],"end":x[1],"label":x[2]} for x in entities]
    ex = [{"text":text,
       "ents":ents}
         ]
    colors = {"DRUG": "rgb(60,180,240)","DOSE":"rgb(240,180,60)","ROUTE":"rgb(200,200,200)"}
    options = {"colors":colors}
    html = displacy.render(ex,style="ent",manual=True,options=options,jupyter=True)
    return

def get_entity_tags(text,ent_df):
    ent_df["in_text"] = ent_df["Name"].apply(lambda x:in_text(x,text.lower()))
    entities = ent_df[ent_df["in_text"]][["Name","Entity"]].values
    ent_locs = get_ent_locs(text.lower(),entities)
    return ent_locs

def clean_text(text):
    bad_chars = [":","*"]
    space_chars = ["[","]","(",")","\n"]
    for c in bad_chars:
        text = text.replace(c,"")
    for c in space_chars:
        text = text.replace(c," ")
    return text

def get_drugs_and_conditions(ent_locs):
    drug_list = list(set([i[3] for i in ent_locs if i[2] == "DRUG"]))
    condition_list = list(set([i[3] for i in ent_locs if i[2] in ["CONDITION","SYMPTOM"]]))
    return {"DRUGS":drug_list,"CONDITIONS":condition_list}

def load_ent_df():
    ent_df = pd.read_csv("./app/entities.csv")
    bad_ents = ["solution","dose","lot","enema","-","in","can","pack","ring","bar","bags","cart","jar","pad","as","it","in"]
    ent_df = ent_df[ent_df["Name"].isin(bad_ents)==0].copy()
    return ent_df

if __name__ == "__main__":
    text = "DISCHARGE MEDICATIONS: \n1. aspirin 500 mg tablet twice (2) a day as needed for pain \n2. Oxacillin 2 mg as needed for pain \n"
    text = clean_text(text)
    ent_df = load_ent_df()
    ent_locs = get_entity_tags(text,ent_df)
    drugs_and_conditions = get_drugs_and_conditions(ent_locs)
    print(drugs_and_conditions)