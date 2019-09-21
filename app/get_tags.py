import pandas as pd
import re
import spacy
from spacy import displacy
import numpy as np

def load_drug_entities():
    drugs = np.load("./app/static/data/drug_entities.npy")
    drugs = [d.lower() for d in drugs if (len(d)>4)]
    non_ents = ["solution"]
    for ent in non_ents:
        drugs.remove(ent)
    drugs = list(set(drugs))
    #drugs = add_single_words(drugs,l=4)
    return drugs

def load_dose_entities():
    doses = np.load("./app/static/data/dose_entities.npy")
    doses = [d.lower() for d in doses if len(d)>1]
    return list(set(doses))

def load_unit_entities():
    ents = np.load("./app/static/data/unit_entities.npy")
    ents = [ent.lower() for ent in ents]
    return list(set(ents))

def load_route_entities():
    routes = np.load("./app/static/data/route_entities.npy")
    routes = [d.lower() for d in routes if d.lower()!='as']
    routes = set(routes)
    return list(routes)
def create_ent_df():
    drugs = pd.DataFrame()
    drugs["Name"] = load_drug_entities()
    drugs["Entity"] = 'DRUG'
    
    doses = pd.DataFrame()
    doses["Name"] = load_dose_entities()
    doses["Entity"] = 'DOSE'
    
    routes = pd.DataFrame()
    routes["Name"] = load_route_entities()
    routes["Entity"] = 'ROUTE'
    
    unit = pd.DataFrame()
    unit["Name"] = load_unit_entities()
    unit["Entity"] = 'UNIT'
    
    other_ents = pd.DataFrame()
    names = [
            "a day",
            "daily",
            "hours",
            "hr",
            "every",
            "as needed",
            "delayed release",
            "extended release",
            "sustained release",
            "refills",
            "disp",
             ]
    numbers = [str(i) for i in range(100)]
    numbers = numbers+["1-2","1-3","1-4","2-4"]
    
    other_ents["Name"] = names+numbers                    
    other_ents["Entity"] = ["Frequency"]*6+["ROUTE"]*2+["DOSE"]*3+["CARDINAL"]*104
    
    df = pd.concat([drugs,unit,doses,routes,other_ents],axis=0)
    
    return df

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
                matches.append([match.start()+1,match.end()-1,ent_type])
        return matches
    
def add_pattern_matches(text):
    matches = []
    patterns = ["[^a-zA-Z]\d+\.\d+[^a-zA-Z\.]","[^a-zA-Z]\d+\-\d+[^a-zA-Z\.]"]
    for pattern in patterns:
        pat_matches = re.finditer(pattern,text.lower())
        for match in pat_matches:
            matches.append([match.start()+1,match.end()-1,'CARDINAL'])
    ord_matches = re.finditer(r"\n\d+\.",text.lower())
    for match in ord_matches:
        matches.append([match.start()+1,match.end()-1,'ORDINAL'])
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
    ent_df["in_text"] = ent_df["Name"].apply(lambda x:in_text(x,text))
    entities = ent_df[ent_df["in_text"]][["Name","Entity"]].values
    ent_locs = get_ent_locs(text,entities)
    return ent_locs

def clean_text(text):
    text = re.sub("[:*]"," ",text)
    return text

if __name__ == "__main__":
    ent_df = create_ent_df()
    print(ent_df.head())  
