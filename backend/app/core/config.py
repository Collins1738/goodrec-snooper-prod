from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"  # "development" | "staging" | "production"

    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_db_url(cls, v: str) -> str:
        # Railway injects postgres:// — SQLAlchemy+asyncpg needs postgresql+asyncpg://
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_ACCOUNT_SID_TEST: str = ""
    TWILIO_AUTH_TOKEN_TEST: str = ""
    TWILIO_VERIFY_SERVICE_SID: str
    TWILIO_FROM_NUMBER: str

    GOODREC_ACCESS_TOKEN: str
    GOODREC_REFRESH_TOKEN: str
    FIREBASE_API_KEY: str  # Goodrec Firebase project key (pickupsoccer-6a62a) — set in Railway env vars

    SLACK_WEBHOOK_URL: str = ""  # Optional — used for staging notifications

    class Config:
        env_file = ".env"

    @property
    def is_dev(self) -> bool:
        return self.ENV == "development"

    @property
    def is_staging(self) -> bool:
        return self.ENV == "staging"

    @property
    def is_test_env(self) -> bool:
        """True for both dev and staging — use test Twilio creds and OTP bypass."""
        return self.ENV in ("development", "staging")

    @property
    def twilio_sid(self) -> str:
        return self.TWILIO_ACCOUNT_SID_TEST if self.is_test_env else self.TWILIO_ACCOUNT_SID

    @property
    def twilio_token(self) -> str:
        return self.TWILIO_AUTH_TOKEN_TEST if self.is_test_env else self.TWILIO_AUTH_TOKEN


settings = Settings()
