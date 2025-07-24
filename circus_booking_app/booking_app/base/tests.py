from django.test import TestCase

# Create your tests here
from django.test import TestCase, Client as DjangoClient
from django.urls import reverse
from django.contrib.auth.models import User
from .models import TrainerProfile, Client, Session, Booking

class TrainerClientTests(TestCase):
    def setUp(self):
        # Create a trainer user and profile
        self.trainer_user = User.objects.create_user(username='trainer1', password='pass123')
        self.trainer_profile = TrainerProfile.objects.create(
            user=self.trainer_user,
            business_name='CircusFit',
            email='trainer@example.com',
            phone='123456789'
        )
        # Create a client user and profile
        self.client_user = User.objects.create_user(username='client1', password='pass123')
        self.client_profile = Client.objects.create(user=self.client_user, can_self_book=True)
        self.client_profile.trainers.add(self.trainer_profile)
        # Create a session
        self.session = Session.objects.create(
            trainer=self.trainer_profile,
            title='Juggling 101',
            date='2030-01-01 10:00',
            max_clients=5,
            price=20.00,
            session_type='Workshop'
        )
        self.client = DjangoClient()

    def test_trainer_dashboard_access(self):
        self.client.login(username='trainer1', password='pass123')
        response = self.client.get(reverse('trainer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trainer Dashboard')

    def test_client_dashboard_access(self):
        self.client.login(username='client1', password='pass123')
        response = self.client.get(reverse('client_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Client Dashboard')

    def test_client_trainer_relationship(self):
        self.assertIn(self.trainer_profile, self.client_profile.trainers.all())

    def test_session_creation(self):
        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(self.session.trainer, self.trainer_profile)

    def test_booking_creation(self):
        Booking.objects.create(client=self.client_profile, session=self.session, status='booked')
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.client, self.client_profile)
        self.assertEqual(booking.session, self.session)

    def test_client_can_book_session(self):
        self.client.login(username='client1', password='pass123')
        response = self.client.post(reverse('book_session', args=[self.session.id]))
        self.assertRedirects(response, reverse('client_dashboard'))
        self.assertEqual(Booking.objects.count(), 1)

    def test_trainer_can_create_client(self):
        self.client.login(username='trainer1', password='pass123')
        response = self.client.post(reverse('trainer_client_create'), {
            'username': 'client2',
            'email': 'client2@example.com',
            'first_name': 'Client',
            'last_name': 'Two',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'can_self_book': True,
        })
        self.assertEqual(Client.objects.filter(user__username='client2').count(), 1)

    def test_client_dashboard_shows_trainers(self):
        self.client.login(username='client1', password='pass123')
        response = self.client.get(reverse('client_dashboard'))
        self.assertContains(response, 'CircusFit')