import unittest
from balance.balance import Balance
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction_adapter import TransactionAdapter
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TestTransactionAdapter(unittest.TestCase):

    def test_adapter_converts_freelance_income(self):
        ext_txn = ExternalFreelanceIncome(
            500, "INV-12345", "Website development"
        )
        adapter = TransactionAdapter(ext_txn)
        txn = adapter.to_transaction()
        self.assertEqual(txn, Transaction(500, TransactionCategory.INCOME))

    def test_result_is_a_transaction(self):
        txn = TransactionAdapter(
            ExternalFreelanceIncome(75.25, "INV-1", "Logo design")
        ).to_transaction()
        self.assertIsInstance(txn, Transaction)
        self.assertEqual(txn.amount, 75.25)
        self.assertEqual(txn.category, TransactionCategory.INCOME)

    def test_exposes_external_details(self):
        adapter = TransactionAdapter(
            ExternalFreelanceIncome(1200, "INV-98765", "Mobile App Project")
        )
        self.assertEqual(adapter.invoice_id, "INV-98765")
        self.assertEqual(adapter.description, "Mobile App Project")

    def test_type_matching_is_case_insensitive(self):
        ext_txn = ExternalFreelanceIncome(10, "INV-2", "Consulting")
        ext_txn.typ = " INCOME "
        txn = TransactionAdapter(ext_txn).to_transaction()
        self.assertEqual(txn.category, TransactionCategory.INCOME)

    def test_unknown_type_rejected(self):
        ext_txn = ExternalFreelanceIncome(10, "INV-3", "Refund")
        ext_txn.typ = "chargeback"
        with self.assertRaises(ValueError):
            TransactionAdapter(ext_txn).to_transaction()

    def test_does_not_modify_external_object(self):
        ext_txn = ExternalFreelanceIncome(500, "INV-4", "Website development")
        TransactionAdapter(ext_txn).to_transaction()
        self.assertEqual(
            (
                ext_txn.amount,
                ext_txn.invoice_id,
                ext_txn.description,
                ext_txn.typ,
            ),
            (500, "INV-4", "Website development", "income"),
        )

    def test_adapted_transaction_updates_balance(self):
        balance = Balance.get_instance()
        balance.reset()
        balance.clear_observers()
        txn = TransactionAdapter(
            ExternalFreelanceIncome(1200, "INV-5", "Mobile App Project")
        ).to_transaction()
        balance.apply_transaction(txn)
        self.assertEqual(balance.get_balance(), 1200)
        balance.reset()


if __name__ == "__main__":
    unittest.main()
