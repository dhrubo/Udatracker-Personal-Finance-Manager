# transaction_adapter.py

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory


class TransactionAdapter:
    """Adapter: lets external freelance income be used as a ``Transaction``.

    The external platform describes money with its own shape
    (``amount``, ``invoice_id``, ``description`` and a free-text ``typ``).
    The rest of the app only understands ``Transaction`` objects, so this
    adapter translates one into the other without changing either class.
    """

    _TYPE_TO_CATEGORY = {
        "income": TransactionCategory.INCOME,
        "expense": TransactionCategory.EXPENSE,
    }

    def __init__(self, external_transaction):
        self.external_transaction = external_transaction

    @property
    def invoice_id(self):
        """Invoice ID from the external platform, kept for traceability."""
        return self.external_transaction.invoice_id

    @property
    def description(self):
        """Project details from the external platform."""
        return self.external_transaction.description

    def to_transaction(self):
        """Convert an external transaction to a standard Transaction.

        Raises:
            ValueError: If the external type string is not one we can map.
        """
        ext = self.external_transaction
        # Freelance income is always income, so fall back to that
        # when the external object has no ``typ``.
        external_type = str(getattr(ext, "typ", "income")).strip().lower()
        try:
            category = self._TYPE_TO_CATEGORY[external_type]
        except KeyError:
            raise ValueError(
                f"Cannot adapt external transaction type {ext.typ!r}"
            ) from None
        return Transaction(ext.amount, category)
