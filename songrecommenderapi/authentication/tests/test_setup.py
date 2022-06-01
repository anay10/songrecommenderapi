from rest_framework.test import APITestCase
from django.urls import reverse
from faker import Faker

class TestSetUp(APITestCase):
    #we will declare things we will reuse like urls and testing data
    #for every test setup and teardown will run
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.fake = Faker()

        #test data
        self.user_data = {
            # 'email' : 'email@test.com',
            # 'username' : 'email',
            # 'password' : 'email@test.com'

            'email' : self.fake.email(),
            'username' : self.fake.email().split('@')[0],
            'password' : self.fake.email()

        }
        
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()
