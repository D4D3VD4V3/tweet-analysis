from collections import namedtuple
import os
import tweepy
from flask import Flask, render_template, session, redirect, request, url_for, flash
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Link
from flask_wtf import FlaskForm
from textblob import TextBlob
from wtforms.fields import StringField, SubmitField
from wtforms.validators import DataRequired, Length

secret_key = os.getenv("SECRET_KEY")
CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")

app = Flask(__name__)
app.secret_key = secret_key
Bootstrap(app)
topbar = Navbar(View("Home", "home"),
                Link("Source Code", r"http://www.github.com/d4d3vd4v3/tweet-analysis"))
nav = Nav()
nav.register_element("topbar", topbar)
nav.init_app(app)


class HashtagForm(FlaskForm):
    hashtag = StringField("Enter a keyword", [DataRequired(), Length(min=1, max=140)])
    submit = SubmitField("Go!")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/twittersignin")
def twittersignin():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    try:
        redirect_url = auth.get_authorization_url()
        session["request_token"] = auth.request_token

    except tweepy.TweepError:
        flash("Failed to get request token", "danger")
        return redirect(url_for("home"))
    return redirect(redirect_url)


def analyzetweets(mytweets, q=None):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(session["access_token"], session["access_token_secret"])
    api = tweepy.API(auth)
    sentimentlist = []
    subjectivitylist = []
    analysistuple = namedtuple("analysis", ["number", "sentimentavg", "subjectivityavg", "tweets"])
    tweets = tweepy.Cursor(api.user_timeline).items() if mytweets else tweepy.Cursor(api.search,
                                                                                     q=q).items(100)
    for tweet in tweets:
        analysis = TextBlob(tweet.text).sentiment
        sentimentlist.append(analysis.polarity)
        subjectivitylist.append(analysis.subjectivity)
    sentimentavg = float(sum(sentimentlist) / max(len(sentimentlist), 1))
    subjectivityavg = float(sum(subjectivitylist) / max(len(subjectivitylist), 1))
    analysedstuff = analysistuple(len(sentimentlist), sentimentavg, subjectivityavg, tweets)
    return analysedstuff


@app.route("/analyzemytweets")
def analyzemytweets():
    analysedstuff = analyzetweets(True)
    return render_template("analyzemytweets.html", number=analysedstuff.number,
                           sentimentavg=analysedstuff.sentimentavg,
                           subjectivityavg=analysedstuff.subjectivityavg,
                           tweets=analysedstuff.tweets)


@app.route("/analyzehashtag", methods=["POST"])
def analyzehashtag():
    form = HashtagForm()
    if form.validate_on_submit():
        analysedstuff = analyzetweets(False, request.form["hashtag"])
        return render_template("analyzemytweets.html", number=analysedstuff.number,
                               sentimentavg=analysedstuff.sentimentavg,
                               subjectivityavg=analysedstuff.subjectivityavg,
                               tweets=analysedstuff.tweets)
    return redirect(url_for("home"))


@app.route("/twittercallback", methods=["GET", "POST"])
def twittercallback():
    verification = request.args["oauth_verifier"]
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    try:
        auth.request_token = session["request_token"]
    except KeyError:
        flash("Please login again", "danger")
        return redirect(url_for("home"))

    try:
        auth.get_access_token(verification)
    except tweepy.TweepError:
        flash("Failed to get access token", "danger")
        return redirect(url_for("home"))

    session["access_token"] = auth.access_token
    session["access_token_secret"] = auth.access_token_secret

    return render_template("twittercallback.html", form=HashtagForm())


@app.errorhandler(404)
def fournotfour(e):
    return render_template("404page.html"), 404


if __name__ == "__main__":
    app.run()
