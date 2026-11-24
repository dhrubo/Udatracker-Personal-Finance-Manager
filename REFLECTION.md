# Reflection — Design Patterns in the Personal Finance Manager

This app uses four design patterns. **Singleton**, **Adapter** and **Observer** were required. I chose **Command** as the fourth.

| Pattern   | Where it lives | What it does in the app |
|-----------|----------------|-------------------------|
| Singleton | `balance/balance.py` (`Balance`) | Makes sure there is only one balance for the whole app |
| Adapter   | `transaction/transaction_adapter.py` (`TransactionAdapter`) | Turns freelance-platform income into a normal `Transaction` |
| Observer  | `balance/balance_observer.py` (`PrintObserver`, `LowBalanceAlertObserver`); `Balance` is the subject | Reacts to every balance change: prints it, and alerts when funds get low |
| Command   | `command/transaction_command.py`, `command/transaction_manager.py` | Wraps each transaction as an action that can be undone and redone |

---

## 1. Singleton — `Balance`

**How it works.** `Balance.get_instance()` creates the balance the first time it is called and returns that same object every time after. Calling `Balance()` directly when an instance already exists raises `RuntimeError`. Creation is wrapped in a lock with a double check, so two threads asking at the same moment still get one object.

**How it improved the design.** Every part of the app (the observers, the commands, `main.py`) works with the same running total. There is no chance of two balances drifting apart.

**Trade-off.** A singleton is global state. It carries over between unit tests, so a test that leaves observers registered changes the results of the next one. I added `reset()` and `clear_observers()` and call them in every test's `setUp`/`tearDown`. To keep the global from spreading, the commands *receive* the balance as a constructor argument. Only `main.py` calls `get_instance()`. A test could hand a command a fake balance without touching the real singleton.

## 2. Adapter — `TransactionAdapter`

**How it works.** `ExternalFreelanceIncome` has its own shape: `amount`, `invoice_id`, `description`, and a text field `typ = "income"`. `TransactionAdapter.to_transaction()` maps that text to the `TransactionCategory` enum (ignoring case and spaces) and returns a standard `Transaction`. An unknown type raises `ValueError` instead of slipping through quietly. The adapter also exposes `invoice_id` and `description` so callers can still trace where the money came from.

**How it improved the design.** `Balance`, the observers and the commands only know about `Transaction`. They didn't change at all to support freelance income. Another income source (Stripe, PayPal, a bank CSV) would just need its own small adapter.

**Trade-off.** `Transaction` has no place to store an invoice ID, so the adapted transaction loses those details once it reaches the balance. I could have added an optional metadata field to `Transaction`. But the provided test requires the adapted transaction to equal a plain `Transaction(500, INCOME)`, which means equality would have to ignore the metadata. Two transactions that "look different but are equal" is confusing, so I kept `Transaction` simple and left the details on the adapter.

## 3. Observer — `PrintObserver` and `LowBalanceAlertObserver`

**How it works.** `Balance` keeps a list of observers (`register_observer`, `unregister_observer`). After every successful change it calls `update(new_balance, transaction)` on each one, and `add_income`/`add_expense` go through the same path. `PrintObserver` logs each change. `LowBalanceAlertObserver` sets `alert_triggered` to `True` while the balance is strictly below its threshold, prints an alert, and resets the flag once the balance recovers. A rejected transaction (invalid category) changes nothing and notifies no one.

**How it improved the design.** `Balance` has no idea what happens when money moves. It only announces it. New reactions (email or push notifications, a budget tracker, writing to a file) can be added by registering another observer, without editing `Balance`. Each observer can also be unit-tested by calling `update()` directly.

**Trade-offs.**
- Observers run synchronously, in the order they were registered. If one raises an exception, the ones after it are skipped, and the balance has already changed. In a real app I would catch errors per observer, or dispatch events asynchronously.
- The low-balance alert fires on *every* transaction that leaves the balance below the threshold, not just the first time it drops. The provided test expects `alert_triggered` to track the current state, and repeating the warning while you are still low felt more useful than staying silent.

## 4. Command (my choice) — `ApplyTransactionCommand` and `TransactionManager`

### Why I chose it
Fixing a mistake is a real need in a finance app: you enter $500 instead of $50, or record an expense twice. The Command pattern solves that directly. I also picked it over Strategy or Factory because it fits around the existing classes without changing them. A command just calls `Balance.apply_transaction`, so it automatically works with the Singleton and the observers.

### Where it fits
- `ApplyTransactionCommand(balance, transaction)` has `execute()` and `undo()`. Undo applies the opposite transaction (income is reversed by an expense of the same amount), so the balance comes back exactly to where it was.
- `TransactionManager` is the *invoker*. It runs commands and keeps an undo stack and a redo stack. A new command clears the redo stack, as in any editor. A command that fails (for example, an invalid category) is never recorded.
- `main.py` sends every transaction through the manager, then shows an undo and a redo of the freelance payment.

### How it improves flexibility, testability and scalability
- **Flexibility:** new operations, such as a transfer between two accounts or a recurring payment, become new `ICommand` classes. The manager handles their undo/redo with no changes. Several commands could be grouped into one "macro" command that undoes as a unit.
- **Testability:** each command can be tested on its own (execute, then undo, then check the balance). The manager can be tested for stack behaviour (order, clearing redo, empty-stack errors) without caring what the commands do.
- **Scalability:** the manager's history is effectively an audit log. Saving it to disk would allow replaying the history to rebuild the balance, or a full change history per user.

### Trade-offs
- Undo is a *compensating* transaction, not an erase. Observers see the reversal like any other change, so the print log shows "$1200 EXPENSE" when the freelance income is undone, and an undo can trigger a low-balance alert. That keeps the log accurate, but it can look odd at first.
- The history lives only in memory and is lost when the program exits.
- It adds two classes and an extra step for what used to be a single method call. For a tiny script that would be over-engineering; it pays off once undo, auditing or more operation types matter.

---

## Other implementation notes
- `Transaction` rejects negative or non-numeric amounts. Direction is expressed only through the `INCOME`/`EXPENSE` enum, so `-50 EXPENSE` can never mean "add 50". It also defines `__hash__` alongside `__eq__` so equal transactions behave correctly in sets and dicts.
- I added `__init__.py` files to `balance/`, `transaction/` and `command/`. Without them, `python -m unittest discover` doesn't look inside those folders and finds 0 tests.
- Amounts are stored as Python floats to match the starter code and tests. A production version should use `decimal.Decimal` to avoid rounding errors with cents.
- Test count: 64 tests (13 provided + 51 new), all passing. The provided tests are unchanged apart from added `setUp`/`tearDown` cleanup and captured console output.
