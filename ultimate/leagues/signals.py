# index/signals.py

from datetime import datetime

from ultimate.leagues.models import Registrations

from paypal.standard.ipn.signals import payment_was_successful

def payment_success(sender, **kwargs):
	ipn_obj = sender

	print 'PayPal IPN Incoming: ' + ipn_obj.invoice

	try:
		registration = Registrations.objects.get(paypal_invoice_id=ipn_obj.invoice)
		registration.paypal_complete = 1
		registration.registered = datetime.now()
		registration.save()

		print 'PayPal IPN Success: ' + ipn_obj.invoice
	except Registrations.DoesNotExist:
		print 'PayPal IPN Error: ' + ipn_obj.invoice

payment_was_successful.connect(payment_success)
