from flask import Flask, render_template,request, session, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug import secure_filename
import json
import os
import math
from flask_mail import Mail
from datetime import datetime


with open('config.json', 'r') as c:
    params=json.load(c)["params"]


app = Flask(__name__)
app.secret_key = 'SECRET KEY'
app.config['UPLOAD_FOLDER'] = params['upload_location']

app.config.update(
    MAIL_SERVER ='smtp.gmail.com',
    MAIL_PORT ='465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['gmail_password']    
)

mail = Mail(app)
app.config['SQLALCHEMY_DATABASE_URI'] = params['local_server']
db = SQLAlchemy(app)


class Contacts(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), nullable=False)
    email= db.Column(db.String(25), nullable=False)
    phone_number= db.Column(db.String(5), nullable=False)
    message= db.Column(db.String(150), nullable=False)

class Posts(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(25), nullable=False)
    slug= db.Column(db.String(25), nullable=False)
    content= db.Column(db.String(100), nullable=False)
    date= db.Column(db.String(12), nullable=False)
    img_file= db.Column(db.String(12), nullable=False)
    tagline= db.Column(db.String(120), nullable=False)




@app.route("/")
def home():
    posts=Posts.query.filter_by().all()
    #Pagination
    last = math.ceil(len(posts)/ int(params['no_of_posts']))
    page=request.args.get('page')
    if (not str(page).isnumeric()):
        page=1
    page=int(page)
    
    posts = posts[(page-1)* int(params['no_of_posts']) : (page-1)* int(params['no_of_posts']) + int(params['no_of_posts'])]
    
    if(page==1 and page==last):
        prev = "#"
        next ="#"
    elif(page==1 and page!=last):
        prev= "#"
        next= "/?page=" + str(page+1)
    elif(page==last and page!=1):
        prev= "/?page" + str(page-1)
        next= "#"
    else:
        prev= "/?page" + str(page-1)
        next= "/?page=" + str(page+1)


    return render_template('index.html', params=params, posts=posts, prev=prev, next=next ) 





@app.route("/about")
def about():
    return render_template('about.html', params=params)



# EDIT
@app.route("/edit/<string:id>", methods= ['GET', 'POST'])
def edit(id):
    if ('user' in session and session['user'] == params['admin_email']):
        if (request.method == 'POST'):
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date=datetime.now()

            if id =="0":
                post=Posts(title=title, tagline=tagline, slug=slug, content=content, img_file=img_file, date=date)
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(id=id).first()
                post.title=title
                post.tagline=tagline
                post.slug=slug
                post.content=content
                post.img_file=img_file
                post.date=date
                db.session.add(post)
                db.session.commit()
                return redirect('/edit/' + id)
    post = Posts.query.filter_by(id=id).first()
    return render_template('edit.html', params=params, post=post, id=id)


#DELETE
@app.route("/delete/<string:id>", methods= ['GET', 'POST'])
def delete(id):
    if ('user' in session and session['user'] == params['admin_email']):
        post= Posts.query.filter_by(id=id).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')




@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_email']):
        posts=Posts.query.all()
        return render_template("dashboard.html", params=params, posts=posts)
    
    if request.method =='POST':
        user_email=request.form.get("email")
        user_password=request.form.get("password")
        if (user_email == params['admin_email'] and user_password == params['admin_password']):
            #set session variable
            session['user']= user_email
            posts=Posts.query.all()
            return render_template('dashboard.html', params=params, posts=posts)

    
    return render_template('login.html', params=params)





@app.route("/contact", methods=['GET', 'POST'])
def contact():
    
    if(request.method=='POST'):
        '''Add entry to database '''
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')

        entry=Contacts(name=name, email=email, phone_number=phone, message=message)
        db.session.add(entry)
        db.session.commit()
        # mail.send_message('New message from Flask app by ' + name, 
        #                     sender= email, 
        #                     recipients = [params['gmail_recipients']],
        #                     body = message + "\n " + phone,
        #                     )
        flash("Thanks for submitting your detail. We will get back to you soon", "success")
    return render_template('contact.html', params=params)



@app.route("/uploader", methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_email']):
        if request.method== "POST":
            f=request.files['myfile']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded Successfully"


@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', params=params, post=post)



app.run(debug=True)






















