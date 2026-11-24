import threading
import unittest
from balance.balance import Balance
from balance.balance_observer import IBalanceObserver
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class RecordingObserver(IBalanceObserver):
    """Test double that records every notification it receives."""

    def __init__(self):
        self.calls = []

    def update(self, balance, transaction):
        self.calls.append((balance, transaction))


class TestBalance(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()

    def tearDown(self):
        self.balance.clear_observers()

    def test_initial_balance(self):
        self.assertEqual(self.balance.get_balance(), 0.0)

    def test_singleton_instance(self):
        balance1 = Balance.get_instance()
        balance2 = Balance.get_instance()
        self.assertIs(balance1, balance2)

    def test_add_income(self):
        self.balance.add_income(100)
        self.assertEqual(self.balance.get_balance(), 100)

    def test_add_expense(self):
        self.balance.add_expense(40)
        self.assertEqual(self.balance.get_balance(), -40)

    def test_apply_transaction_income(self):
        t = Transaction(150, TransactionCategory.INCOME)
        self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), 150)

    def test_apply_transaction_expense(self):
        t = Transaction(60, TransactionCategory.EXPENSE)
        self.balance.apply_transaction(t)
        self.assertEqual(self.balance.get_balance(), -60)

    def test_apply_transaction_invalid_category(self):
        class FakeCategory:
            pass
        t = Transaction(100, FakeCategory())
        with self.assertRaises(ValueError):
            self.balance.apply_transaction(t)

    def test_reset(self):
        self.balance.add_income(100)
        self.balance.add_expense(50)
        self.balance.reset()
        self.assertEqual(self.balance.get_balance(), 0.0)

    # --- Singleton --------------------------------------------------------

    def test_direct_instantiation_is_blocked(self):
        with self.assertRaises(RuntimeError):
            Balance()

    def test_get_instance_returns_same_object_across_threads(self):
        instances = []
        threads = [
            threading.Thread(target=lambda: instances.append(Balance.get_instance()))
            for _ in range(10)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertTrue(all(instance is self.balance for instance in instances))

    def test_state_is_shared_between_references(self):
        Balance.get_instance().add_income(30)
        self.assertEqual(Balance.get_instance().get_balance(), 30)

    # --- Balance operations ----------------------------------------------

    def test_multiple_transactions_accumulate(self):
        self.balance.add_income(100)
        self.balance.add_expense(25.5)
        self.balance.add_income(10)
        self.assertAlmostEqual(self.balance.get_balance(), 84.5)

    def test_invalid_category_leaves_balance_unchanged(self):
        class FakeCategory:
            pass
        self.balance.add_income(70)
        with self.assertRaises(ValueError):
            self.balance.apply_transaction(Transaction(100, FakeCategory()))
        self.assertEqual(self.balance.get_balance(), 70)

    def test_summary_positive(self):
        self.balance.add_income(1375)
        self.assertEqual(self.balance.summary(), "Net balance: $1,375.00")

    def test_summary_negative(self):
        self.balance.add_expense(40)
        self.assertEqual(self.balance.summary(), "Net balance: -$40.00")

    # --- Subject side of the Observer pattern ----------------------------

    def test_apply_transaction_notifies_observers(self):
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        t = Transaction(80, TransactionCategory.INCOME)
        self.balance.apply_transaction(t)
        self.assertEqual(observer.calls, [(80, t)])

    def test_add_income_and_expense_notify_observers(self):
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        self.balance.add_income(50)
        self.balance.add_expense(20)
        self.assertEqual(
            observer.calls,
            [
                (50, Transaction(50, TransactionCategory.INCOME)),
                (30, Transaction(20, TransactionCategory.EXPENSE)),
            ],
        )

    def test_register_observer_ignores_duplicates(self):
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        self.balance.register_observer(observer)
        self.balance.add_income(10)
        self.assertEqual(len(observer.calls), 1)

    def test_unregister_observer_stops_notifications(self):
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        self.balance.unregister_observer(observer)
        self.balance.add_income(10)
        self.assertEqual(observer.calls, [])

    def test_unregister_unknown_observer_is_harmless(self):
        self.balance.unregister_observer(RecordingObserver())

    def test_invalid_transaction_does_not_notify(self):
        class FakeCategory:
            pass
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        with self.assertRaises(ValueError):
            self.balance.apply_transaction(Transaction(100, FakeCategory()))
        self.assertEqual(observer.calls, [])

    def test_reset_does_not_notify(self):
        observer = RecordingObserver()
        self.balance.register_observer(observer)
        self.balance.reset()
        self.assertEqual(observer.calls, [])


if __name__ == "__main__":
    unittest.main()
