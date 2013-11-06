# index/signals.py

from datetime import datetime

from ultimate.leagues.models import League, Registrations

from paypal.standard.ipn.signals import payment_was_successful

def payment_success(sender, **kwargs):
	ipn_obj = sender

	print 'PayPal IPN Incoming: ' + ipn_obj.invoice

	try:
		registration = Registrations.objects.get(paypal_invoice_id=ipn_obj.invoice)

		if registration.league.is_waitlist(registration.user):
			registration.waitlist = 1

		registration.paypal_complete = 1
		registration.registered = datetime.now()
		registration.save()

		print 'PayPal IPN Success: ' + ipn_obj.invoice
	except Registrations.DoesNotExist:
		print 'PayPal IPN Error: ' + ipn_obj.invoice + ' - Registration does not exist'
	except Exception, e:
		print 'PayPal IPN Error: ' + ipn_obj.invoice + ' - Unknown error'
		print '%s' % e

payment_was_successful.connect(payment_success)
