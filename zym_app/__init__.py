"""

QUARK BREWING

ZYM_APP

"""

# -----------------------------------------
#     Import stuff
# -----------------------------------------

from flask import Flask, render_template, request, g, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from forms import NewRecipe

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
app.config['SECRET_KEY'] = '51bc14061a7a9c248ac219d84493cebc'
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
	bevs_data = Bevvy_list.query.all()
	return render_template("recipes.html", bevs_data=bevs_data)

# @app.route("/recipes")
# def recipes():
# 	users = User.query.all()
# 	return render_template("recipes.html", users=users)

# Tab view for brew day, including timers
@app.route("/edit/<int:recipe_id>")
def edit():
	return render_template("edit_recipe.html")

# add a new recipe
@app.route("/newrecipe", methods=['GET', 'POST'])
def new_recipe():
	form = NewRecipe()
	if form.validate_on_submit():
		recipe = Bevvy_list(name=form.name.data, style=form.style.data, abbreviation=form.abbreviation.data, iteration=form.iteration.data, \
			iteration_of=form.iteration_of.data, batch_size=form.batch_size.data, brewday_date=form.brewday_date.data, user_id=form.user_id.data)
		db.session.add(recipe)
		db.session.commit()
		flash(f'Recipe for {form.name.data} successfully added 🍻', 'success')
		return redirect(url_for('home'))
	return render_template("new_recipe.html", title="New Recipe", form=form)

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