"""
Tests for the Exporter module.
"""

import json
import csv
import pytest
from pathlib import Path
from volatility_gui.logic.exporter import Exporter


class TestExporter:
    """Tests for Exporter."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for export tests."""
        return [
            {"PID": "1234", "Name": "process1.exe", "PPID": "0"},
            {"PID": "5678", "Name": "process2.exe", "PPID": "1234"},
        ]
    
    def test_export_to_json(self, sample_data, tmp_path):
        """Test JSON export."""
        output_file = tmp_path / "export.json"
        success, message = Exporter.export_to_json(sample_data, str(output_file))
        
        assert success
        assert output_file.exists()
        
        with open(output_file) as f:
            loaded = json.load(f)
        assert loaded == sample_data
    
    def test_export_to_csv(self, sample_data, tmp_path):
        """Test CSV export."""
        output_file = tmp_path / "export.csv"
        success, message = Exporter.export_to_csv(sample_data, str(output_file))
        
        assert success
        assert output_file.exists()
        
        with open(output_file) as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 2
        assert rows[0]["PID"] == "1234"
    
    def test_export_empty_data(self, tmp_path):
        """Test export with empty data."""
        output_file = tmp_path / "empty.json"
        success, message = Exporter.export_to_json([], str(output_file))
        
        # Exporter may return False for empty data - that's acceptable
        assert success or "No data" in message
