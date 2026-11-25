import unittest
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestTransaction(unittest.TestCase):

    def test_transaction_creation(self):
        t = Transaction(100, TransactionCategory.EXPENSE)
        self.assertEqual(t.amount, 100)
        self.assertEqual(t.category, TransactionCategory.EXPENSE)

    def test_transaction_str(self):
        t = Transaction(50, TransactionCategory.INCOME)
        self.assertEqual(
            str(t),
            "Transaction($50, category='TransactionCategory.INCOME')",
        )

    def test_transaction_equality(self):
        t1 = Transaction(20, TransactionCategory.EXPENSE)
        t2 = Transaction(20, TransactionCategory.EXPENSE)
        t3 = Transaction(30, TransactionCategory.EXPENSE)
        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)

    def test_same_amount_different_category_not_equal(self):
        self.assertNotEqual(
            Transaction(20, TransactionCategory.INCOME),
            Transaction(20, TransactionCategory.EXPENSE),
        )

    def test_not_equal_to_other_types(self):
        t = Transaction(20, TransactionCategory.INCOME)
        self.assertNotEqual(t, 20)
        self.assertNotEqual(t, None)

    def test_equal_transactions_have_equal_hashes(self):
        t1 = Transaction(20, TransactionCategory.INCOME)
        t2 = Transaction(20, TransactionCategory.INCOME)
        self.assertEqual(len({t1, t2}), 1)

    def test_float_amount(self):
        t = Transaction(12.5, TransactionCategory.EXPENSE)
        self.assertEqual(
            str(t),
            "Transaction($12.5, category='TransactionCategory.EXPENSE')",
        )

    def test_zero_amount_allowed(self):
        self.assertEqual(Transaction(0, TransactionCategory.INCOME).amount, 0)

    def test_negative_amount_rejected(self):
        with self.assertRaises(ValueError):
            Transaction(-10, TransactionCategory.EXPENSE)

    def test_non_numeric_amount_rejected(self):
        for bad in ("100", None, True):
            with self.subTest(amount=bad):
                with self.assertRaises(TypeError):
                    Transaction(bad, TransactionCategory.INCOME)

    def test_category_enum_members(self):
        self.assertEqual(
            {member.name for member in TransactionCategory},
            {"INCOME", "EXPENSE"},
        )


if __name__ == "__main__":
    unittest.main()
