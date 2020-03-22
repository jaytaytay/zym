from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length

class NewRecipe(FlaskForm):
	name 			= StringField('Name', validators=[DataRequired(), Length(min=3, max=100)])
	style 			= StringField('Style', validators=[DataRequired(), Length(min=3, max=60)])
	abbreviation 	= StringField('Abbreviation', validators=[DataRequired(), Length(min=3, max=60)])
	iteration 		= IntegerField('Iteration', validators=[DataRequired()], render_kw={"placeholder": "Integer pls"})
	iteration_of 	= IntegerField('Iteration of', render_kw={"placeholder": "ID number of original parent, if applicable"})
	batch_size 		= IntegerField('Batch Size', validators=[DataRequired()], render_kw={"placeholder": "in litres"})
	brewday_date 	= DateField('Brewday Date', validators=[DataRequired()], render_kw={"placeholder": "YYYY-MM-DD"})
	user_id			= RadioField('Brewer', choices=[('mark', 'Mark'), ('liam', 'Liam')])

	submit 			= SubmitField('Submit')