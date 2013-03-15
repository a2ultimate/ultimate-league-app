# index/signals.py

from a2ultimate.leagues.models import Registrations

from paypal.standard.ipn.signals import payment_was_successful

def payment_success(sender, **kwargs):
	ipn_obj = sender
	try:
		registration = Registrations.objects.get(paypal_invoice_id=ipn_obj.invoice)
		registration.paypal_complete = 1
		registration.save()
	except Registrations.DoesNotExist:
		print 'PayPal Error - No Invoice ID Found - ' + ipn_obj.invoice

payment_was_successful.connect(payment_success)
