# leagues/signals.py

from ultimate.leagues.models import Registrations

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received


def paypal_callback(sender, **kwargs):
    ipn_obj = sender

    print 'PayPal IPN Incoming: {} - {}'.format(ipn_obj.invoice, ipn_obj.payment_status)

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        try:
            registration = Registrations.objects.get(paypal_invoice_id=ipn_obj.invoice)

            if registration.league.is_waitlist(registration.user):
                registration.waitlist = True

            registration.payment_complete = True
            registration.paypal_complete = True
            registration.registered = ipn_obj.payment_date
            registration.save()

            if registration.coupon:
                registration.coupon.process(registration.user)

            print 'PayPal IPN Complete: {} - {}'.format(ipn_obj.invoice, registration.id)
        except Registrations.DoesNotExist:
            print 'PayPal IPN Error: {} - Registration does not exist'.format(ipn_obj.invoice)
        except Exception, ex:
            print 'PayPal IPN Error: {} - Unknown error'.format(ipn_obj.invoice)
            print '%s' % ex

    else:
        print 'PayPal IPN Not Complete: {} - {}'.format(ipn_obj.invoice, ipn_obj.payment_status)


valid_ipn_received.connect(paypal_callback)
