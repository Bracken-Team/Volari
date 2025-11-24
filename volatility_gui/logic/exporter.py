import json
import csv
import html
from typing import List, Dict, Any

class Exporter:
    """Helper class to export data to various formats."""

    @staticmethod
    def export_to_json(data: List[Dict[str, Any]], filename: str):
        """Export data to a JSON file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, default=str)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False

    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str):
        """Export data to a CSV file."""
        if not data:
            return False
            
        try:
            # Get all unique keys from all dictionaries to ensure all columns are present
            keys = set()
            for item in data:
                keys.update(item.keys())
            fieldnames = sorted(list(keys))
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    @staticmethod
    def export_to_html(data: List[Dict[str, Any]], filename: str):
        """Export data to an HTML file."""
        if not data:
            return False
            
        try:
            # Get all unique keys
            keys = set()
            for item in data:
                keys.update(item.keys())
            headers = sorted(list(keys))
            
            html_content = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "<style>",
                "table { border-collapse: collapse; width: 100%; font-family: Arial, sans-serif; }",
                "th, td { text-align: left; padding: 8px; border: 1px solid #ddd; }",
                "th { background-color: #f2f2f2; }",
                "tr:nth-child(even) { background-color: #f9f9f9; }",
                "</style>",
                "</head>",
                "<body>",
                "<h2>Exported Data</h2>",
                "<table>",
                "<thead>",
                "<tr>"
            ]
            
            # Add headers
            for header in headers:
                html_content.append(f"<th>{html.escape(header)}</th>")
            html_content.append("</tr></thead><tbody>")
            
            # Add rows
            for item in data:
                html_content.append("<tr>")
                for header in headers:
                    value = str(item.get(header, ""))
                    html_content.append(f"<td>{html.escape(value)}</td>")
                html_content.append("</tr>")
                
            html_content.append("</tbody></table></body></html>")
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("\n".join(html_content))
            return True
        except Exception as e:
            print(f"Error exporting to HTML: {e}")
            return False
