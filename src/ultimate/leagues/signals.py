# leagues/signals.py

from ultimate.leagues.models import Registrations

from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received


def paypal_callback(sender, **kwargs):
    ipn_obj = sender

    print(('PayPal IPN Incoming: {} - {}'.format(ipn_obj.invoice, ipn_obj.payment_status)))

    if ipn_obj.payment_status == ST_PP_COMPLETED:
        if ipn_obj.receiver_email != 'treasurer@annarborultimate.org':
            # Not a valid payment
            print(('PayPal IPN Error: {} - invalid receiver_email'.format(ipn_obj.invoice)))
            return

        try:
            registration = Registrations.objects.get(paypal_invoice_id=ipn_obj.invoice)

            if ipn_obj.mc_gross != registration.paypal_price or ipn_obj.mc_currency != 'USD':
                # Not a valid payment amount
                print(('PayPal IPN Error: {} - invalid mc_gross'.format(ipn_obj.invoice)))
                return

            if registration.league.is_waitlisting_registrations(registration.user):
                registration.waitlist = True

            registration.payment_complete = True
            registration.paypal_complete = True
            registration.registered = ipn_obj.payment_date
            registration.save()

            if registration.coupon:
                registration.coupon.process(registration.user)

            print(('PayPal IPN Complete: {} - {} - {} - {}'.format(ipn_obj.invoice, registration.id, ipn_obj.mc_gross, registration.paypal_price)))
        except Registrations.DoesNotExist:
            print(('PayPal IPN Error: {} - Registration does not exist'.format(ipn_obj.invoice)))
        except Exception as ex:
            print(('PayPal IPN Error: {} - Unknown error'.format(ipn_obj.invoice)))
            print(('{}'.format(ex)))

    else:
        print(('PayPal IPN Not Complete: {} - {}'.format(ipn_obj.invoice, ipn_obj.payment_status)))


valid_ipn_received.connect(paypal_callback)
