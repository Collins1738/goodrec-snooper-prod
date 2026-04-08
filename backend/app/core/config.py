from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"  # "development" | "production"

    DATABASE_URL: str
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

    class Config:
        env_file = ".env"

    @property
    def is_dev(self) -> bool:
        return self.ENV == "development"

    @property
    def twilio_sid(self) -> str:
        return self.TWILIO_ACCOUNT_SID_TEST if self.is_dev else self.TWILIO_ACCOUNT_SID

    @property
    def twilio_token(self) -> str:
        return self.TWILIO_AUTH_TOKEN_TEST if self.is_dev else self.TWILIO_AUTH_TOKEN


settings = Settings()
