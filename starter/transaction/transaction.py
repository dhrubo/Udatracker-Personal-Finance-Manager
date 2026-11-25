# transaction.py

from numbers import Real

from transaction.transaction_category import TransactionCategory


class Transaction:
    """Represents a financial transaction with an amount and category.

    The amount is always a non-negative number; the direction of the money
    (in or out) comes from the ``TransactionCategory`` enum.
    """

    def __init__(self, amount, category: TransactionCategory):
        if isinstance(amount, bool) or not isinstance(amount, Real):
            raise TypeError(
                f"Transaction amount must be a number, got {amount!r}"
            )
        if amount < 0:
            raise ValueError(
                "Transaction amount cannot be negative; "
                "use the EXPENSE category instead."
            )
        self.amount = amount
        self.category = category

    def __str__(self):
        return f"Transaction(${self.amount}, category='{self.category}')"

    def __repr__(self):
        return (
            f"Transaction(amount={self.amount!r}, "
            f"category={self.category!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.amount == other.amount and self.category == other.category

    def __hash__(self):
        return hash((self.amount, self.category))
