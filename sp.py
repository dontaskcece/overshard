from flask import Blueprint ,render_template

sp=Blueprint("sp",__name__)

@sp.route("/")
def index():
	return render_template("index.html")