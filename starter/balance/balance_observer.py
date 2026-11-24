# balance_observer.py

from balance.currency import format_currency


class IBalanceObserver:
    """Observer interface: notified by ``Balance`` after every change."""

    def update(self, balance, transaction):
        """Handle balance updates.

        Args:
            balance (float): The net balance after the transaction was applied.
            transaction (Transaction): The transaction that changed the balance.
        """
        raise NotImplementedError("Subclasses must implement update method.")


class PrintObserver(IBalanceObserver):
    """Prints a line every time the balance changes."""

    def __init__(self):
        self.last_message = None

    def update(self, balance, transaction):
        """Print balance update message."""
        self.last_message = (
            f"[Balance Update] {transaction} -> New balance: {format_currency(balance)}"
        )
        print(self.last_message)


class LowBalanceAlertObserver(IBalanceObserver):
    """Raises an alert while the balance is below ``threshold``.

    ``alert_triggered`` reflects the latest update: True when the balance
    is strictly below the threshold, False once it recovers.
    """

    def __init__(self, threshold):
        self.threshold = threshold
        self.alert_triggered = False

    def update(self, balance, transaction):
        """Alert if balance drops below threshold."""
        self.alert_triggered = balance < self.threshold
        if self.alert_triggered:
            print(
                f"[ALERT] Low balance: {format_currency(balance)} is below "
                f"the {format_currency(self.threshold)} threshold."
            )
