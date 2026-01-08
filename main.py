from unittest import mock
import re
import unittest
import uuid


class UsernameException(Exception):
    pass


class PaymentException(Exception):
    pass


class CreditCardException(Exception):
    pass


class Payment:

    def __init__(self, amount, actor, target, note):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note


class User:

    def __init__(self, username):
        self.credit_card_number = None
        self.balance = 0.0

        if self._is_valid_username(username):
            self.username = username
        else:
            raise UsernameException('Username not valid.')

    def retrieve_feed(self):
        # TODO: add code here
        return []

    def add_friend(self, new_friend):
        # TODO: add code here
        pass

    def add_to_balance(self, amount):
        self.balance += float(amount)

    def add_credit_card(self, credit_card_number):
        if self.credit_card_number is not None:
            raise CreditCardException('Only one credit card per user!')

        if self._is_valid_credit_card(credit_card_number):
            self.credit_card_number = credit_card_number

        else:
            raise CreditCardException('Invalid credit card number.')

    def pay(self, target, amount, note):
        try:
            return self.pay_with_balance(target, amount, note)
        except PaymentException:
            # Shouldn't charge all balance and only the rest in card?
            return self.pay_with_card(target, amount, note)

    def pay_with_card(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.credit_card_number is None:
            raise PaymentException('Must have a credit card to make a payment.')

        self._charge_credit_card(self.credit_card_number, amount)
        payment = Payment(amount, self, target, note)
        target.add_to_balance(amount)

        return payment

    def pay_with_balance(self, target, amount, note):
        amount = float(amount)

        if self.username == target.username:
            raise PaymentException('User cannot pay themselves.')

        elif amount <= 0.0:
            raise PaymentException('Amount must be a non-negative number.')

        elif self.balance < amount:
            raise PaymentException('Insufficient funds.')

        self.add_to_balance(-amount)
        target.add_to_balance(amount)
        payment = Payment(amount, self, target, note)
        return payment

    def _is_valid_credit_card(self, credit_card_number):
        return credit_card_number in ["4111111111111111", "4242424242424242"]

    def _is_valid_username(self, username):
        return re.match('^[A-Za-z0-9_\\-]{4,15}$', username)

    def _charge_credit_card(self, credit_card_number, amount):
        # magic method that charges a credit card thru the card processor
        pass


class MiniVenmo:
    def create_user(self, username, balance, credit_card_number):
        user = User(username)
        user.add_to_balance(balance)
        if credit_card_number is not None:
            user.add_credit_card(credit_card_number)
        return user

    def render_feed(self, feed):
        # Bobby paid Carol $5.00 for Coffee
        # Carol paid Bobby $15.00 for Lunch
        # TODO: add code here
        pass

    @classmethod
    def run(cls):
        venmo = cls()

        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        try:
            # should complete using balance
            bobby.pay(carol, 5.00, "Coffee")
 
            # should complete using card
            carol.pay(bobby, 15.00, "Lunch")
        except PaymentException as e:
            print(e)

        feed = bobby.retrieve_feed()
        venmo.render_feed(feed)

        bobby.add_friend(carol)


class TestUser(unittest.TestCase):

    def test_this_works(self):
        with self.assertRaises(UsernameException):
            raise UsernameException()

    def test_user_creation(self):
        venmo = MiniVenmo()
        me = venmo.create_user("Danilo", 15.22, "4111111111111111")
        self.assertEqual(me.username, "Danilo")
        self.assertEqual(me.balance, 15.22)
        self.assertEqual(me.credit_card_number, "4111111111111111")

    def test_user_creation_without_credit_card(self):
        venmo = MiniVenmo()
        me = venmo.create_user("Danilo", 122.51, None)
        self.assertEqual(me.username, "Danilo")
        self.assertEqual(me.balance, 122.51)
        self.assertIsNone(me.credit_card_number)

    def test_payment_balance(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        payment1 = bobby.pay(carol, 1.50, "Tea")
        self.assertEqual(payment1.amount, 1.50)
        self.assertEqual(payment1.actor, bobby)
        self.assertEqual(payment1.target, carol)
        self.assertEqual(payment1.note, "Tea")

        self.assertAlmostEqual(bobby.balance, 3.50, places=5)
        self.assertAlmostEqual(carol.balance, 11.50, places=5)

        payment2 = carol.pay(bobby, 3.25, "Box")
        self.assertEqual(payment2.amount, 3.25)
        self.assertEqual(payment2.actor, carol)
        self.assertEqual(payment2.target, bobby)
        self.assertEqual(payment2.note, "Box")
        self.assertNotEqual(payment1.id, payment2.id)

        self.assertAlmostEqual(bobby.balance, 6.75, places=5)
        self.assertAlmostEqual(carol.balance, 8.25, places=5)

    def test_payment_bobby_cant_pay_for_himself(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        with self.assertRaises(PaymentException):
            bobby.pay(bobby, 1.50, "Tea")
        with self.assertRaises(PaymentException):
            bobby.pay_with_balance(bobby, 1.50, "Tea")
        with self.assertRaises(PaymentException):
            bobby.pay_with_card(bobby, 1.50, "Tea")

    def test_payment_carol_cant_pay_negative_amount(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")
        with self.assertRaises(PaymentException):
            carol.pay(bobby, -1.50, "Tea")
        with self.assertRaises(PaymentException):
            carol.pay_with_balance(bobby, -1.50, "Tea")
        with self.assertRaises(PaymentException):
            carol.pay_with_card(bobby, -1.50, "Tea")

    def test_payment_balance_carol_insufficient_funds(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")
        with self.assertRaises(PaymentException):
            carol.pay_with_balance(bobby, 10.50, "Mirror")

    def test_payment_credit_card_missing(self):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, None)
        with self.assertRaises(PaymentException):
            carol.pay_with_card(bobby, 10.50, "Mirror")

    @mock.patch.object(target=User, attribute="_charge_credit_card")
    def test_payment_credit_card(self, charge_mock: mock.MagicMock):
        venmo = MiniVenmo()
        bobby = venmo.create_user("Bobby", 5.00, "4111111111111111")
        carol = venmo.create_user("Carol", 10.00, "4242424242424242")

        charge_mock.assert_not_called()
        payment = bobby.pay(carol, 5.50, "Chocolate")
        charge_mock.assert_called_once_with("4111111111111111", 5.50)
        self.assertEqual(payment.amount, 5.50)
        self.assertEqual(payment.actor, bobby)
        self.assertEqual(payment.target, carol)
        self.assertEqual(payment.note, "Chocolate")

        self.assertEqual(bobby.balance, 5.00)  # Credit (to be paid)
        self.assertEqual(carol.balance, 15.50)  # Already received


if __name__ == '__main__':
    unittest.main()
