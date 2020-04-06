import datetime
import json

from django.test import Client
from django.test import TestCase

from boards.models import Board, Comment, BoardLike, Topic
from users.models import User, Role, get_auth_token, CommentLike
from users.factories import UserFactory


class UserTestCase(TestCase):

    def setUp(self) -> None:
        self.su = User.objects.create_superuser(
            email="sudo@email.com",
            date_of_birth="1970-03-10",
            username="sudoUser",
            password="sudoPassword1"
        )
        self.un_auth = User.objects.create_user(
            email="user@email.com",
            date_of_birth="1980-03-20",
            username="UserUnAuth",
            password="nonAuthPassword"
        )

    def test_get_token(self):
        """Grab api token"""
        t = get_auth_token(self.su)
        self.assertEqual(t, self.su.auth_token)
        # Failed dut to no user found
        self.assertRaises(ValueError, get_auth_token, 4)

    def test_is_staff(self):
        """Ensure superuser creation successfully grants
        needed authorization upon creation"""

        # Assertions
        self.assertTrue(self.su.is_staff)
        self.assertEqual(self.su.role.title, "staff")
        self.assertFalse(self.un_auth.is_staff)
        self.assertEqual(self.un_auth.role.title, "user")

    def test_user_login(self):
        """Login functionality - Django auth login to avoid token
        authentication for each API hit.
        -- Custom Login BELOW--"""

        c1 = Client()
        c2 = Client()

        su = {
            'username': self.su.username,
            'password': "sudoPassword1"
        }
        un_auth = {
            'username': self.un_auth.username,
            'password': "nonAuthPassword"
        }

        su_login = c1.login(
            username=su['username'],
            password=su['password']
        )
        unAuth_login = c2.login(
            username=un_auth['username'],
            password=un_auth['password']
        )
        #  Both should be true == logged in
        self.assertEqual(su_login, unAuth_login)

        # Wrong credentials
        wrongCreds_user = {
            'username': self.su.username,
            'password': "wrongpassword"
        }
        c1.logout()
        c2.logout()
        """Custom Login Start"""
        #  Now check the CUSTOM login function. Returns a serialized
        #  selection of he User model
        su = c1.post(
            '/api/user/login', {
                'username': su['username'],
                'password': su['password']
            }
        ).json()
        self.assertEqual(su['username'], self.su.username)
        self.assertTrue(su['is_staff'])

        un_auth = c2.post(
            '/api/user/login', {
                'username': un_auth['username'],
                'password': un_auth['password']
            }
        ).json()
        self.assertEqual(un_auth['username'], self.un_auth.username)
        self.assertFalse(un_auth['is_staff'])

        wrong_login = c2.post(
            '/api/user/login', {
                'username': wrongCreds_user['username'],
                'password': wrongCreds_user['password']
            }
        )
        self.assertEqual(wrong_login.status_code, 401)

        #  Check string ---Satisfy coverage
        self.assertEqual(su['username'], str(self.su))
        self.assertEqual(un_auth['username'], str(self.un_auth))

        self.assertTrue(self.su.dailyChance)

    def test_user_logout(self):
        c = Client()
        url = '/api/user/logout'

        user = {
            'username': self.un_auth.username,
            'password': "nonAuthPassword"
        }
        fail = c.get(url)
        #  Failed: no log in
        self.assertEqual(fail.status_code, 401)

        userObj = User.objects.get(username=user['username'])
        data = {
            "username": userObj.username,
            "password": user['password']
        }
        login = c.post(
            '/api/user/login',
            data,
        )
        userObj = User.objects.get(username=user['username'])
        self.assertTrue(userObj.online)
        passed = c.get(
            url,
            HTTP_AUTHORIZATION=f'Token {userObj.auth_token}'
        )
        userObj = User.objects.get(username=user['username'])
        self.assertEqual(passed.status_code, 200)
        self.assertFalse(userObj.online)

    def test_create_user_success(self):
        """Test create user functionality"""
        c = Client()
        url = '/api/user/create'
        new_user = {
            'email': 'newuser@email.com',
            'username': 'NewUser',
            'password': 'NewUserPassword',
            'date_of_birth': '1990-06-20'
        }

        successUser = c.post(url, new_user)
        self.assertEqual(successUser.status_code, 201)

        newer_user = {
            'email': 'neweruser@email.com',
            'username': 'neweruser@email.com',
            'password': 'NewUserPassword',
            'date_of_birth': '1990-06-20'
        }

        successUser = User.objects.create_user(
            email=newer_user['email'],
            username=newer_user['username'],
            password=newer_user['password'],
            date_of_birth=newer_user['date_of_birth']
        )
        #  Turns the email into a username
        self.assertEqual(successUser.username, 'neweruser')

    def test_create_user_fail(self):
        """Fail cases of the create user function-
            -No email,
            -Username already exists
        """
        c = Client()
        url = '/api/user/create'
        no_email_user = {
            'username': 'NewerUser',
            'password': 'NewerUserPassword',
            # 'date_of_birth': '1991-06-20'
        }
        duplicate_uname_user1 = {
            'email': 'valid@email.com',
            'username': 'NewerUser',
            'password': 'NewerUserPassword',
            'date_of_birth': '1971-09-26'
        }
        duplicate_uname_user2 = {
            'email': 'validbutdiff@email.com',
            'username': 'NewerUser',
            'password': 'NewerUserPassword',
            'date_of_birth': '1971-09-26'
        }

        #  Fails with no email
        failEmail = c.post(url, no_email_user)
        self.assertEqual(failEmail.status_code, 400)

        #  Pass creation as constant to test username
        passUsername = c.post(url, duplicate_uname_user1)
        self.assertEqual(passUsername.status_code, 201)

        failUsername = c.post(url, duplicate_uname_user2)
        #  Username already exists
        self.assertEqual(failUsername.status_code, 400)

    def test_view_user(self):
        url = f'/api/user/view/{self.un_auth.username}'
        c = Client()
        user = {
            'username': self.un_auth.username,
            'password': "nonAuthPassword"
        }
        c.login(username=user['username'], password=user['password'])
        response = c.get(url)
        self.assertEqual(response.status_code, 200)
        c.logout()
        response = c.get(url)
        # self.assertEqual(response.status_code, 401)

    # Set and check dates for the dailyChance item
    def test_dailyChance(self):
        # Should reset every 24hrs
        self.assertTrue(self.su.dailyChance)

        # API test
        url = '/api/user/item/dailychance'
        c = Client()
        auth_info = {
            'username': self.su.username,
            'password': "sudoPassword1"
        }
        c.login(
            username=auth_info['username'],
            password=auth_info['password']
        )
        auth = User.objects.get(username=auth_info['username'])
        #  dailyChance == True
        self.assertTrue(auth.dailyChance)

        # Manual changes
        auth.set_dailyChance(False)
        self.assertFalse(auth.dailyChance)
        auth.set_dailyChance(True)
        self.assertTrue(auth.dailyChance)

        response = c.put(url)
        #  Passes - dailyChance == False
        self.assertEqual(response.status_code, 202)
        auth = User.objects.get(username=auth_info['username'])
        self.assertFalse(auth.dailyChance)

    def test_dailyChance_timer(self):
        url = '/api/user/item/dailychance'
        c = Client()
        auth_info = {
            'username': self.su.username,
            'password': "sudoPassword1"
        }
        c.login(
            username=auth_info['username'],
            password=auth_info['password']
        )
        auth = User.objects.get(username=auth_info['username'])
        auth.dailyChance = False
        auth.save()
        # Set date back 2 days, this will cause the dailyChance timer to reset
        # and set dailyChance = True
        date = datetime.datetime.now() - datetime.timedelta(hours=48)
        auth.dailyChanceDate = date
        auth.save()
        auth.set_dailyChance(state="reset")
        auth.save()
        self.assertTrue(auth.dailyChance)

        response = c.put(url)
        #  Passes - dailyChance == False
        self.assertEqual(response.status_code, 202)
        auth = User.objects.get(username=auth_info['username'])
        self.assertFalse(auth.dailyChance)

        date = datetime.datetime.now() - datetime.timedelta(hours=20)
        auth.dailyChanceDate = date
        auth.save()
        auth.set_dailyChance(state="reset")
        auth.save()
        auth = User.objects.get(username=auth_info['username'])
        self.assertFalse(auth.dailyChance)

        date = datetime.datetime.now() - datetime.timedelta(hours=48)
        auth.dailyChanceDate = date
        auth.save()
        auth.set_dailyChance(state="reset")
        auth.save()
        auth = User.objects.get(username=auth_info['username'])
        self.assertTrue(auth.dailyChance)

    def test_get_clearance(self):
        self.assertTrue(self.su.is_staff)
        self.assertEqual(self.su.role.title, "staff")
        self.assertEqual(self.su.role.clearance, 1)
        self.assertEqual(self.un_auth.role.clearance, 0)
        self.assertFalse(self.un_auth.get_clearance(2))

    def test_friends(self):
        user1 = {
            'email': 'valid@email.com',
            'username': 'NewerUser',
            'password': 'NewerUserPassword',
            'date_of_birth': '1971-09-26'
        }
        user2 = {
            'email': 'validdddd@email.com',
            'username': 'NewestUser',
            'password': 'NewerUserPassword',
            'date_of_birth': '1971-09-26'
        }
        # create new users
        user1 = User.objects.create_user(**user1)
        user2 = User.objects.create_user(**user2)
        #  assign users to friend of self.su
        self.su.friends.add(user1)
        self.su.friends.add(user2)
        self.su.save()
        #  Users have become registered friends of self.su
        user1_in_friends = (user1 in self.su.get_friends())
        self.assertTrue(user1_in_friends)
        user2_in_friends = (user2 in self.su.get_friends())
        self.assertTrue(user2_in_friends)
        self.assertEqual(
            self.su.friends.get(email=user1.email).username,
            "NewerUser"
        )


