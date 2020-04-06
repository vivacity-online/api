from django.test import TestCase, Client
from users.models import User


class WalletTestCase(TestCase):

    def setUp(self) -> None:
        c = Client()
        url = '/api/user/create'
        new_user = {
            'email': 'newuser@email.com',
            'username': 'NewUser',
            'password': 'NewUserPassword',
            'date_of_birth': '1990-06-20'
        }
        c.post(url, new_user)
        self.user1 = User.objects.get(username=new_user['username'])

        newer_user = {
            'email': 'neweruser@email.com',
            'username': 'neweruser@email.com',
            'password': 'NewUserPassword',
            'date_of_birth': '1990-06-20'
        }

        self.user2 = User.objects.create_user(
            email=newer_user['email'],
            username=newer_user['username'],
            password=newer_user['password'],
            date_of_birth=newer_user['date_of_birth']
        )

    def test_wallet_creation(self):
        self.assertTrue(self.user1.wallet is not None)
        self.assertEqual(
            self.user1.wallet.shinies,
            self.user2.wallet.shinies
        )
        self.assertEqual(self.user1.wallet.owner, self.user1)

    def test_currency_transaction(self):
        self.assertEqual(self.user1.wallet.shinies, 0)
        wallet = self.user1.wallet
        wallet.transact_currency(20, 'shinies')
        self.assertEqual(wallet.shinies, 20)
        wallet.transact_currency(-10, 'shinies')
        self.assertEqual(wallet.shinies, 10)

        self.assertEqual(self.user1.wallet.muns, 0)
        wallet = self.user1.wallet
        wallet.transact_currency(20, 'muns')
        self.assertEqual(wallet.muns, 20)
        wallet.transact_currency(-10, 'muns')
        self.assertEqual(wallet.muns, 10)

    def test_send_currency(self):
        wallet1 = self.user1.wallet
        wallet2 = self.user2.wallet
        self.assertEqual(wallet1.shinies, 0)
        self.assertEqual(wallet2.shinies, 0)
        self.assertEqual(wallet1.muns, 0)
        self.assertEqual(wallet2.muns, 0)

        # Plump wallet1 so that a trade can take place
        wallet1.transact_currency(20, 'shinies')

        wallet1.send_currency(wallet2, 7, 'shinies')
        self.assertEqual(wallet1.shinies, 13)
        self.assertEqual(self.user2.wallet.shinies, 7)

        # Plump wallet2 muns
        wallet2.transact_currency(34, 'muns')

        self.assertEqual(wallet2.muns, 34)
        self.assertEqual(wallet1.muns, 0)
        wallet2.send_currency(wallet1, 20, 'muns')
        self.assertEqual(wallet1.muns, 20)

        with self.assertRaises(AttributeError) as e:
            # No attr for 'walrus'
            wallet1.send_currency(wallet2, 20, 'walrus')

        with self.assertRaises(TypeError) as e:
            # Must send to wallet object instance
            # not user
            wallet1.send_currency(self.user2, 20, 'muns')

        with self.assertRaises(TypeError) as e:
            # Must send an integer ! str('twenty')
            wallet1.send_currency(wallet2, 'twenty', 'muns')

    def test_balance(self):
        wallet1 = self.user1.wallet
        self.assertEqual(wallet1.balance, {'shinies': 0, 'muns': 0})

        # plump wallet1
        wallet1.transact_currency(30, 'shinies')
        self.assertEqual(wallet1.balance, {'shinies': 30, 'muns': 0})
