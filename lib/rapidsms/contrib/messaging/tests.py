from django.test import TestCase
from django.core.urlresolvers import reverse

from rapidsms.tests.harness.base import MockBackendRouter, CreateDataTest
from rapidsms.contrib.messaging.forms import MessageForm


class MessagingTest(MockBackendRouter, CreateDataTest, TestCase):
    """
    Test rapidsms.contrib.messaging form and views
    """

    def setUp(self):
        self.contact = self.create_contact()
        self.backend = self.create_backend({'name': 'simple'})
        self.connection = self.create_connection({'backend': self.backend,
                                                  'contact': self.contact})

    def test_contacts_with_connection(self):
        """
        Only contacts with connections are valid options
        """
        connectionless_contact = self.create_contact()
        data = {'text': 'hello!',
                'recipients': [self.contact.id, connectionless_contact.pk]}
        form = MessageForm(data)
        self.assertTrue('recipients' in form.errors)
        self.assertEqual(len(self.outbox), 0)

    def test_valid_send_data(self):
        """
        MessageForm.send should return successfully with valid data
        """
        data = {'text': 'hello!',
                'recipients': [self.contact.id]}
        form = MessageForm(data)
        self.assertTrue(form.is_valid())
        recipients = form.send()
        self.assertTrue(self.contact in recipients)
        self.assertEqual(self.outbox[0].text, data['text'])

    def test_ajax_send_view(self):
        """
        Test AJAX send view with valid data
        """
        data = {'text': 'hello!',
                'recipients': [self.contact.id]}
        response = self.client.post(reverse('send_message'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.outbox[0].text, data['text'])
