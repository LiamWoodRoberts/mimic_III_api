from app import app,api,ent_df
from app.get_tags import get_entity_tags,get_drugs_and_conditions,clean_text

from flask import render_template,request,jsonify,url_for,redirect

@app.route("/contact")
def test():
    return render_template("/contact.html")

@app.route("/",methods=["GET","POST"])
@app.route("/home",methods=["GET","POST"])
def home():
    d_and_c = {"DRUGS":['None'],"CONDITIONS":["None"]}
    if request.method == "POST":
        text = request.form["text"]
        text = clean_text(text)
        ent_locs = get_entity_tags(text,ent_df)
        d_and_c = get_drugs_and_conditions(ent_locs)
        return render_template("/home.html",ents = d_and_c)
    else:
        return render_template("/home.html",ents=d_and_c)
