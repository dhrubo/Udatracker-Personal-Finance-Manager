"""This module serves as the entry point for the program."""
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from balance.balance_observer import PrintObserver
from command.transaction_command import ApplyTransactionCommand
from command.transaction_manager import TransactionManager
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_adapter import TransactionAdapter
from transaction.external_income_transaction import ExternalFreelanceIncome

LOW_BALANCE_THRESHOLD = 100


def main():
    print("Adding transactions...")

    # Create balance (Singleton) and add observers (Observer)
    balance = Balance.get_instance()
    balance.register_observer(PrintObserver())
    balance.register_observer(
        LowBalanceAlertObserver(threshold=LOW_BALANCE_THRESHOLD)
    )

    # Create standard transactions
    transactions = [
        Transaction(100, TransactionCategory.INCOME),
        Transaction(50, TransactionCategory.EXPENSE),
        Transaction(200, TransactionCategory.INCOME),
        Transaction(75, TransactionCategory.EXPENSE),
    ]

    # Create an external income transaction (via Adapter pattern)
    freelance_income = ExternalFreelanceIncome(
        1200, "INV-98765", "Mobile App Project"
    )
    adapter = TransactionAdapter(freelance_income)
    adapted_transaction = adapter.to_transaction()
    print(
        f"Adapted freelance invoice {adapter.invoice_id} "
        f"({adapter.description})"
    )

    all_transactions = transactions + [adapted_transaction]

    # Apply each transaction as an undoable command (Command)
    manager = TransactionManager()
    for transaction in all_transactions:
        manager.execute(ApplyTransactionCommand(balance, transaction))

    print(balance.summary())

    # Demonstrate undo/redo of the last transaction
    print("\nUndoing last transaction...")
    undone = manager.undo()
    print(f"Undid: {undone}")
    print(balance.summary())

    print("\nRedoing it...")
    manager.redo()
    print(balance.summary())


if __name__ == "__main__":
    main()
