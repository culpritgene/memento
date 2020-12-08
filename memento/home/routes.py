from flask import Blueprint
from flask import render_template

home_bp = Blueprint('home_bp', __name__, static_folder='static', template_folder='templates')

@home_bp.route("/")
@home_bp.route("/home")
def home():
    return render_template('home.html')


@home_bp.route("/about")
def about():
    return render_template('about.html')
