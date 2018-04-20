from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(255))
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date
       

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/', methods=['POST', 'GET'])
def index():  
    authors = User.query.all()   
    return render_template("index.html", authors=authors)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    #new parameter to consider when creating a blog entry?
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error=''
        body_error = ''
        
        owner = User.query.filter_by(username=session['username']).first()
        
        if len(title) == 0:
            title_error = "Please fill in the title"
        if len(body) == 0:
            body_error = "Please fill in the body"  
        if title_error == '' and body_error == '':
            new_post = Blog(title, body, owner)
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
    users = User.query.all()
    id = request.args.get('id')
    userID = request.args.get('user')
    if id:
        id_on_page = Blog.query.filter_by(id=id).first()
        return render_template("post.html", post=id_on_page)

    elif userID:
        
        single_page = User.query.filter_by(username=userID).first()
        author_posts = Blog.query.filter_by(owner_id=single_page.id).all()
        return render_template("singleUser.html", posts=author_posts)

    else:
        
        return render_template("blog.html", new_post=posts)


@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        username_error = ''
        password_error = ''

        user = User.query.filter_by(username=username).first()
        if not user:
            username_error = "The user does not exist"
        if user and user.password != password:
            password_error = "Password is incorrect"
        
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            print(session)
            return redirect('/newpost')
        else:
            return render_template("login.html", username=username, username_error=username_error, password_error=password_error)
    return render_template("login.html")

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify= request.form['verify']
        existinguser_error = "User already exists"

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            username_error = ''
            password_error = ''
            verify_error = ''


            if len(username) == 0 or len(username) < 3 or len(username) > 20 or ' ' in username:
                username_error = "That's not a valid username" 

            if len(password) == 0 or len(password) < 3 or len(password) > 20 or ' ' in password:
                password_error = "That's not a valid password"

            if len(verify)== 0 or verify != password: 
                verify_error = "Passwords do not match"

            if username_error == '' and password_error == '' and verify_error == '': 
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username #remember that user has logged in
                return redirect('/newpost')
                
    
            else:
                return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error, username=username)

        else:
            return render_template("signup.html",existinguser_error=existinguser_error)
    return render_template("signup.html")

@app.route('/singleUser')
def singleUser():
    authors = User.query.all()
    return render_template('singleUser.html')

@app.route('/logout', methods = ['GET'])
def logout():
    del session['username']
    flash ("Logged out")
    return redirect('/blog')

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index'] 
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')



if __name__ == '__main__':
    app.run()