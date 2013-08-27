import tweepy

# This code requires the Python package tweepy,
# which you can find here:
#
#	https://github.com/tweepy/tweepy
#

# You'll need to get your own consumer key / secret key
# and access token / secret token. See here for how:
#
#	https://dev.twitter.com/docs/auth/tokens-devtwittercom
#

consumer_key = ""
consumer_secret = ""

access_token=""
access_token_secret=""

# Authenticate yourself.

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Create an API instance.

api = tweepy.API(auth)

# friends = api.lookup_friendships(user_ids = [14777850])

# Get access to a user via their username.

user = api.get_user('MetroEscalators')

# A list where we'll store the timeline of a user.

timeline_full = []

# Pull down as many tweets from a user as 
# the Twitter rate limit allows, starting from
# their latest tweet and going backwards in time.

for page in range(0, 150):
	timeline_full.extend(api.user_timeline(id = user.id, page = page, include_rts = True))

import codecs

# We use codecs since some characters may not be ASCII.
# Open a file to write to:

wfile = codecs.open('MetroEscalators.txt', encoding='utf-8', mode='w')

# Write the statuses of the user, from oldest to newest,
# in the format
#
#	time_of_status \t status

for ind in range(1, len(timeline_full) + 1):
	tweet = timeline_full[-ind]

	time = tweet.created_at
	status = tweet.text

	status = status.replace('\n', ' NEWLINE ')

	print status
	print time

	wfile.write(u'{}\t{}\n'.format(time, status))

wfile.close()