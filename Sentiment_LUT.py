#A module for determining how often a word is found in postive vs negative tweets.

import re
import pandas as pd
import numpy as np


def LUT(n):
	Training_set=pd.read_csv('NLP_files/SentimentAnalysisDataset.csv',usecols=['Sentiment','SentimentText']) #need to import tweets with labeled sentiment
	#n=50000 #only taking a sample of the totatl 1.5M training tweets to reduce time of work.
	Training_set_neg_sample=Training_set.loc[Training_set.loc[:,'Sentiment']==0,:].sample(n);
	Training_set_pos_sample=Training_set.loc[Training_set.loc[:,'Sentiment']==1,:].sample(n);
	Training_set_sample=pd.concat([Training_set_neg_sample,Training_set_pos_sample]) #even split of pos and neg tweets in sample
	Training_set_sample.reset_index(inplace=True)
	del Training_set_sample['index']
	Training_set=Training_set_sample.copy()
	Training_set.rename(columns={"SentimentText": "tweets"},inplace=True) #rename to have consistnacy over all notebooks.
	#basic pre-processing
	Training_set['tweets']=Training_set['tweets'].str.lower()
	punctuation=['.','?','!','/',';',':','(',')'];
	for elm in punctuation:
		Training_set.loc[:,'tweets']=Training_set.loc[:,'tweets'].str.replace('%s'%elm,' %s '%elm)
	def clean_tweet(tweet):
		return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
	Training_set.loc[:,'tweets']=Training_set.loc[:,'tweets'].apply(clean_tweet)
	#splitting by individual words and counting up the number of times words show up in neg and pos tweets
	neg_counts=pd.value_counts(np.concatenate(
			Training_set.loc[Training_set.loc[:,'Sentiment']==0,'tweets'].str.split(' ').values));
	pos_counts=pd.value_counts(np.concatenate(
			Training_set.loc[Training_set.loc[:,'Sentiment']==1,'tweets'].str.split(' ').values));
	#bad form to have def in def, but it was the fastest method I came up with
	#calculating ratio for a given word of number of times in postive tweets to negative tweets. A score of 0==equal times in both. A score of 1==either only in pos or neg tweets.
	def word_based(word):
		try:
			a=(pos_counts[word]-neg_counts[word])/(pos_counts[word]+neg_counts[word]);
		except:
			try:
				a=pos_counts[word]/pos_counts[word]
			except:
				try:
					a=-(neg_counts[word]/neg_counts[word])
				except:
					a=0                                             
		return a

	#return a dataframe with each word as the index and the ratio of pos/neg as a sentiment value from 0 to 1.
	LUT_sentiment_words=pd.DataFrame()
	LUT_sentiment_words['words']=pd.Series(np.concatenate(Training_set.loc[0:,'tweets'].str.split(' '))).value_counts().index
	LUT_sentiment_words['Score']=LUT_sentiment_words.loc[:,'words'].apply(word_based)
	return LUT_sentiment_words