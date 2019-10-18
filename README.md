# Medical Entity Recognition App

### Summary:
Deployed Web App for Identifying Medical Entities and ongoing annottation for Gold Standard Medical Datasets for NLP.

Available: https://medication-ner-app.herokuapp.com/home

### Requirements:

Project is executed entirely in python. Uses Flask to serve static, html, css and data files. Environment can be recreated with.

- <code> pip install -r requirements.txt </code>

### Data:

Data for medical entities has been combined from: 

- Mimic III Presriptions
- MedicineNet.com
- Human annotated entities from Mimic III discharge summaries.

### File Summaries:

#### Base Folder:
- **run.py:** contains executable for flask application
- **Procfile:** Contains specifics for launching python application
- **config.py:** Contains information for flask configurations
- **requirements.txt:** text file indicting dependencies for application environment.
- **uwsgi.ini:** UWSGI configuration file

> #### /app: contains flask python application
> - **__init__.py:** File for initializing variables for flask app
> - **api_views.py:** contains api routes for flask app
> - **app_views.py:** contains app routes for flask app
> - **entities.csv:** contains dataset of known medical entities
> - **get_tags.py:** python code for identifying medical entities in text
> - **hybrid_tagger.py:** python code for creating tags using spacy pre-trained model and heuristic tagging.

>> **/static:**
>>> - **/css:** contains css styles for app
>>> - **/images:** contains images called by app

>> **/templates:** contains html files or app

### Running Application:

App can either by cloned and deployed to heroku. Or run locally.

To run locally:
1. Create a folder to house application
2. cd into created folder and download repo with:

- <code> git clone https://github.com/LiamWoodRoberts/mimic_III_api/tree/dev_branch/app</code>

3. create and activate a virtual enviroment

4. install requirements.txt with:

- <code> pip install -r requirements.txt </code>

5. Update flask executable with:

- <code> export FLASK_APP=run.py </code>

6. Launch Application with:

- <code> flask run </code>

