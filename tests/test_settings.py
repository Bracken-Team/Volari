"""
Tests for the SettingsManager module.
"""

import json
import pytest
from volatility_gui.logic.settings_manager import SettingsManager


class TestSettingsManager:
    """Tests for SettingsManager."""
    
    def test_get_default_value(self, temp_settings_file):
        """Test that default values are returned for missing keys."""
        manager = SettingsManager(temp_settings_file)
        result = manager.get("nonexistent.key", "default_value")
        assert result == "default_value"
    
    def test_set_and_get(self, temp_settings_file):
        """Test setting and getting a value."""
        manager = SettingsManager(temp_settings_file)
        manager.set("test.key", "test_value")
        result = manager.get("test.key")
        assert result == "test_value"
    
    def test_nested_keys(self, temp_settings_file):
        """Test setting and getting nested keys."""
        manager = SettingsManager(temp_settings_file)
        manager.set("parent.child.grandchild", 42)
        result = manager.get("parent.child.grandchild")
        assert result == 42
    
    def test_persistence(self, temp_settings_file):
        """Test that settings persist across instances."""
        manager1 = SettingsManager(temp_settings_file)
        manager1.set("persistent.key", "saved_value")
        
        # Create new instance to test loading
        manager2 = SettingsManager(temp_settings_file)
        result = manager2.get("persistent.key")
        assert result == "saved_value"