class ProfileTestCase(TestCase):

    def setUp(self) -> None:
        self.su = User.objects.create_superuser(
            email="sudo@email.com",
            date_of_birth="1970-03-10",
            username="sudoUser",
            password="sudoPassword1"
        )
        self.u = User.objects.create_user(
            email="user@email.com",
            date_of_birth="1980-03-20",
            username="UserUnAuth",
            password="nonAuthPassword"
        )
        self.c = Client()

    def test_profile_api(self):
        # Hit the view profile API for displayed information

        login = self.c.login(
            username=self.su.username,
            password="sudoPassword1"
        )
        if login:
            def url(endpoint):
                return f'/api/user/profile/{endpoint}'

            r = self.c.get(url(self.u.username))
            self.assertEqual(r.status_code, 200)
            # Test for no user found
            r = self.c.get(url("NoUserNamedThis"))
            # No user found for query so 404 returned
            self.assertEqual(r.status_code, 404)

    def test_display_settings_name(self):
        # Set up the un_auth user stats so that test can measure
        # bool value deciding which fields to display
        requested_user = User.objects.get(username=self.u.username)
        requested_user.first_name = "firstName"
        requested_user.last_name = "LastName"
        requested_user.save()
        requesting_user = User.objects.get(username=self.su.username)
        login = self.c.login(
            username=requesting_user.username,
            password="sudoPassword1"
        )
        if login:
            def url(endpoint):
                return f'/api/user/profile/{endpoint}'

            r = self.c.get(url(self.u.username))
            data = json.loads(r.content)
            self.assertEqual(self.u.username, data['username'])
            self.assertEqual(None, data['first_name'])
            # set user display_full_name = True
            self.assertEqual(data['first_name'], data['last_name'])
            requested_user.display_full_name = True
            requested_user.save()

            r = self.c.get(url(self.u.username))
            self.assertEqual(r.status_code, 200)
            data = json.loads(r.content)

            self.assertEqual(data['first_name'], requested_user.first_name)
            self.assertEqual(data['last_name'], requested_user.last_name)

    def test_friends(self):
        self.assertEqual(self.su.get_friends().count(), 0)
        friend_added = self.su.add_friend(self.u)
        if friend_added:
            self.assertEqual(self.su.get_friends().count(), 1)

    def test_display_settings_date_of_birth(self):
        requested_user = User.objects.get(username=self.u.username)
        requesting_user = User.objects.get(username=self.su.username)
        login = self.c.login(
            username=requesting_user.username,
            password="sudoPassword1"
        )
        if login:
            def url(endpoint):
                return f'/api/user/profile/{endpoint}'

            r = self.c.get(url(self.u.username))
            data = json.loads(r.content)
            # Check display birthdate
            self.assertFalse(requested_user.display_date_of_birth)
            self.assertEqual(data['date_of_birth'], None)
            requested_user.display_date_of_birth = True
            requested_user.save()

            r = self.c.get(url(self.u.username))
            self.assertEqual(r.status_code, 200)
            data = json.loads(r.content)

            self.assertEqual(
                str(requested_user.date_of_birth),
                data['date_of_birth']
            )

    def test_display_settings_location(self):
        requested_user = User.objects.get(username=self.u.username)
        requesting_user = User.objects.get(username=self.su.username)
        login = self.c.login(
            username=requesting_user.username,
            password="sudoPassword1"
        )
        requested_user.location = "Boise, ID"
        requested_user.save()
        if login:
            def url(endpoint):
                return f'/api/user/profile/{endpoint}'

            r = self.c.get(url(requested_user.username))
            data = json.loads(r.content)
            self.assertEqual(data['location'], None)

    def test_display_settings_occupation(self):
        requested_user = User.objects.get(username=self.u.username)
        requesting_user = User.objects.get(username=self.su.username)
        requested_user.occupation = "Dev"
        requested_user.save()
        login = self.c.login(
            username=requesting_user.username,
            password="sudoPassword1"
        )
        if login:
            def url(endpoint):
                return f'/api/user/profile/{endpoint}'

            r = self.c.get(url(requested_user.username))
            data = json.loads(r.content)
            self.assertEqual(data['occupation'], None)

    def test_profile_update_api(self):
        # Test update API
        requesting_user = User.objects.get(username=self.su.username)
        login = self.c.login(
            username=requesting_user.username,
            password="sudoPassword1"
        )
        self.assertEqual(requesting_user.first_name, "")
        if login:
            def url(endpoint):
                return f'/api/user/profile/edit/{endpoint}'

            data = {
                'first_name': 'FirstName',
                'last_name': 'LastName'
            }
            data = json.dumps(data)
            r = self.c.patch(
                url(requesting_user.username),
                data,
                CONTENT_TYPE='application/json',
                HTTP_AUTHORIZATION=f'Token {requesting_user.auth_token}',
            )
            print(r.status_code, r.content)

            requesting_user = User.objects.get(username=self.su.username)
            self.assertEqual(requesting_user.first_name, 'FirstName')
            self.assertEqual(requesting_user.last_name, 'LastName')



