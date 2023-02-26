from typing import Dict, List, Optional, Union


class Character:
    def __init__(self, name: str, data: Optional[Dict[str, Union[str, List[str]]]]):
        self.name: str
        self.role: str
        self.full_name: str
        self.pdf_name_format: List[str]

        self.name = name

        if data is None:
            data = {}

        if "role" in data and data["role"] is not None:
            self.role = data["role"]
        else:
            self.role = self.name.capitalize()

        if "full-name" in data and data["full-name"] is not None:
            self.full_name = data["full-name"]
        else:
            self.full_name = self.name.capitalize()

        if "pdf-name-format" in data and data["pdf-name-format"] is not None:
            self.pdf_name_format = data["pdf-name-format"]
        else:
            self.pdf_name_format = self.full_name.split()

class Suspect:
    def __init__(self, name: str, description: Optional[str]):
        self.name = name
        self.description = description

class Location:
    def __init__(self, name: str, description: Optional[str]):
        self.name = name
        self.description = description

class Searching:
    def __init__(self, name: str, description: Optional[str]):
        self.name = name
        self.description = description

