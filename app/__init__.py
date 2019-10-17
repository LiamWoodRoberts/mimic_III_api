# Other Modules
from flask import Flask,Blueprint
from flask_restplus import Api
from app.get_tags import load_ent_df
import en_core_web_sm

app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

app.config.from_object('config.Config')

blueprint = Blueprint('api',__name__,url_prefix='/api')
api_name = 'Customer Loyalty Prediction Model'
api = Api(blueprint,default=api_name,doc='/documentation')
app.register_blueprint(blueprint)

ent_df = load_ent_df()
nlp = en_core_web_sm.load()

from app import api_views
from app import app_views