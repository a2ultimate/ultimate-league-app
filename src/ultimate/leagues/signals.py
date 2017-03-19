# leagues/signals.py

from django.db.models import F

from ultimate.leagues.models import League, Registrations

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received


def paypal_callback(sender, **kwargs):
    ipn_obj = sender

    print 'PayPal IPN Incoming: ' + ipn_obj.invoice + ' - ' + ipn_obj.payment_status

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            registration = Registrations.objects.get(paypal_invoice_id=ipn_obj.invoice)

            if registration.league.is_waitlist(registration.user):
                registration.waitlist = True

            registration.payment_complete = True
            registration.paypal_complete = True
            registration.registered = ipn_obj.payment_date
            registration.save()

            print 'PayPal IPN Complete: ' + ipn_obj.invoice + ' - ' + str(registration.id)
        except Registrations.DoesNotExist:
            print 'PayPal IPN Error: ' + ipn_obj.invoice + ' - Registration does not exist'
        except Exception, e:
            print 'PayPal IPN Error: ' + ipn_obj.invoice + ' - Unknown error'
            print '%s' % e

    else:
        print 'PayPal IPN Not Complete: ' + ipn_obj.invoice + ' - ' + ipn_obj.payment_status


valid_ipn_received.connect(paypal_callback)
