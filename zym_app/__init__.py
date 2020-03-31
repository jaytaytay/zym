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
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declarative_base

from forms import NewRecipe, NewBoilAddition, StartBoilTimer, RemoveBoilAddition

# import sqlite3
import pandas as pd
import numpy as np
import json
import sys
import os
import config

from datetime import datetime, timedelta

from flask_gtts import gtts

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
gtts(app)

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
	url 			= db.Column(db.String(20), nullable=True)
	user_id			= db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
	boils 			= db.relationship('Boil', backref='bevvy', lazy=True)

	def __repr__(self):
		return f"Bevvy_list('{self.id}', '{self.name}')"

class Boil(db.Model):

	__tablename__ = 'boil'

	id 				= db.Column(db.Integer, primary_key=True)
	description		= db.Column(db.String(100), unique=False, nullable=False)
	time 			= db.Column(db.Integer, unique=False, nullable=False)
	end_datetime 	= db.Column(db.DateTime, unique=False, nullable=True)
	brew_id			= db.Column(db.Integer, db.ForeignKey('bevvy_list.id'), nullable=False)

	def __repr__(self):
		return f"Boil('{self.id}', '{self.description}', '{self.time}', '{self.end_datetime}')"

# -----------------------------------------
#       Functions
# -----------------------------------------
def max_value(inputlist):
	return max([sublist[-1] for sublist in inputlist])

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

# Tab view for brew day, including timers
@app.route("/edit/<int:recipe_id>", methods=['GET', 'POST'])
@app.route("/edit/<int:recipe_id>/<string:scroll>", methods=['GET', 'POST'])
def edit(recipe_id, scroll=None):
	form = NewBoilAddition(brew_id=recipe_id, prefix='a')
	start_timer_form = StartBoilTimer(prefix='b')
	boil_additions = Boil.query.filter(Boil.brew_id == recipe_id).order_by(Boil.time.desc()).all()
	df = pd.DataFrame([(d.time, d.description, d.end_datetime, d.id) for d in boil_additions], 
                  columns=['time', 'description', 'end_datetime', 'id']).sort_values(by=['time'], ascending=False)
	df['addition_group'] = df['time'].rank(ascending=False, method='dense')
	df['addition_group_count'] = list(map(lambda x: df.groupby('addition_group').count().loc[x,'time'], df['addition_group']))
	df['addition_group_ranking'] = df.groupby(['addition_group','addition_group_count']).cumcount()+1
	df['say_it'] = df['time'].astype(str) + " minute addition"
	df.loc[df[df.addition_group_count == 1].index,'say_it'] = df.loc[df[df.addition_group_count == 1].index,'description']
	df.end_datetime = pd.to_datetime(df.end_datetime)
	df['datetime_string'] = df.end_datetime + timedelta(hours=8)
	df['datetime_string'] = df.datetime_string.map(lambda x: x.strftime("%H:%M:%S") if pd.notnull(x) else ' - ')

	recipe = Bevvy_list.query.filter(Bevvy_list.id == recipe_id).all() # could put check to ensure only one item is returned in this list. SHouldn't be any duplicate IDs

	if form.validate_on_submit():
		boil_addition = Boil(description=form.description.data, \
							time=form.time.data, \
							brew_id=recipe_id,\
							end_datetime=None)
		db.session.add(boil_addition)
		db.session.commit()
		flash(f'Boil Addition {form.description.data} successfully added 🔥', 'success_boil')
		return redirect(url_for('edit', recipe_id=recipe_id, scroll="boil_scroll"))

	if start_timer_form.validate_on_submit():
		end_all_timers = datetime.now() + timedelta(minutes=max_value(Boil.query.filter(Boil.brew_id == recipe_id).with_entities(Boil.time).all()))
		for addition in boil_additions:
			addition_end_datetime = end_all_timers - timedelta(minutes=addition.time)
			db.session.query(Boil).filter(Boil.id == addition.id).update({'end_datetime':addition_end_datetime})
		db.session.commit()
		return redirect(url_for('edit', recipe_id=recipe_id, scroll="boil_scroll"))

	remove_boil_addition_form = RemoveBoilAddition(prefix='c')
	remove_boil_addition_form.item_id.choices = [(i.id, str(i.time) + " min: " + i.description) for i in boil_additions]

	if remove_boil_addition_form.validate_on_submit():
		deleted_item = Boil.query.filter(Boil.id == remove_boil_addition_form.item_id.data).first()
		db.session.delete(deleted_item)
		db.session.commit()
		flash(f'Boil Addition {str(deleted_item.time)} min: {deleted_item.description} successfully deleted ❌', 'success_boil')
		return redirect(url_for('edit', recipe_id=recipe_id, scroll="boil_scroll"))


	return render_template("edit.html", recipe=recipe[0], form=form, \
		boil_additions=boil_additions, start_timer_form=start_timer_form, \
		remove_boil_addition_form=remove_boil_addition_form, \
		boil_table=df, scroll=scroll)

# add a new recipe
@app.route("/newrecipe", methods=['GET', 'POST'])
def new_recipe():
	form = NewRecipe()
	recipe_list = Bevvy_list.query.all()
	list_recipes = []

	for recipe in recipe_list:
		row = [recipe.id, recipe.name, recipe.brewday_date.strftime("%-d %b %y")]
		list_recipes.append(row)

	if form.validate_on_submit():
		recipe = Bevvy_list(name=form.name.data, style=form.style.data, abbreviation=form.abbreviation.data, iteration=form.iteration.data, \
			iteration_of=form.iteration_of.data, batch_size=form.batch_size.data, brewday_date=form.brewday_date.data, user_id=form.user_id.data)
		db.session.add(recipe)
		href = "/edit/" + str(db.session.query(Bevvy_list).order_by(Bevvy_list.id.desc()).first().id)
		db.session.query(Bevvy_list).order_by(Bevvy_list.id.desc()).first().url = href
		db.session.commit()
		flash(f'Recipe for {form.name.data} successfully added 🍻', 'success')
		return redirect(url_for('home'))

	return render_template("new_recipe.html", title="New Recipe", form=form, modal=list_recipes)

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
