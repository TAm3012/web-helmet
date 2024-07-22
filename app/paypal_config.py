import paypalrestsdk
from django.conf import settings

paypalrestsdk.configure({
    "sandox": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})
