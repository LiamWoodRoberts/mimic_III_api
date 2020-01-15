import re
import pickle
from nltk import pos_tag

# Parse Summary --> Sentances

def clean_text(text):
    bad_chars = [":","*"]
    space_chars = ["[","]","(",")","\n"]
    for c in bad_chars:
        text = text.replace(c,"")
    for c in space_chars:
        text = text.replace(c," ")
    return text

def to_sentances(discharge_summary):
    discharge_summary = clean_text(discharge_summary)
    sentances = [i.lstrip() for i in re.split("\. ",discharge_summary) if len(i)>0]
    return sentances

def remove_spaces(seq):
    return [word.replace(" ","") for word in seq if len(word.replace(" ",""))>0]

def create_seqs(sentances):
    seqs = [re.split("([ ,;])",i) for i in sentances]
    return [remove_spaces(seq) for seq in seqs]

def add_pos_sentances(seqs):
    new_seqs = []
    for sentance in seqs:
        pos = pos_tag(sentance)        
        new_seqs.append(pos)
    return new_seqs

def word2features(sent, i):
    '''
    
    From:
    https://www.depends-on-the-definition.com/named-entity-recognition-conditional-random-fields-python/
    
    '''
    word = sent[i][0]
    postag = sent[i][1]

    features = {
        'bias': 1.0,
        'word.lower()': word.lower(),
        'word[-3:]': word[-3:],
        'word[-2:]': word[-2:],
        'word.isupper()': word.isupper(),
        'word.istitle()': word.istitle(),
        'word.isdigit()': word.isdigit(),
        'postag': postag,
        'postag[:2]': postag[:2],
    }
    if i > 0:
        word1 = sent[i-1][0]
        postag1 = sent[i-1][1]
        features.update({
            '-1:word.lower()': word1.lower(),
            '-1:word.istitle()': word1.istitle(),
            '-1:word.isupper()': word1.isupper(),
            '-1:postag': postag1,
            '-1:postag[:2]': postag1[:2],
        })
    else:
        features['BOS'] = True

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        postag1 = sent[i+1][1]
        features.update({
            '+1:word.lower()': word1.lower(),
            '+1:word.istitle()': word1.istitle(),
            '+1:word.isupper()': word1.isupper(),
            '+1:postag': postag1,
            '+1:postag[:2]': postag1[:2],
        })
    else:
        features['EOS'] = True

    return features

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def remove_null_words(seq):
    return [word for word in seq if len(word)>0]

def load_crf(filepath):
    with open(filepath,"rb") as f:
        crf = pickle.load(f)
    return crf

def create_annotations(crf,seqs):
    x = [sent2features(s) for s in seqs]
    ner_tags = crf.predict(x)
    return ner_tags

def combine_B_I_tags(seq):
    combi_seq = []
    phrase = ""
    for word,tag in seq:
        if tag == "O":
            if len(phrase)>0:
                combi_seq.append([phrase,phrase_tag])
                phrase = ""
            combi_seq.append([word,tag])
        else:
            if tag[0] == "B":
                if len(phrase)>0:
                    combi_seq.append([phrase,phrase_tag])
                    phrase = ""
                phrase = word
                phrase_tag = tag[2:]
            if tag[0] == "I":
                phrase += " "+word
    if len(phrase)>0:
        combi_seq.append([phrase,phrase_tag])
    return combi_seq

def create_dataset(crf,seqs):
    ner_tags = create_annotations(crf,seqs)
    data = []
    for i in range(len(seqs)):
        data_entry = [[seqs[i][j][0],ner_tags[i][j]] for j in range(len(seqs[i]))]
        data.append(data_entry)
    data = [combine_B_I_tags(seq) for seq in data]
    summary = []
    for s in data:
        summary += s
    return summary

def prep_unannotated_data(raw_text):
    sentances = to_sentances(raw_text)
    seqs = create_seqs(sentances)    # Remove null words
    seqs = [remove_null_words(seq) for seq in seqs]
    seqs = add_pos_sentances(seqs)
    return seqs

def predict_raw(raw_text,crf):
    seqs = prep_unannotated_data(raw_text)
    prediction = create_dataset(crf,seqs)
    return prediction

def get_tags(summary,tags):
    ents = []
    for a,b in summary:
        if b in tags:
            ents.append(a)
    return ents

def show_info(summary,text):
    
    print("\nMedical Info:\n","-"*40)
    
    print("\nAge:")
    age = get_tags(summary,["Age"])
    print(tags)

    print("\nGender:")
    tags = get_tags(summary,["Gender"])
    print(tags)

    print("\nSymptoms:")
    tags = get_tags(summary,["DOS"])
    print(tags)

    print("\nConditions:")
    tags = get_tags(summary,["Condition"])
    print(tags)

    print("\nMajor Tests or Procedures:")
    tags = get_tags(summary,["Test / Screening","Procedure"])
    print(tags)

    print("\n Drugs:")
    tags = get_tags(summary,["Drug","Dose","Route"])
    print(tags)
    
    print("\nRaw Text:")
    print(text)
    return 

def medical_suite(text,crf):
    summary = predict_raw(text,crf)
    age = get_tags(summary,["Age"])
    gender = get_tags(summary,["Gender"])
    symptoms = get_tags(summary,["DOS"])
    conditions = get_tags(summary,["Condition"])
    procedures = get_tags(summary,["Test / Screening","Procedure"])
    drugs = get_tags(summary,["Drug","Dose","Route"])

    return age,gender,symptoms,conditions,procedures,drugs

if __name__ == "__main__":
    crf_path = "crf_model"
    crf = load_crf(crf_path)
    sample_text = '''This is an 81-year-old female with a history of emphysema (not on home O2), who presents with three days of shortness of breath thought by her primary care doctor to be a COPD flare. Two days prior to admission, she was started on a prednisone taper and one day prior to admission she required oxygen at home in order to maintain oxygen saturation greater than 90%. She has also been on levofloxacin and nebulizers, and was not getting better, and presented to the [**Hospital1 18**] Emergency Room.'''
    summary1 = medical_suite(sample_text,crf)
