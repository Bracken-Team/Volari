"""
Base classes and utilities for tabs.
Provides shared functionality for non-editable tables with copy-on-double-click.
"""
from PyQt6.QtWidgets import QTableWidget, QApplication, QAbstractItemView


class NonEditableTableMixin:
    """
    Mixin to make a QTableWidget non-editable and enable copy-on-double-click.

    Usage:
        Call setup_non_editable_table(self.table) in init_ui() after creating the table.
    """

    @staticmethod
    def setup_non_editable_table(table: QTableWidget):
        """
        Configure a table to be non-editable with copy-on-double-click.

        Args:
            table: The QTableWidget to configure
        """
        # Disable editing
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Connect double-click to copy
        table.cellDoubleClicked.connect(lambda row, col: NonEditableTableMixin._copy_cell(table, row, col))

    @staticmethod
    def _copy_cell(table: QTableWidget, row: int, col: int):
        """Copy cell contents to clipboard on double-click."""
        item = table.item(row, col)
        if item:
            text = item.text()
            clipboard = QApplication.clipboard()
            clipboard.setText(text)

            # Show feedback in status bar if available
            main_window = table.window()
            if hasattr(main_window, 'statusBar'):
                status_bar = main_window.statusBar()
                if status_bar:
                    # Truncate long text for display
                    display_text = text[:50] + "..." if len(text) > 50 else text
                    status_bar.showMessage(f"Copied: {display_text}", 2000)


def setup_table_copy_on_double_click(table: QTableWidget):
    """
    Convenience function to set up a table with non-editable behavior and copy-on-double-click.

    Args:
        table: The QTableWidget to configure
    """
    NonEditableTableMixin.setup_non_editable_table(table)
