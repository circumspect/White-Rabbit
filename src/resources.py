from pathlib import Path
from typing import Sequence


class ImageResource:
    IMAGE_EXTENSIONS = ["png", "jpg", "jpeg"]

    def __init__(self, extensions: Sequence[str]) -> None:
        self.extensions = extensions

    def get(self, directory: Path, name: str) -> Path:
        """
        Attempts to find the image file in the given directory by trying each
        of the acceptable extensions

        Raises FileNotFoundError if none of them match
        """

        for extension in self.extensions:
            filepath = directory / f"{name}.{extension}"
            if filepath.exists():
                return filepath

        raise FileNotFoundError(directory / name)
