"""
Pytest configuration and fixtures for Volari tests.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication for the test session.
    
    This fixture ensures a single QApplication instance exists
    for all tests that need Qt widgets.
    """
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def mock_volatility_wrapper():
    """Mock the VolatilityWrapper for testing without real memory dumps."""
    with patch("volatility_gui.logic.volatility_wrapper.VolatilityWrapper") as mock:
        instance = MagicMock()
        mock.return_value = instance
        yield instance


@pytest.fixture
def temp_settings_file(tmp_path):
    """Create a temporary settings file for testing."""
    settings_file = tmp_path / "settings.json"
    return str(settings_file)
