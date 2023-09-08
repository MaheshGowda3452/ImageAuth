from flask import Flask, redirect, url_for, session, request, render_template
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
import base64
from PIL import Image
import io
# from starlette.requests import Request
# decorator for routes that should be accessible only by logged in users
from auth_decorator import login_required
# from authlib.integrations.starlette_client import OAuth
# dotenv setup
# from dotenv import load_dotenv
# load_dotenv()


# App config
app = Flask(__name__)
# Session config
# app.secret_key = os.getenv("APP_SECRET_KEY")

app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

# oAuth Setup
oauth = OAuth(app)
google = oauth.register(
    name='google',
    # client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_id='802199944149-ulq1986gaoaslqtjhpvl7m7n4jd6m7fo.apps.googleusercontent.com',
    # client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    client_secret='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',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url= 'https://accounts.google.com/.well-known/openid-configuration'
)


@app.route('/')
# @login_required
def home():
    app.secret_key = "image secret key"
    # print(os.getenv("APP_SECRET_KEY"))
    try:
        print(session['profile'])
    except KeyError:
        return redirect('/login')
    else:
        return redirect('/home')
    


@app.route('/login')
def login():
    app.secret_key = "image secret key"
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    
    token = google.authorize_access_token() 
    # print(token)
    resp = google.get('userinfo')  # userinfo contains stuff u specificed in the scrope
    user_info = resp.json()
    print(user_info)
    # user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # print(user)
    # # Here you use the profile/user data that you got and query your database find/register the user
    # # and set ur own data in the session not the profile from google
    session['email'] = user_info['email']
    session['profile'] = user_info
    # session.permanent = True  # make the session permanant so it keeps existing after broweser gets closed
    return redirect('/home')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


@app.route('/home')
@login_required
def uploadImage():
    return render_template("index.html", session=dict(session)['profile']['name'])
    # return dict(session)['profile']['email']

@app.route('/image-preview', methods=["POST"])
@login_required
def imagePreview():
    print(request.files['image'])

    file = request.files['image']
    img = Image.open(file.stream)
    # img = img.convert('L')   # ie. convert to grayscale
    #data = file.stream.read()
    #data = base64.b64encode(data).decode()
    buffer = io.BytesIO()
    img.save(buffer, 'png')
    buffer.seek(0)
    data = buffer.read()
    data = base64.b64encode(data).decode()
    print(request.files['image'].filename)
    return render_template("/image-preview/preview.html",img=[data,request.files['image'].filename])

if __name__ == "__main__":
    app.run(debug=True)
