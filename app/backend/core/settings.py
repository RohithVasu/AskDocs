from dynaconf import Dynaconf
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

settings = Dynaconf(
    envvar_prefix="ASKDOCS",
    settings_files=[BASE_DIR / "config/settings.dev.yaml"],
    environments=True,
    load_dotenv=True,
    env_switcher="ENV_FOR_DYNACONF",
    env="development"
)