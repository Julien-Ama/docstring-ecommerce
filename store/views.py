from pprint import pprint
import json
import stripe
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from accounts.models import Shopper, ShippingAddress
from shop import settings
from store.models import Product, Cart, Order


stripe.api_key = settings.STRIPE_API_KEY


def index(request):
    products = Product.objects.all()

    return render(request, 'store/index.html', context={"products": products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request, 'store/detail.html', context={"product": product})

def add_to_cart(request, slug):
    user = request.user
    product = get_object_or_404(Product, slug=slug)
    cart, _ = Cart.objects.get_or_create(user=user) # _ 2 éléments à gauche et à droite du symbole d'égalité
    order, created = Order.objects.get_or_create(user=user,
                                                 ordered=False,
                                                 product=product)

    if created:
        cart.orders.add(order)
        cart.save()
    else:
        order.quantity += 1
        order.save()

    return redirect(reverse("product", kwargs={"slug": slug}))


def cart(request):
    cart = get_object_or_404(Cart, user=request.user)

    return render(request, 'store/cart.html', context={"orders": cart.orders.all()})


def create_checkout_session(request):
    cart = request.user.cart
    line_items = [{"price": order.product.stripe_id,
                   "quantity": order.quantity} for order in cart.orders.all()]

    session = stripe.checkout.Session.create(
        locale="fr",
        line_items=line_items,
        mode='payment',
        customer_email=request.user.email,
        shipping_address_collection={"allowed_countries": ["FR","US", "CA"]},
        success_url=request.build_absolute_uri(reverse('checkout-success')),
        cancel_url='http://127.0.0.1:8000',
    )

    return redirect(session.url, code=303)


def checkout_success(request):
    # cart = Cart.objects.get(user=request.user)
    # cart.delete()

    return render(request, 'store/success.html')


def delete_cart(request):

    # cart = request.user.cart
    # if cart:
    if cart := request.user.cart:       #walrus(morse)
        cart.orders.all().delete()
        cart.delete()

    return redirect('index')

# @csrf_exempt
# def stripe_webhook(request):
#   payload = request.body
#   event = None
#
#   try:
#     event = stripe.Event.construct_from(
#       json.loads(payload), stripe.api_key
#     )
#   except ValueError as e:
#     # Invalid payload
#     return HttpResponse(status=400)
#
#   # Handle the event
#   if event.type == 'payment_intent.succeeded':
#     payment_intent = event.data.object # contains a stripe.PaymentIntent
#     # Then define and call a method to handle the successful payment intent.
#     # handle_payment_intent_succeeded(payment_intent)
#   elif event.type == 'payment_method.attached':
#     payment_method = event.data.object # contains a stripe.PaymentMethod
#     # Then define and call a method to handle the successful attachment of a PaymentMethod.
#     # handle_payment_method_attached(payment_method)
#   # ... handle other event types
#   else:
#     print('Unhandled event type {}'.format(event.type))
#
#   return HttpResponse(status=200)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = "whsec_1b32becf79f2bc60e1a4c2f6ae0bc317cfb49545f10c4835b1a0a90ba9303183"
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        data = event['data']['object']
        pprint(data)
        try:
            user = get_object_or_404(Shopper, email=data['customer_details']['email'])
        except KeyError:
            return HttpResponse("Invalid user email", status=404)

        complete_order(data=data, user=user)
        save_shipping_address(data=data, user=user)

        return HttpResponse(status=200)

    # Passed signature verification
    return HttpResponse(status=200)

def complete_order(data, user):
    pprint(data)

    user.stripe_id = data['customer']
    user.cart.delete()
    user.save()
    return HttpResponse(status=200)

def save_shipping_address(data, user):
    """
      "shipping_details": {
    "address": {
      "city": "Toulouse",
      "country": "FR",
      "line1": "1 Rue des Champs Elys\u00e9es",
      "line2": null,
      "postal_code": "31500",
      "state": ""
    },
    "name": "domicile"
  },
    """
    try:
        address = data["shipping"]["address"]
        name = data["shipping"]["name"]
        city = address["city"]
        country = address["country"]
        line1 = address["line1"]
        line2 = address["line2"]
        zip_code = address["postal_code"]
    except KeyError:
        return HttpResponse(status=400)

    print(line2)
    ShippingAddress.objects.get_or_create(user=user,
                                          name=name,
                                          city=city,
                                          country=country.lower(),
                                          address_1=line1,
                                          address_2=line2 or "",
                                          zip_code=zip_code)

    return HttpResponse(status=200)