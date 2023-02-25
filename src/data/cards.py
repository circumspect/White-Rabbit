from rabbit import WHITE_RABBIT_DIR
import envvars
import yaml

CARD_LIST_DIR = WHITE_RABBIT_DIR / "card_lists"

with open(CARD_LIST_DIR / f"{envvars.get_env_var('WHITE_RABBIT_CARD_LIST')}.yaml", "r") as f:
    data = yaml.safe_load(f)

CHARACTERS = data["characters"]
ROLES_TO_CHARACTERS = {
    v["role"]: character for character, v in CHARACTERS.items()
}
SUSPECTS = data["suspects"]
LOCATIONS = data["locations"]
SEARCHING = data["searching"]
