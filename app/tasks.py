from . import CONSUMER_KEY, CONSUMER_SECRET
from . import celery
import tweepy
from textblob import TextBlob
from . import NUMBER_OF_TWEETS


@celery.task(bind=True, name="tasks.analyzetweets")
def analyzetweets(self, access_token, access_token_secret, mytweets=False, q=None):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    sentimentlist = []
    subjectivitylist = []
    number = NUMBER_OF_TWEETS
    tweets = tweepy.Cursor(api.user_timeline).items() if mytweets else tweepy.Cursor(api.search, q=q).items(number)
    for index, tweet in enumerate(tweets):
        analysis = TextBlob(tweet.text).sentiment
        sentimentlist.append(analysis.polarity)
        subjectivitylist.append(analysis.subjectivity)
        self.update_state(state="RUNNING", meta={"current": index + 1, "total": number})
    sentimentavg = float(sum(sentimentlist) / max(len(sentimentlist), 1))
    subjectivityavg = float(sum(subjectivitylist) / max(len(subjectivitylist), 1))
    return {"current": number, "total": number, "subjectivityavg": subjectivityavg, "sentimentavg": sentimentavg}
