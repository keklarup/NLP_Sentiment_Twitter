#importing the modules needed to gather tweets
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
import pandas as pd

#initializing and opening Twitter api:
consumer_key = 'xxxxxxxxxxxxxxxxxxxxxxx'
consumer_secret = 'xxxxxxxxxxxxxxxxxxxxxxx'
access_token = 'xxxxxxxxxxxxxxxxxxxxxxx'
access_secret = 'xxxxxxxxxxxxxxxxxxxxxxx'
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

#def to mine a given Twitter handle for 200 most recent tweets (minus retweets) and repeat for the next 200 till limit on repeats hit.
#ex handle:	#handle='@realDonaldTrump' or handle='@BillNye'
def mine(handle, limit, save):
	#collecting the first batch of tweets
	tweets=[];
	tweets_set=api.user_timeline(screen_name = handle, count = 200, include_rts = False)
	tweets.extend(tweets_set)

	#extending the collection of tweets by rerunning collection x times:
	oldestID=tweets[-1].id-1
	x=0
	while len(tweets_set) > 0:
		#print ("getting tweets before %s" % (oldestID))
		try:
			tweets_set = api.user_timeline(screen_name = handle,count=200,max_id=oldestID)
		except:
			break
		tweets.extend(tweets_set)
		oldestID = tweets[-1].id - 1
		#print ("...%s tweets downloaded so far" % (len(tweets)))
		x=x+1
		if x>limit:
			break
			
	#cleaning up the collection and putting into dataframe:
	def clean_tweet(tweet):
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

	User_tweets=pd.DataFrame()
	User_tweets['tweets']=''
	User_tweets['timestamp']=''
	User_tweets['handle']=''
	y=0
	for tweet in tweets:
		User_tweets.loc[y,'tweets']=clean_tweet(tweet.text.lower())
		User_tweets.loc[y,'timestamp']=str(tweet.created_at)
		User_tweets.loc[y,'retweet_count']=tweet.retweet_count
		User_tweets.loc[y,'handle']=handle
		y=y+1

	#additional cleaning:
	punctuation=['.','?','!','/',';',':','(',')'];
	for elm in punctuation:
		User_tweets['tweets']=User_tweets['tweets'].str.replace('%s'%elm,' %s '%elm)
		
	#getting TextBlob's sentiment rating (Textblob gives a very basic sentiment analysis score. I've measured accuracy and my NN seems to do better):
	def get_tweet_sentiment(tweet):
		analysis = TextBlob(tweet)
		# set sentiment
		if analysis.sentiment.polarity > 0:
			return 'positive'
		#elif analysis.sentiment.polarity == 0:
		#    return 'neutral'
		else:
			return 'negative'
	User_tweets['TextBlob']=User_tweets['tweets'].apply(get_tweet_sentiment)

	#checking if some tweets from this handle already saved:
	try:
		User_tweets_previous=pd.read_csv('User_tweets_%s.csv'%(handle))
		User_tweets=pd.concat([User_tweets_previous,User_tweets.loc[~(
                    User_tweets['timestamp'].isin(User_tweets_previous['timestamp'])),:]])
		User_tweets.reset_index(inplace=True)
		del User_tweets['index']
	except:
		pass
	
	#saving to csv:
	if save==True:
		User_tweets.to_csv('User_tweets_%s.csv'%(handle),index=False)
	return User_tweets
	