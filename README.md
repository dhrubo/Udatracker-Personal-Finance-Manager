# Personal Finance Manager — Design Patterns Project

This project is a hands-on exercise in applying Object-Oriented Design Patterns to build a simplified personal finance manager.
You will implement and extend starter code to add functionality such as tracking transactions, adapting external data, observing balance changes, and ensuring proper architectural patterns.

## Getting Started

### Dependencies

Make sure you have python version >= 3.10.x installed on your computer. 


### Installation

1. Clone the repo:

```bash
git clone https://github.com/udacity/cd14600-project-starter.git
cd cd14600-project-starter/starter
```

2. Run the Program: 
```
python main.py
```

## Testing

This project uses Python’s built-in unittest framework.

To run all tests:

```
python -m unittest discover
```

To run a single test file:
```
python -m unittest balance/test_balance_observer.py
```

### Break Down Tests

- test_balance.py → Verifies correct implementation of the Singleton Balance class.
- test_transaction.py → Confirms transactions update balances correctly.
- test_transaction_adapter.py → Ensures external income data is correctly adapted into Transaction objects.
- test_balance_observer.py → Validates that low-balance alerts are triggered at the correct threshold.
- test_transaction_command.py → Checks that commands apply, undo and redo transactions, and that the manager's history behaves correctly.

## Design Patterns Implemented

| Pattern | Location |
|---------|----------|
| Singleton | `starter/balance/balance.py`: `Balance.get_instance()` |
| Adapter | `starter/transaction/transaction_adapter.py`: `TransactionAdapter` |
| Observer | `starter/balance/balance_observer.py`: `PrintObserver`, `LowBalanceAlertObserver` |
| Command (chosen pattern) | `starter/command/`: `ApplyTransactionCommand`, `TransactionManager` (undo/redo) |

See [REFLECTION.md](REFLECTION.md) for why each pattern was used, how it improved the design, and the trade-offs.

### Sample output

```
Adding transactions...
Adapted freelance invoice INV-98765 (Mobile App Project)
[Balance Update] Transaction($100, category='TransactionCategory.INCOME') -> New balance: $100.00
[Balance Update] Transaction($50, category='TransactionCategory.EXPENSE') -> New balance: $50.00
[ALERT] Low balance: $50.00 is below the $100.00 threshold.
[Balance Update] Transaction($200, category='TransactionCategory.INCOME') -> New balance: $250.00
[Balance Update] Transaction($75, category='TransactionCategory.EXPENSE') -> New balance: $175.00
[Balance Update] Transaction($1200, category='TransactionCategory.INCOME') -> New balance: $1,375.00
Net balance: $1,375.00

Undoing last transaction...
[Balance Update] Transaction($1200, category='TransactionCategory.EXPENSE') -> New balance: $175.00
Undid: Apply Transaction($1200, category='TransactionCategory.INCOME')
Net balance: $175.00

Redoing it...
[Balance Update] Transaction($1200, category='TransactionCategory.INCOME') -> New balance: $1,375.00
Net balance: $1,375.00
```

## Project Instructions

1. Implement Singleton Balance Class – Ensure only one balance object exists throughout the app.
2. Complete Transaction Class – Handle income and expense transactions.
3. Implement Adapter Pattern – Adapt external freelance income data into internal Transaction objects.
4. Implement Observer Pattern – Create a low balance observer that triggers an alert when funds drop too low.
5. Add Unit Tests – Write tests for all implemented functionality.
6. Choose and Implement a Fourth Pattern – Pick one additional design pattern (e.g., Strategy, Command, Decorator, etc.) and integrate it into your project.
7. Provide a Reflection – Add a short write-up in your repo (README or separate file) explaining your design choices.

## Built With

* [Python](https://www.python.org/) – Main programming language
* [unittest](https://docs.python.org/3/library/unittest.html) – Testing framework
* [PEP8](https://peps.python.org/pep-0008/) – Style guide for Python code

## License

[License](LICENSE.txt)
