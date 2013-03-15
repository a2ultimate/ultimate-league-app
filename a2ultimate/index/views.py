from django import forms
from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from syncr.app.tweet import TwitterSyncr
from syncr.twitter.models import Tweet
from twitter import TwitterError

from syncr.app.flickr import FlickrSyncr
from syncr.flickr.models import Photo
from flickrapi import FlickrError
import datetime
import pytz
import traceback

from a2ultimate.index.models import *
from pybb.models import Forum, Topic

from paypal.standard.forms import PayPalPaymentsForm

import feedparser

def index(request):
	announcements = Topic.objects.filter(forum__name__exact='Announcements')[:5]

	updates = list()

	photoset = list()
	counter = 0
	photos = Photo.objects.order_by('-upload_date', 'owner')[:30]
	for photo in photos:
		photo.url = photo.get_thumbnail_url

		photoset.append(photo)

		try:
			nextOwner = photos[counter+1].owner
		except IndexError:
			nextOwner = False

		if photo.owner != nextOwner:
			updates.append({'type':'photo','photoset': photoset, 'owner': photo.owner,'owner_nsid': photo.owner_nsid, 'count':len(photoset), 'datetime': photo.upload_date})
			photoset = list()
		counter += 1

	tweets = Tweet.objects.order_by('-pub_time')[:10]
	for tweet in tweets:
		updates.append({'type': 'tweet', 'tweet': tweet, 'datetime': tweet.pub_time})

	updates.sort(key=lambda x:x['datetime'], reverse=True)

	return render_to_response('index/index.html',
		{'announcements': announcements, 'updates': updates, 'tweets': tweets, 'photos': photos},
		context_instance=RequestContext(request))

def update_feed(request):
	# try:
	# 	twitterSyncr = TwitterSyncr('aaultimate')
	# 	twitterSearchFeed = feedparser.parse('http://search.twitter.com/search.atom?lang=en&q=ultimate+frisbee')

	# 	for tweet in twitterSearchFeed.entries:
	# 		twitterID = tweet.id[tweet.id.rindex(':')+1:]
	# 		try:
	# 			twitterSyncr.syncTweet(twitterID)
	# 		except TwitterError:
	# 			print 'twitter parse error'
	# 		except:
	# 			print 'twitter unknown error'
	# except:
	# 	print 'twitter unknown feed error'


	flickrSyncr = FlickrSyncr('1d6f830e7130f7196c4104d70589c031', '73ad75aac80ea1a8')
	flickrSearchFeed = feedparser.parse('http://api.flickr.com/services/feeds/photos_public.gne?tags=frisbee&format=atom')

	for photo in flickrSearchFeed.entries:
		photoID = photo.id.rsplit('/', 1)[1]

		try:
			flickrSyncr.syncPhoto(photoID)
		except FlickrError:
			print 'flickr parse error'



	messages.success(request, 'The social feed was updated successfully (maybe).')
	return HttpResponseRedirect(reverse('home'))

	return render_to_response('index/content.html',
		{'content': 'update'},
		context_instance=RequestContext(request))

def content(request, url):
	try:
		content = get_object_or_404(StaticContent, url=url)
	except StaticContent.DoesNotExist:
		content = ''
	return render_to_response('index/content.html',
		{'content': content},
		context_instance=RequestContext(request))



