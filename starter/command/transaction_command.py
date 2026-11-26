# transaction_command.py

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class ICommand:
    """Command interface: an action that can be executed and undone."""

    def execute(self):
        raise NotImplementedError("Subclasses must implement execute method.")

    def undo(self):
        raise NotImplementedError("Subclasses must implement undo method.")


class ApplyTransactionCommand(ICommand):
    """Command that applies a Transaction to a Balance and can undo it.

    Undo applies the opposite transaction (an INCOME is reversed by
    an EXPENSE of the same amount, and vice versa). Because the
    reversal goes through ``Balance.apply_transaction``, observers are
    notified of it like any other change.
    """

    _OPPOSITE = {
        TransactionCategory.INCOME: TransactionCategory.EXPENSE,
        TransactionCategory.EXPENSE: TransactionCategory.INCOME,
    }

    def __init__(self, balance, transaction):
        self.balance = balance
        self.transaction = transaction
        self._executed = False

    def execute(self):
        """Apply the transaction to the balance."""
        self.balance.apply_transaction(self.transaction)
        self._executed = True

    def undo(self):
        """Reverse the transaction.

        Raises:
            RuntimeError: If the command has not been executed yet.
        """
        if not self._executed:
            raise RuntimeError(
                "Cannot undo a command that has not been executed."
            )
        reversal = Transaction(
            self.transaction.amount, self._OPPOSITE[self.transaction.category]
        )
        self.balance.apply_transaction(reversal)
        self._executed = False

    def __str__(self):
        return f"Apply {self.transaction}"
