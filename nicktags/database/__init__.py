import json

import disnake

from nicktags.constants import Config

__all__ = ("DB",)


class DB:
    def __init__(self):
        self.cache = {}
        self.path = "./nicktags/database/data.json"

    def load_data(self) -> dict[str, str]:
        if self.cache == {}:
            with open(self.path) as f:
                self.cache = json.load(f)

        return self.cache

    def _dump_data(self, data: dict[str, str]) -> None:
        self.cache = data

        with open(self.path, "w") as f:
            json.dump(data, f, indent=4)

    def add_update_tag(self, role_id: int, tag: str) -> bool:
        """Adds a tag for a role, or updates an existing tag
        Returns `True` if updating existing tag, or `False` if adding a new tag"""

        role_id = str(role_id)
        data = self.load_data()

        if role_id in data.keys():
            tag_update = True
        else:
            tag_update = False

        data[role_id] = tag
        self._dump_data(data)
        return tag_update

    def delete_tag(self, tag: str) -> None:
        data = self.load_data()

        for k, v in data:
            if tag == v:
                data[k] = None

        self._dump_data(data)

    def get_tag_by_role(self, role: disnake.Role) -> str | None:
        data = self.load_data()
        role_id = str(role.id)

        if role_id in data.keys():
            return data[role_id]

    def get_tag_named(self, tag: str) -> tuple[str, str] | None:
        data = self.load_data()
        for k, v in data.items():
            if v == tag:
                return k, v

        return None, None
