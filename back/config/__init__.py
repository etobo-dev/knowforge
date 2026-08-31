from config.settings import DailyQuotaLimits, Settings, load_settings

_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


__all__ = ["DailyQuotaLimits", "Settings", "get_settings", "load_settings"]
