from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IDRS_", env_file=".env", extra="ignore")

    start_node: int = 20
    goal_node: int = 17
    baseline_speed: float = 100.0
    constraint_fraction: float = 0.60
    constraint_speed: float = 40.0
    constraint_seed: int = 42
    replan_fraction: float = 0.20
    fragility_levels: list[int] = [2, 5, 8]
    network_data_path: Path = Path(__file__).resolve().parent.parent / "data" / "network.json"


@lru_cache
def get_settings() -> Settings:
    return Settings()
