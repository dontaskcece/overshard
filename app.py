from flask import g,Flask,render_template,abort,session,jsonify,request,redirect,flash,url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form 
from wtforms import TextField
from wtforms.validators import DataRequired
from sp import sp
import os
from werkzeug import secure_filename
from flask.ext.cache import Cache
from flask_debugtoolbar import DebugToolbarExtension

app= Flask(__name__)
app.config["DEBUG"]=True
app.config["SECRET_KEY"]="sdfsfsafsafa"
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:////tmp/test.db"
db=SQLAlchemy(app)
cache=Cache(app,config={'CACHE_TYPE': 'simple'})
toolbar = DebugToolbarExtension(app)
app.register_blueprint(sp,url_prefix="/sp")



UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

##########################################

class Content(db.Model):
	id=db.Column(db.Integer,primary_key=True)
	content=db.Column(db.String(1000))
	def __init__(self,content):
		self.content=content
db.create_all()
######################################
class MyForm(Form):
	username=TextField("username",validators=[DataRequired()])

class WriteForm(Form):
	content=TextField("content",validators=[DataRequired])
######################################
@cache.cached(timeout=10,key_prefix="all_posts")
def get_all_posts():
	posts=Content.query.order_by("id desc").all()
	return posts 


@app.route("/")
def index():
	content=get_all_posts()
	return render_template("index.html",content=content)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

##################################
@app.route("/write",methods=['GET', 'POST'])
def write():
	form=WriteForm()
	if request.method=="POST":
		content=form.content.data
		db.session.add(Content(content))
		db.session.commit()
		return redirect(url_for("index"))
	return render_template("write.html",form=form)

@app.route("/del/<int:id>")
def delete(id):
	db.session.delete(Content.query.get(id))
	db.session.commit()
	return redirect(url_for("index"))

#####################################################


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash("file %s uploaded"% filename)
            return redirect(url_for("index"))
    return  render_template("upload.html")
###### login && logout ###########################


@app.route("/login",methods=["GET","POST"])
def login():
	form=MyForm()
	if request.method=="POST":
		username=form.username.data 
		session["username"]=username
		session["logged"]=True
		return redirect(url_for("index"))
	return render_template("login.html",form=form)

@app.route("/logout")
def logout():
	session.pop("username",None)
	session["logged"]=False
	return redirect(url_for("index"))



#####################################################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

import time
@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

if __name__=="__main__":
	app.run()