from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
#app.secret_key = 'somethingsecret'?

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, body, pub_date=None):
        self.title = title
        self.body = body
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

@app.route('/', methods=['POST', 'GET'])
def index():  
    #completed_blogs = Blog.query.filter_by(body=True).all()
    return render_template('blog.html',title="Blog It!")


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error=''
        body_error = ''
        
        if len(title) == 0:
            title_error = "Please fill in the title"
        if len(body) == 0:
            body_error = "Please fill in the body"  
        if title_error == '' and body_error == '':
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()
            post_id = new_post.id
            return redirect('/blog?id=' + str(post_id))
        else:
            return render_template('newpost.html', title_error=title_error, body_error=body_error)
    
    return render_template('newpost.html')


@app.route('/blog', methods=['POST','GET'])
def blog():
    
    posts = Blog.query.all()
    id = request.args.get('id')
    id_on_page = Blog.query.filter_by(id=id).first()
    if not id_on_page:
        return render_template ("blog.html",new_post=posts)
    else:
        return render_template("post.html", post=id_on_page)


if __name__ == '__main__':
    app.run()