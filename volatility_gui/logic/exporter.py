import json
import csv
import html
from typing import List, Dict, Any, Tuple

class Exporter:
    """Helper class to export data to various formats."""

    @staticmethod
    def export_to_json(data: List[Dict[str, Any]], filename: str) -> Tuple[bool, str]:
        """Export data to a JSON file.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not data:
            return False, "No data to export"

        if not filename:
            return False, "No filename specified"

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, default=str)
            return True, f"Successfully exported {len(data)} items to {filename}"
        except PermissionError:
            return False, f"Permission denied: Cannot write to {filename}"
        except OSError as e:
            return False, f"OS error writing to {filename}: {e}"
        except Exception as e:
            return False, f"Error exporting to JSON: {e}"

    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str) -> Tuple[bool, str]:
        """Export data to a CSV file.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not data:
            return False, "No data to export"

        if not filename:
            return False, "No filename specified"

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
            return True, f"Successfully exported {len(data)} rows to {filename}"
        except PermissionError:
            return False, f"Permission denied: Cannot write to {filename}"
        except OSError as e:
            return False, f"OS error writing to {filename}: {e}"
        except Exception as e:
            return False, f"Error exporting to CSV: {e}"

    @staticmethod
    def export_to_html(data: List[Dict[str, Any]], filename: str, title: str = "Exported Data") -> Tuple[bool, str]:
        """Export data to an HTML file.

        Args:
            data: List of dictionaries to export
            filename: Output file path
            title: Title for the HTML page

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not data:
            return False, "No data to export"

        if not filename:
            return False, "No filename specified"

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
                "<meta charset='utf-8'>",
                f"<title>{html.escape(title)}</title>",
                "<style>",
                "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 20px; background: #1a1b26; color: #c0caf5; }",
                "table { border-collapse: collapse; width: 100%; margin-top: 20px; }",
                "th, td { text-align: left; padding: 12px 8px; border-bottom: 1px solid #414868; }",
                "th { background-color: #24283b; color: #7aa2f7; font-weight: 600; }",
                "tr:hover { background-color: #292e42; }",
                "h2 { color: #7aa2f7; margin-bottom: 5px; }",
                ".meta { color: #565f89; font-size: 12px; }",
                "</style>",
                "</head>",
                "<body>",
                f"<h2>{html.escape(title)}</h2>",
                f"<p class='meta'>Exported {len(data)} items</p>",
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
            return True, f"Successfully exported {len(data)} items to {filename}"
        except PermissionError:
            return False, f"Permission denied: Cannot write to {filename}"
        except OSError as e:
            return False, f"OS error writing to {filename}: {e}"
        except Exception as e:
            return False, f"Error exporting to HTML: {e}"

