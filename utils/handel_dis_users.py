"""
This module contains the DisabledUsers class
which provides methods for managing disabled users
"""

import json
import os
import logging

from utils.logs import logger

DISABLED_USERS = set()

class DisabledUsers:
    """
    A class used to represent the Disabled Users.
    """

    def __init__(self, filename=".disable_users.json"):
        self.filename = filename
        self.disabled_users = self.load_disabled_users()

    def load_disabled_users(self):
        """
        Loads the disabled users from the JSON file.
        """
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    return set(data.get("disable_user", []))
            else:
                return set()
        except Exception as error:  # pylint: disable=broad-except
            logger.error(f"Error loading disabled users: {error}", exc_info=True)
            print("Check the error or delete the file :", error)
            print("Delete the .disable_users.json file? (y/n)")
            if input().lower() == "y":
                print("Deleting ...")
                logger.info("remove .disable_users.json file")
                try:
                    os.remove(".disable_users.json")
                except Exception as rm_error:
                    logger.error(f"Error deleting .disable_users.json: {rm_error}", exc_info=True)
            return set()

    async def save_disabled_users(self):
        """
        Saves the disabled users to the JSON file.
        """
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump({"disable_user": list(self.disabled_users)}, file)
        except Exception as error:
            logger.error(f"Error saving disabled users: {error}", exc_info=True)

    async def add_user(self, username: str):
        """
        Adds a user to the set of disabled users
        and saves the updated set to the JSON file.
        """
        DISABLED_USERS.add(username)
        self.disabled_users.add(username)
        await self.save_disabled_users()

    async def read_and_clear_users(self):
        """
        Returns a list of disabled users, clears the set of disabled users
        and saves the empty set to the JSON file.
        """
        disabled_users = list(self.disabled_users)
        self.disabled_users.clear()
        DISABLED_USERS.clear()
        await self.save_disabled_users()
        return set(disabled_users)
