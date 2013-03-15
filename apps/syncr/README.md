
The twitter app depends on python-twitter, available at: http://code.google.com/p/python-twitter/

The flickr app depends on Beej's Python flickrapi v1.1, available at: http://flickrapi.sourceforge.net/

INSTALLATION / USAGE
Download the most recent tar file or check out the code:
svn checkout http://django-syncr.googlecode.com/svn/trunk/ syncr
Add the syncr app to your PYTHONPATH.
Modify your Django settings file by adding the appropriate modules to your INSTALLED_APPS. Available Django apps are:
'syncr.flickr'
'syncr.youtube'
'syncr.twitter'
'syncr.delicious'
Use the interfaces provided in syncr.app to write scripts for synchronizing your web service data with the Django backend.
For example:
	from syncr.app.flickr import FlickrSyncr
	f = FlickrSyncr(API_KEY, API_SECRET)

	# sync all my photos from the past week...
	f.syncRecentPhotos('username', days=7)

	# sync my favorite photos list
	f.syncPublicFavorites('username')
