from .test_setup import TestSetUp
from ..models import User

#here we will define our test methods
#name of all the test methods MUST have a prefix "test"
class TestViews(TestSetUp):
    #a function to test if user can register without any data
    def test_user_cannot_register_with_no_data(self):
        #we write sessions i.e. comparisons or checks

        #with APITestCase class we get access to APIClient which is used below
        res = self.client.post(self.register_url)

        #since we are not passing any data for registration we expect this session
        #response to be an error
        self.assertEqual(res.status_code, 400)

    #a function to test if a user can register correctly
    def test_user_can_register_correctly(self):
        res = self.client.post(self.register_url, self.user_data, format = "json")
        self.assertEqual(res.data['email'], self.user_data['email'])
        self.assertEqual(res.data['username'], self.user_data['username'])
        self.assertEqual(res.status_code, 201)

    #a function to test a user cannot login with unverified email
    def test_user_cannot_login_with_unverified_email(self):
        #register
        self.client.post(self.register_url, self.user_data, format = "json")

        #make request to login
        res =  self.client.post(self.login_url, self.user_data, format = "json")

        self.assertEqual(res.status_code, 401)

    #a function to test that a user can login after verification of email
    def test_user_can_login_after_verification(self):
        #register
        response = self.client.post(self.register_url, self.user_data, format = "json")
        email = response.data['email']
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()

        #make request to login
        res =  self.client.post(self.login_url, self.user_data, format = "json")

        self.assertEqual(res.status_code, 200)
