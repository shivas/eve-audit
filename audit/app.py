from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.debug = True
app.secret_key = """2,\x88\xcfh\xaei\xfbf\xe4\xa1\xb4\xbf\x07y\xf3\xf0\xe9\xc1Q\xa3q\x94Y,p\xdd.\xeb\xb7\x9cn\xd6F(\x00Q\xc5\x9f\xcf\xf6\x80\x0e\xad\x1a\xb3m^r2\xcbm\xfe_\xa9|\t\xdc\x18\xb1\xe0>\x10\x96"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
db = SQLAlchemy(app)