class RoleTestCase(TestCase):

    def setUp(self) -> None:
        User.objects.create_superuser(
            email="sudo@email.com",
            date_of_birth="1970-03-10",
            username="sudoUser",
            password="sudoPassword1"
        )
        User.objects.create_user(
            email="user@email.com",
            date_of_birth="1980-03-20",
            username="UserUnAuth",
            password="nonAuthPassword"
        )
        self.su = User.objects.get(email="sudo@email.com")
        self.un_auth = User.objects.get(email="user@email.com")

        self.role1 = Role.objects.create(
            title="ModeRatoR",  # Should get lowered
            desc="Nine rings given to the realm of men",
            clearance=3
        )
        self.role2 = Role.objects.create(
            title="user",  # Should get lowered
            desc="Nine rings given to the realm of men",
            clearance=0
        )

    def test_string(self):
        #  Test str and toLower on save()
        self.assertEqual(str(self.role1), "moderator")

    def test_clearance(self):
        """Tests clearance level and functionality-
        Separate from django authorization"""
        required_clearance = 3

        def clear(role_clearance):
            return True if role_clearance >= required_clearance else False

        role1 = clear(self.role1.clearance)
        role2 = clear(self.role2.clearance)

        self.assertTrue(role1)
        self.assertFalse(role2)

    def test_default_role_set(self):
        """User model should set blank Roles to 'user' role model
        and should create the role if not exists"""
        self.assertTrue(self.su.role, 'staff')
        self.assertTrue(self.un_auth.role, 'user')


class LikeTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="user@email.com",
            date_of_birth="1980-03-20",
            username="UserUnAuth",
            password="nonAuthPassword"
        )
        self.topic = Topic.objects.create(
            title="Tests and testing",
            desc="All things about tests and the testing of such things"
        )
        self.board = Board.objects.create(
            author=self.user,
            title="This is the test title",
            desc="Obviously it is a test, it is only a test",
            content="This could go on and on, so i won't let it.",
            topic=self.topic
        )

    def test_has_liked_count(self):
        self.assertEqual(self.user.has_liked_count, 0)
        BoardLike.objects.create(
            board=self.board,
            author=self.user
        )
        self.assertEqual(self.user.has_liked_count, 1)
        comment = Comment.objects.create(
            board=self.board,
            author=self.user,
            content="This comment is here because I am grateful for this test!"
        )
        CommentLike.objects.create(
            comment=comment,
            author=self.user
        )
        self.assertEqual(self.user.has_liked_count, 2)


class SerializerTest(TestCase):

    def setUp(self) -> None:
        self.auth_user = UserFactory()
        self.unAuth_user = UserFactory()

    def test_factory_success(self):
        self.assertEqual(self.auth_user.is_active, self.unAuth_user.is_active)
