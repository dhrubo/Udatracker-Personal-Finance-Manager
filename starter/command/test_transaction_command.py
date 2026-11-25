import io
import unittest
from contextlib import redirect_stdout
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from command.transaction_command import ApplyTransactionCommand, ICommand
from command.transaction_manager import TransactionManager
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


def income(amount):
    return Transaction(amount, TransactionCategory.INCOME)


def expense(amount):
    return Transaction(amount, TransactionCategory.EXPENSE)


class TestApplyTransactionCommand(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()

    def tearDown(self):
        self.balance.clear_observers()

    def test_execute_applies_transaction(self):
        ApplyTransactionCommand(self.balance, income(100)).execute()
        self.assertEqual(self.balance.get_balance(), 100)

    def test_undo_reverses_income(self):
        command = ApplyTransactionCommand(self.balance, income(100))
        command.execute()
        command.undo()
        self.assertEqual(self.balance.get_balance(), 0)

    def test_undo_reverses_expense(self):
        self.balance.add_income(100)
        command = ApplyTransactionCommand(self.balance, expense(40))
        command.execute()
        command.undo()
        self.assertEqual(self.balance.get_balance(), 100)

    def test_undo_before_execute_raises(self):
        command = ApplyTransactionCommand(self.balance, income(100))
        with self.assertRaises(RuntimeError):
            command.undo()

    def test_cannot_undo_twice(self):
        command = ApplyTransactionCommand(self.balance, income(100))
        command.execute()
        command.undo()
        with self.assertRaises(RuntimeError):
            command.undo()

    def test_undo_notifies_observers(self):
        alert = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(alert)
        with redirect_stdout(io.StringIO()):
            self.balance.add_income(30)
            command = ApplyTransactionCommand(self.balance, income(100))
            command.execute()
            self.assertFalse(alert.alert_triggered)
            command.undo()
        self.assertTrue(alert.alert_triggered)

    def test_base_command_methods_must_be_overridden(self):
        with self.assertRaises(NotImplementedError):
            ICommand().execute()
        with self.assertRaises(NotImplementedError):
            ICommand().undo()


class TestTransactionManager(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()
        self.manager = TransactionManager()

    def tearDown(self):
        self.balance.clear_observers()

    def run_txn(self, transaction):
        return self.manager.execute(
            ApplyTransactionCommand(self.balance, transaction)
        )

    def test_execute_records_history(self):
        first = self.run_txn(income(100))
        second = self.run_txn(expense(30))
        self.assertEqual(self.manager.history, (first, second))
        self.assertEqual(self.balance.get_balance(), 70)

    def test_undo_most_recent_first(self):
        self.run_txn(income(100))
        last = self.run_txn(expense(30))
        self.assertIs(self.manager.undo(), last)
        self.assertEqual(self.balance.get_balance(), 100)
        self.manager.undo()
        self.assertEqual(self.balance.get_balance(), 0)
        self.assertFalse(self.manager.can_undo())

    def test_redo_reapplies(self):
        self.run_txn(income(100))
        self.manager.undo()
        self.assertTrue(self.manager.can_redo())
        self.manager.redo()
        self.assertEqual(self.balance.get_balance(), 100)
        self.assertFalse(self.manager.can_redo())

    def test_new_command_clears_redo(self):
        self.run_txn(income(100))
        self.manager.undo()
        self.run_txn(income(5))
        self.assertFalse(self.manager.can_redo())
        with self.assertRaises(IndexError):
            self.manager.redo()

    def test_undo_with_empty_history_raises(self):
        with self.assertRaises(IndexError):
            self.manager.undo()

    def test_redo_with_nothing_undone_raises(self):
        with self.assertRaises(IndexError):
            self.manager.redo()

    def test_failed_command_not_recorded(self):
        class FakeCategory:
            pass
        with self.assertRaises(ValueError):
            self.run_txn(Transaction(100, FakeCategory()))
        self.assertEqual(self.manager.history, ())
        self.assertEqual(self.balance.get_balance(), 0)


if __name__ == "__main__":
    unittest.main()
