"""

QUARK BREWING

ZYM_APP

"""


# -----------------------------------------
#     Import stuff
# -----------------------------------------

from flask import Flask, render_template, request, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# import sqlite3
import pandas as pd

import sys
import os
import config

from datetime import datetime

# -----------------------------------------
#       files
# -----------------------------------------
path                = os.getcwd()
sys.path.append(path)

dirpath             = os.path.dirname(path)


# -----------------------------------------
#       initialise app
# -----------------------------------------
app = Flask(__name__)

# -----------------------------------------
#       Database
# -----------------------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):

	__tablename__ = 'users'

	id 			= db.Column(db.Integer, primary_key=True)
	username 	= db.Column(db.String(20), unique=True, nullable=False)
	password 	= db.Column(db.String(60), nullable=False)
	bevvys 		= db.relationship('Bevvy_list', backref='brewer', lazy=True)

	def __repr__(self):
		return f"User('{self.id}', '{self.username}')"

class Bevvy_list(db.Model):

	__tablename__ = 'bevvy_list'

	id 				= db.Column(db.Integer, primary_key=True)
	name 			= db.Column(db.String(100), unique=True, nullable=False) #Optimise length of this string
	style 			= db.Column(db.String(60), nullable=False) #TODO add in validated field, linking to style guide
	abbreviation 	= db.Column(db.String(60), nullable=False)
	iteration 		= db.Column(db.Integer, nullable=False)
	iteration_of 	= db.Column(db.Integer, nullable=False) #id of parent beer, if iteration = 1 then this equals self.id
	batch_size 		= db.Column(db.Integer, nullable=False)
	brewday_date 	= db.Column(db.DateTime, nullable=False)
	user_id			= db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

	def __repr__(self):
		return f"Bevvy_list('{self.id}', '{self.name}')"

# engine = create_engine('sqlite:///site.db', echo=True)
# Session = sessionmaker(bind=engine)
# session = Session()

# def create_connection(db_file):
#     """ create a database connection to the SQLite database
#         specified by the db_file
#     :param db_file: database file
#     :return: Connection object or None
#     """
#     conn = None
#     try:
#         conn = sqlite3.connect(db_file)
#     except Exception as e:
#         print(e)
 
#     return conn

# def select_all_tasks(conn):
#     """
#     Query all rows in the tasks table
#     :param conn: the Connection object
#     :return:
#     """
#     cur = conn.cursor()
#     cur.execute("SELECT * FROM tasks")
 
#     rows = cur.fetchall()
 
#     for row in rows:
#         print(row)

# conn = create_connection(db)

##########################################
#          Build app
##########################################

# home navigation
@app.route("/")
def index():
	return render_template("home.html")

@app.route("/home")
def home():
	return render_template("home.html")

# table of historical recipes. Able to add new recipes, and link to their edit pages.
# could filter by owner (mark/liam)
@app.route("/recipes")
def recipes():

	# collect data
	# bevs_data = db.session.query(Bevvy_list).all()

	bevs_data = Bevvy_list.query.all()

	return render_template("recipes.html", bevs_data=bevs_data)

# # Tab view for brew day, including timers
# @app.route("/edit/<int:recipe_id>")
# def edit():
# 	return render_template("edit_recipe.html")

# # Tab view for various calculators
# @app.route("/calculators")
# def calculators():
# 	return render_template("edit_recipe.html")

# # Tab view for editable lists of ingredients, and their associated properties
# @app.route("/ingredients")
# def ingredients():
# 	return render_template("edit_recipe.html")

if __name__ == "__main__":
	app.run(host='0.0.0.0')