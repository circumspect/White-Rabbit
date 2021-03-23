from pathlib import Path
from typing import Sequence


class ImageResource:
    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg"]

    def __init__(self, extensions: Sequence[str]) -> None:
        self.extensions = extensions

    def get(self, directory: Path, name: str) -> Path:
        for extension in self.extensions:
            filepath = directory / f"{name}.{extension}"
            if filepath.exists():
                return filepath

        raise FileNotFoundError(directory / name)


class LocalizedResource:
    def __init__(self, lang: str) -> None:
        self.lang = lang

    def get_directory(self, directory: Path) -> Path:
        localized_dir = directory / self.lang

        if localized_dir.exists():
            return localized_dir

        return directory

    def get_image(self, directory: Path, name: str) -> Path:
        img = ImageResource(ImageResource.ALLOWED_EXTENSIONS)
        try:
            return img.get(self.get_directory(directory), name)
        except FileNotFoundError:
            # Fallback if image does not exists but localized directory exists
            return img.get(directory, name)

    def get_file(self, directory: Path, filename: str) -> Path:
        filepath = self.get_directory(directory) / filename

        if filepath.exists():
            return filepath

        return directory / filename
