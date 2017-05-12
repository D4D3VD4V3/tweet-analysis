import tweepy
from app import CONSUMER_KEY, CONSUMER_SECRET
from flask import session, flash, redirect, render_template, url_for, request, jsonify
from app.forms import HashtagForm
from app.tasks import analyzetweets
from . import bp
from .. import NUMBER_OF_TWEETS


@bp.route("/")
def home():
    return render_template("index.html", tweets=NUMBER_OF_TWEETS)


@bp.route("/twittersignin")
def twittersignin():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    try:
        redirect_url = auth.get_authorization_url()
        session["request_token"] = auth.request_token

    except tweepy.TweepError:
        flash("Failed to get request token", "danger")
        return redirect(url_for("bp.home"))
    return redirect(redirect_url)


@bp.route("/loading/<task_id>")
def loading(task_id):
    return render_template("showprogress.html", task_id=task_id)


@bp.route("/status/<task_id>")
def taskstatus(task_id):
    task = analyzetweets.AsyncResult(str(task_id))
    if task.state == "PENDING":
        response = {
            "state": task.state,
            "current": 0,
            "total": NUMBER_OF_TWEETS
        }
    elif task.state != "FAILURE":
        response = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": NUMBER_OF_TWEETS
        }
        if "subjectivityavg" in task.info:
            response["subjectivityavg"] = task.info["subjectivityavg"]
            if "sentimentavg" in task.info:
                response["sentimentavg"] = task.info["sentimentavg"]
    else:
        response = {
            "state": task.state,
            "current": 1,
            "total": NUMBER_OF_TWEETS
        }
    return jsonify(response)


@bp.route("/analyzemytweets")
def analyzemytweets():
    task = analyzetweets.apply_async(kwargs={"access_token": session["access_token"],
                                             "access_token_secret": session["access_token_secret"],
                                             "mytweets": True})
    return redirect(url_for("bp.loading", task_id=task.id))


@bp.route("/analyzehashtag", methods=["POST"])
def analyzehashtag():
    form = HashtagForm()
    if form.validate_on_submit():
        task = analyzetweets.apply_async(kwargs={"access_token": session["access_token"],
                                                 "access_token_secret": session["access_token_secret"],
                                                 "mytweets": False,
                                                 "q": request.form["hashtag"]})
        return redirect(url_for("bp.loading", task_id=task.id))
    return redirect(url_for("bp.home"))


@bp.route("/twittercallback", methods=["GET", "POST"])
def twittercallback():
    verification = request.args["oauth_verifier"]
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    try:
        auth.request_token = session["request_token"]
    except KeyError:
        flash("Please login again", "danger")
        return redirect(url_for("bp.home"))

    try:
        auth.get_access_token(verification)
    except tweepy.TweepError:
        flash("Failed to get access token", "danger")
        return redirect(url_for("bp.home"))

    session["access_token"] = auth.access_token
    session["access_token_secret"] = auth.access_token_secret

    return render_template("twittercallback.html", form=HashtagForm())


@bp.route("/showgauges")
def showgauges():
    return render_template("showgauges.html",
                           subjectivityavg=request.args["subjectivityavg"],
                           sentimentavg=request.args["sentimentavg"])
