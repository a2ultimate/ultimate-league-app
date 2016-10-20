# index/signals.py

from datetime import datetime

from django.db.models import F

from ultimate.leagues.models import League, Registrations

from paypal.standard.ipn.signals import payment_was_successful

def payment_success(sender, **kwargs):
    ipn_obj = sender

    print 'PayPal IPN Incoming: ' + ipn_obj.invoice

    try:
        registration = Registrations.objects.get(paypal_invoice_id=ipn_obj.invoice)

        if registration.league.is_waitlist(registration.user):
            registration.waitlist = True

        registration.payment_complete = True
        registration.paypal_complete = True
        registration.registered = ipn_obj.payment_date
        registration.save()

        if registration.coupon:
            registration.coupon.update(
                use_count=F('use_count') + 1, redeemed_at=datetime.now())

        print 'PayPal IPN Success: ' + ipn_obj.invoice
    except Registrations.DoesNotExist:
        print 'PayPal IPN Error: ' + ipn_obj.invoice + ' - Registration does not exist'
    except Exception, e:
        print 'PayPal IPN Error: ' + ipn_obj.invoice + ' - Unknown error'
        print '%s' % e

payment_was_successful.connect(payment_success)
