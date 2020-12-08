from flask import Blueprint
from flask import render_template
from flask_login import login_required

from .matrix import url_base

matrix_bp = Blueprint('matrix_bp', __name__, static_folder='static', template_folder='templates')

@matrix_bp.route("/matrix", methods=['GET', 'POST'])
@login_required
def matrix():
    return render_template('/matrix.html', dash_url=url_base)