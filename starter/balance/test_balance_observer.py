import io
import unittest
from contextlib import redirect_stdout
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from balance.balance import Balance
from balance.balance_observer import IBalanceObserver
from balance.balance_observer import LowBalanceAlertObserver
from balance.balance_observer import PrintObserver


class TestLowBalanceAlertObserver(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()
        # Keep alert output out of the test report; tests read it back.
        self.output = io.StringIO()
        self._redirect = redirect_stdout(self.output)
        self._redirect.__enter__()

    def tearDown(self):
        self._redirect.__exit__(None, None, None)
        self.balance.clear_observers()

    def test_alert_triggers_on_low_balance(self):
        observer = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(observer)

        self.balance.apply_transaction(
            Transaction(100, TransactionCategory.INCOME)
        )
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE)
        )
        self.assertTrue(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(100, TransactionCategory.INCOME)
        )
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE)
        )
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(
            Transaction(60, TransactionCategory.EXPENSE)
        )
        self.assertTrue(observer.alert_triggered)

    def test_alert_not_triggered_before_any_update(self):
        observer = LowBalanceAlertObserver(threshold=50)
        self.assertFalse(observer.alert_triggered)

    def test_balance_equal_to_threshold_does_not_alert(self):
        observer = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(observer)
        self.balance.add_income(50)
        self.assertFalse(observer.alert_triggered)
        self.assertEqual(self.output.getvalue(), "")

    def test_alert_prints_message(self):
        observer = LowBalanceAlertObserver(threshold=100)
        self.balance.register_observer(observer)
        self.balance.add_income(30)
        self.assertIn(
            "[ALERT] Low balance: $30.00 is below the $100.00 threshold.",
            self.output.getvalue(),
        )

    def test_negative_balance_triggers_alert(self):
        observer = LowBalanceAlertObserver(threshold=0)
        self.balance.register_observer(observer)
        self.balance.add_expense(10)
        self.assertTrue(observer.alert_triggered)
        self.assertIn("-$10.00", self.output.getvalue())

    def test_update_can_be_called_directly(self):
        observer = LowBalanceAlertObserver(threshold=50)
        observer.update(10, Transaction(10, TransactionCategory.INCOME))
        self.assertTrue(observer.alert_triggered)


class TestPrintObserver(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()
        self.balance.clear_observers()
        self.observer = PrintObserver()
        self.balance.register_observer(self.observer)

    def tearDown(self):
        self.balance.clear_observers()

    def test_prints_on_every_balance_change(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.balance.add_income(100)
            self.balance.add_expense(30)
        lines = output.getvalue().splitlines()
        self.assertEqual(
            lines,
            [
                "[Balance Update] "
                "Transaction($100, category='TransactionCategory.INCOME')"
                " -> New balance: $100.00",
                "[Balance Update] "
                "Transaction($30, category='TransactionCategory.EXPENSE')"
                " -> New balance: $70.00",
            ],
        )

    def test_last_message_matches_printed_output(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.balance.add_income(5)
        self.assertEqual(output.getvalue().strip(), self.observer.last_message)

    def test_print_and_alert_observers_both_notified(self):
        alert = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(alert)
        output = io.StringIO()
        with redirect_stdout(output):
            self.balance.add_income(20)
        self.assertIn("[Balance Update]", output.getvalue())
        self.assertIn("[ALERT]", output.getvalue())
        self.assertTrue(alert.alert_triggered)


class TestObserverInterface(unittest.TestCase):

    def test_base_update_must_be_overridden(self):
        with self.assertRaises(NotImplementedError):
            IBalanceObserver().update(0, None)


if __name__ == "__main__":
    unittest.main()
