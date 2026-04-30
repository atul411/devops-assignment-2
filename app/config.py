import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    DATABASE = os.environ.get("DATABASE", "/data/aceest_fitness.db")
    FEATURE_LEVEL = int(os.environ.get("FEATURE_LEVEL", "3"))
    APP_VERSION = os.environ.get("APP_VERSION", "3.0.0")
    TESTING = False


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    DATABASE = ":memory:"
    FEATURE_LEVEL = 3
