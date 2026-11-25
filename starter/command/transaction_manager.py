# transaction_manager.py


class TransactionManager:
    """Invoker for the Command pattern.

    Runs commands and keeps their undo/redo history. Callers hand it
    commands instead of mutating the Balance directly, so every change
    is recorded and can be rolled back or replayed.
    """

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def execute(self, command):
        """Run a command and record it.

        A command that raises (for example, a transaction with an invalid
        category) is not recorded. Executing a new command clears the redo
        history, as in any editor.
        """
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()
        return command

    def undo(self):
        """Undo the most recent command and return it.

        Raises:
            IndexError: If there is nothing to undo.
        """
        if not self._undo_stack:
            raise IndexError("Nothing to undo.")
        command = self._undo_stack.pop()
        command.undo()
        self._redo_stack.append(command)
        return command

    def redo(self):
        """Re-run the most recently undone command and return it.

        Raises:
            IndexError: If there is nothing to redo.
        """
        if not self._redo_stack:
            raise IndexError("Nothing to redo.")
        command = self._redo_stack.pop()
        command.execute()
        self._undo_stack.append(command)
        return command

    def can_undo(self):
        return bool(self._undo_stack)

    def can_redo(self):
        return bool(self._redo_stack)

    @property
    def history(self):
        """Commands currently applied, oldest first."""
        return tuple(self._undo_stack)
