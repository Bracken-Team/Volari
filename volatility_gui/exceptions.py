"""
Custom exceptions for Volari.

Provides a hierarchy of exceptions for better error handling
and more informative error messages.
"""


class VolariError(Exception):
    """Base exception for all Volari errors."""

    def __init__(self, message: str, details: str = "") -> None:
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class PluginError(VolariError):
    """Error during plugin execution."""

    def __init__(self, plugin_name: str, message: str, details: str = "") -> None:
        self.plugin_name = plugin_name
        super().__init__(f"Plugin '{plugin_name}' error: {message}", details)


class ConfigError(VolariError):
    """Configuration error."""
    pass


class ExportError(VolariError):
    """Error during data export."""
    pass


class FileLoadError(VolariError):
    """Error loading memory dump file."""
    pass


class APIError(VolariError):
    """Error communicating with external API."""

    def __init__(self, api_name: str, message: str, status_code: int = 0) -> None:
        self.api_name = api_name
        self.status_code = status_code
        details = f"Status: {status_code}" if status_code else ""
        super().__init__(f"{api_name} API error: {message}", details)
