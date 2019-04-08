import django.dispatch

sms_notif_created = django.dispatch.Signal(providing_args=["sms_notif"])
ticket_sms_notif_needed = django.dispatch.Signal(providing_args=["sms_notif"])