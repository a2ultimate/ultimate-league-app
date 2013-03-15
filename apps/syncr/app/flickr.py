import calendar
from datetime import datetime
import flickrapi
import math
from time import strptime

from django.core.exceptions import ObjectDoesNotExist
from django.template import defaultfilters
from django.utils.encoding import smart_str

from syncr.flickr.models import *
from syncr.flickr.slug import get_unique_slug_for_photo

class FlickrSyncr:
	"""
	FlickrSyncr objects sync flickr photos, photo sets, and favorites
	lists with the Django backend.

	It does not currently sync user meta-data. Photo, PhotoSet, and
	FavoriteList objects include some meta-data, but are mostly Django
	ManyToManyFields to Photo objects.

	This app requires Beej's flickrapi library. Available at:
	http://flickrapi.sourceforge.net/
	"""
	def __init__(self, flickr_key, flickr_secret):
		"""
		Construct a new FlickrSyncr object.

		Required arguments
		  flickr_key: a Flickr API key string
		  flickr_secret: a Flickr secret key as a string
		"""
		self.flickr = flickrapi.FlickrAPI(flickr_key, flickr_secret, format='xmlnode')

	def user2nsid(self, username):
		"""
		Convert a flickr username to an NSID
		"""
		return self.flickr.people_findByUsername(username=username).user[0]['nsid']

	# Removed getPhotoSizeURLs() here

	def getPhotoSizes(self, photo_id):
		"""
		Return a dictionary of image sizes for a flickr photo.

		Required arguments
		  photo_id: a flickr photo id as a string
		"""
		result = self.flickr.photos_getSizes(photo_id=photo_id)
		sizes = dict()
		size_labels = ('Thumbnail','Small','Medium','Large','Original')

		# Set defaults to None
		for label in size_labels:
			sizes[label] = {'width': None, 'height': None}

		# Set values given by flickr
		for el in result.sizes[0].size:
			if el['label'] in size_labels:
				sizes[el['label']]['width'] = el['width']
				sizes[el['label']]['height'] = el['height']
		return sizes

	def getGeoLocation(self, photo_id):
		"""
		Obtain the geographical location information for a photo_id

		Required Arguments
		  photo_id: A flickr photo id
		"""
		geo_data = {'latitude': None, 'longitude': None, 'accuracy': None,
					'locality': '', 'county': '', 'region': '', 'country': ''}
		try:
			result = self.flickr.photos_geo_getLocation(photo_id=photo_id)
		except flickrapi.FlickrError:
			return geo_data

		geo_data['latitude'] = float(result.photo[0].location[0]['latitude'])
		geo_data['longitude'] = float(result.photo[0].location[0]['longitude'])
		geo_data['accuracy'] = result.photo[0].location[0]['accuracy']

		for bit in ('locality', 'county', 'region', 'country',):
			if hasattr(result.photo[0].location[0], bit):
				geo_data[bit] = getattr(result.photo[0].location[0], bit)[0].text

		return geo_data

	def _syncPhoto(self, photo_xml, refresh=False):
		"""
		Synchronize a flickr photo with the Django backend.

		Required Arguments
		  photo_xml: A flickr photos in Flickrapi's REST XMLNode format
		"""
		if photo_xml.photo[0]['media'] != 'photo': # Ignore media like videos
			return None
		photo_id = photo_xml.photo[0]['id']

		# if we're refreshing this data, then delete the Photo first...
		if refresh:
			try:
				p = Photo.objects.get(flickr_id = photo_id)
				p.delete()
			except ObjectDoesNotExist:
				pass

		sizes = self.getPhotoSizes(photo_id)
		geo_data = self.getGeoLocation(photo_id)

		taken_date = datetime(*strptime(photo_xml.photo[0].dates[0]['taken'], "%Y-%m-%d %H:%M:%S")[:7])
		upload_date = datetime.fromtimestamp(int(photo_xml.photo[0].dates[0]['posted']))
		update_date = datetime.fromtimestamp(int(photo_xml.photo[0].dates[0]['lastupdate']))

		proposed_slug = defaultfilters.slugify(photo_xml.photo[0].title[0].text.lower())
		slug = get_unique_slug_for_photo(taken_date, proposed_slug)

		try:
			original_secret = photo_xml.photo[0]['originalsecret']
		except KeyError:
			original_secret = ''


		default_dict = {
			'flickr_id': photo_xml.photo[0]['id'],
			'owner': photo_xml.photo[0].owner[0]['username'],
			'owner_nsid': photo_xml.photo[0].owner[0]['nsid'],
			'title': photo_xml.photo[0].title[0].text, # TODO: Typography
			'slug': slug,
			'description': photo_xml.photo[0].description[0].text,
			'taken_date': taken_date,
			'upload_date': upload_date,
			'update_date': update_date,
			'photopage_url': photo_xml.photo[0].urls[0].url[0].text,
			'farm': photo_xml.photo[0]['farm'],
			'server': photo_xml.photo[0]['server'],
			'secret': photo_xml.photo[0]['secret'],
			'original_secret': original_secret,
			'thumbnail_width': sizes['Thumbnail']['width'],
			'thumbnail_height': sizes['Thumbnail']['height'],
			'small_width': sizes['Small']['width'],
			'small_height': sizes['Small']['height'],
			'medium_width': sizes['Medium']['width'],
			'medium_height': sizes['Medium']['height'],
			'large_width': sizes['Large']['width'],
			'large_height': sizes['Large']['height'],
			'original_width': sizes['Original']['width'] or 0,
			'original_height': sizes['Original']['height'] or 0,
			'license': photo_xml.photo[0]['license'],
			'geo_latitude': geo_data['latitude'],
			'geo_longitude': geo_data['longitude'],
			'geo_accuracy': geo_data['accuracy'],
			'geo_locality': geo_data['locality'],
			'geo_county': geo_data['county'],
			'geo_region': geo_data['region'],
			'geo_country': geo_data['country'],
		}

		obj, created = Photo.objects.get_or_create(flickr_id=photo_xml.photo[0]['id'], defaults=default_dict)

		# update if something changed
		if obj.update_date < update_date:
			# Never overwrite URL-relevant attributes
			default_dict['slug'] = obj.slug
			default_dict['taken_date'] = obj.taken_date

			updated_obj = Photo(pk=obj.pk, **default_dict)
			updated_obj.save()

		return obj

	def _syncPhotoXMLList(self, photos_xml):
		"""
		Synchronize a list of flickr photos with Django ORM.

		Required Arguments
		  photos_xml: A list of photos in Flickrapi's REST XMLNode format.
		"""
		photo_list = []
		for photo in photos_xml:
			photo_result = self.flickr.photos_getInfo(photo_id = photo['id'])
			photo_list.append(self._syncPhoto(photo_result))
		return photo_list

	def syncPhoto(self, photo_id, refresh=False):
		"""
		Synchronize a single flickr photo with Django ORM.

		Required Arguments
		  photo_id: A flickr photo_id
		Optional Arguments
		  refresh: A boolean, if true the Photo will be re-sync'd with flickr
		"""
		photo_result = self.flickr.photos_getInfo(photo_id = photo_id)
		photo = self._syncPhoto(photo_result, refresh=refresh)
		return photo

	def syncPhotoSet(self, photoset_id, order=None):
		"""
		Synchronize a single flickr photo set based on the set id.

		Required arguments
		  photoset_id: a flickr photoset id number as a string
		"""
		photoset_xml = self.flickr.photosets_getInfo(photoset_id = photoset_id)
		nsid = photoset_xml.photoset[0]['owner']
		username = self.flickr.people_getInfo(user_id = nsid).person[0].username[0].text
		result = self.flickr.photosets_getPhotos(photoset_id = photoset_id)
		page_count = int(result.photoset[0]['pages'])
		primary = self.syncPhoto(photoset_xml.photoset[0]['primary'])

		d_photoset, created = PhotoSet.objects.get_or_create(
				flickr_id = photoset_id,
				defaults = {
			'owner': username,
			'flickr_id': result.photoset[0]['id'],
			'primary': None,
			'title': photoset_xml.photoset[0].title[0].text,
			'description': photoset_xml.photoset[0].description[0].text,
			'primary': primary.id,
			'order': order
			}
		)
		if not created: # update it
			d_photoset.owner  = username
			d_photoset.title  = photoset_xml.photoset[0].title[0].text
			d_photoset.description=photoset_xml.photoset[0].description[0].text
			d_photoset.primary = primary
			d_photoset.save()

		page_count = int(result.photoset[0]['pages'])

		for page in range(1, page_count+1):
			if page > 1:
				result = self.flickr.photosets_getPhotos(
					photoset_id = photoset_id, page = page+1)
			photo_list = self._syncPhotoXMLList(result.photoset[0].photo)
			for photo in photo_list:
				if photo is not None:
					d_photoset.photos.add(photo)

		# Set primary photo and order
		d_photoset.primary = Photo.objects.get(flickr_id__exact=result.photoset[0]['primary']) # TODO: This query isn't in need, we have the ``flickr_id``...
		d_photoset.order = order
		d_photoset.save()

