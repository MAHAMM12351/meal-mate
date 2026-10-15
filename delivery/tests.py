from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import Cart, Customer, Item, Restaurant


class CartPaymentFlowTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            username='meal_guest',
            password='password',
            email='guest@example.com',
            mobile='9876543210',
            address='123 Main Street',
        )
        self.restaurant = Restaurant.objects.create(
            name='Green Table',
            cuisine='Healthy',
            rating=4.5,
        )
        self.item = Item.objects.create(
            restaurant=self.restaurant,
            name='Garden Bowl',
            description='Fresh vegetables and grains',
            price=12.5,
        )

    def test_add_to_cart_redirects_to_cart_with_payment_next_step(self):
        response = self.client.get(
            reverse('add_to_cart', args=[self.item.id, self.customer.username])
        )

        self.assertRedirects(
            response,
            reverse('show_cart', args=[self.customer.username]),
        )
        cart_response = self.client.get(response.url)
        self.assertContains(cart_response, self.item.name)
        self.assertContains(cart_response, 'Continue to payment')
        self.assertContains(
            cart_response,
            reverse('checkout', args=[self.customer.username]),
        )

    @patch('delivery.views.razorpay.Client')
    @patch('delivery.views.settings.RAZORPAY_KEY_SECRET', 'test_secret')
    @patch('delivery.views.settings.RAZORPAY_KEY_ID', 'rzp_test_example')
    def test_checkout_displays_razorpay_button_with_order_details(self, razorpay_client):
        cart = Cart.objects.create(customer=self.customer)
        cart.items.add(self.item)
        razorpay_client.return_value.order.create.return_value = {
            'id': 'order_test_123',
        }

        response = self.client.get(
            reverse('checkout', args=[self.customer.username])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pay with Razorpay (Test Mode)')
        self.assertContains(response, 'No real payment will be taken')
        self.assertContains(response, 'order_test_123')
        self.assertContains(response, 'key: "rzp_test_example"')
        self.assertContains(response, 'amount: "1250"')
        razorpay_client.return_value.order.create.assert_called_once_with(data={
            'amount': 1250,
            'currency': 'INR',
            'payment_capture': '1',
        })

    def test_empty_cart_does_not_show_payment_button(self):
        response = self.client.get(
            reverse('checkout', args=[self.customer.username])
        )

        self.assertContains(response, 'Your cart is empty!')
        self.assertNotContains(response, 'Pay with Razorpay')

    @patch('delivery.views.settings.RAZORPAY_KEY_ID', '')
    @patch('delivery.views.settings.RAZORPAY_KEY_SECRET', '')
    def test_checkout_explains_missing_razorpay_configuration(self):
        cart = Cart.objects.create(customer=self.customer)
        cart.items.add(self.item)

        response = self.client.get(
            reverse('checkout', args=[self.customer.username])
        )

        self.assertContains(response, 'Online payment is not configured.')
        self.assertNotContains(response, 'Pay with Razorpay')

    @patch('delivery.views.settings.RAZORPAY_KEY_ID', 'rzp_live_example')
    @patch('delivery.views.settings.RAZORPAY_KEY_SECRET', 'live_secret')
    @patch('delivery.views.razorpay.Client')
    def test_checkout_rejects_live_razorpay_keys(self, razorpay_client):
        cart = Cart.objects.create(customer=self.customer)
        cart.items.add(self.item)

        response = self.client.get(
            reverse('checkout', args=[self.customer.username])
        )

        self.assertContains(response, 'only supports Razorpay test-mode keys')
        self.assertNotContains(response, 'Pay with Razorpay')
        razorpay_client.assert_not_called()
