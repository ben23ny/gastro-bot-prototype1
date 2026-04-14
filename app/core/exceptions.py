class AppError(Exception):
    """Basisfehler für die App."""


class JobNotFoundError(AppError):
    """Wird geworfen, wenn ein Job nicht gefunden wird."""


class ConfigurationError(AppError):
    """Wird geworfen, wenn Konfiguration fehlt."""


class GenerationError(AppError):
    """Wird geworfen, wenn die Content-Erzeugung fehlschlägt."""