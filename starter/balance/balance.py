# balance.py

import threading

from balance.currency import format_currency
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class Balance:
    """Singleton to track the balance.

    Balance is also the *subject* in the Observer pattern: every change to
    the balance is broadcast to the registered observers.

    Always obtain the instance through ``Balance.get_instance()``.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize the balance. Prevent direct instantiation."""
        if Balance._instance is not None:
            raise RuntimeError(
                "Balance is a singleton; use Balance.get_instance() instead."
            )
        self._balance = 0.0
        self._observers = []
        Balance._instance = self

    @classmethod
    def get_instance(cls):
        """Return the single shared Balance, creating it on first use.

        Double-checked locking keeps creation safe if two threads ask for
        the instance at the same time.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls()
        return cls._instance

    # ------------------------------------------------------------------ #
    # Observer management
    # ------------------------------------------------------------------ #
    def register_observer(self, observer):
        """Subscribe an observer to balance changes (ignored if already registered)."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer):
        """Unsubscribe an observer. Does nothing if it was not registered."""
        if observer in self._observers:
            self._observers.remove(observer)

    def clear_observers(self):
        """Remove every registered observer."""
        self._observers.clear()

    def notify_observers(self, transaction):
        """Tell every observer the new balance and the transaction that caused it."""
        for observer in list(self._observers):
            observer.update(self._balance, transaction)

    # ------------------------------------------------------------------ #
    # Balance operations
    # ------------------------------------------------------------------ #
    def reset(self):
        """Reset the net balance to zero.

        Registered observers are kept; use ``clear_observers`` to drop them.
        """
        self._balance = 0.0

    def add_income(self, amount):
        """Add income to the balance."""
        self.apply_transaction(Transaction(amount, TransactionCategory.INCOME))

    def add_expense(self, amount):
        """Subtract expense from the balance."""
        self.apply_transaction(Transaction(amount, TransactionCategory.EXPENSE))

    def apply_transaction(self, transaction):
        """
        Apply a Transaction object to update the balance.

        Args:
            transaction (Transaction): The transaction to apply.

        Raises:
            ValueError: If the transaction's category is not INCOME or EXPENSE.
        """
        if transaction.category == TransactionCategory.INCOME:
            self._balance += transaction.amount
        elif transaction.category == TransactionCategory.EXPENSE:
            self._balance -= transaction.amount
        else:
            raise ValueError(
                f"Unsupported transaction category: {transaction.category!r}"
            )
        self.notify_observers(transaction)

    def get_balance(self):
        """Get the current net balance."""
        return self._balance

    def summary(self):
        """Return a summary string of the net balance."""
        return f"Net balance: {format_currency(self._balance)}"
