from flask import Flask, request, render_template, redirect, url_for
from flask_oauthlib.client import OAuth

app = Flask(__name__)

# Configure OAuth settings for Google
app.config["GOOGLE_ID"] = "1"
app.config["GOOGLE_SECRET"] = "1"
oauth = OAuth(app)

# Create an OAuth provider for Google
google = oauth.remote_app(
    "google",
    consumer_key=app.config["GOOGLE_ID"],
    consumer_secret=app.config["GOOGLE_SECRET"],
    request_token_params={"scope": "email"},
    base_url="https://www.googleapis.com/oauth2/v1/",
    request_token_url=None,
    access_token_method="POST",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
)


# Route to initiate the Google OAuth login process
@app.route("/login")
def login():
    return google.authorize(callback=url_for("authorized", _external=True))


# Callback route after successful Google OAuth login
@app.route("/login/authorized")
def authorized():
    response = google.authorized_response()
    if response is None or response.get("access_token") is None:
        return "Access denied: reason={} error={}".format(
            request.args["error_reason"], request.args["error_description"]
        )

    # Store user information in session
    session["google_token"] = (response["access_token"], "")
    user_info = google.get("userinfo")
    session["user_info"] = user_info.data
    return redirect(url_for("upload_page"))


# ... (Keep the previous code for the image upload, display, and API routes)

if __name__ == "__main__":
    app.secret_key = "your_secret_key"  # Change this to a strong secret key
    app.run(debug=True)
