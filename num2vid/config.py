"""An interface for interacting with the num2vid config.json."""
import json

from .errors import ConfigPathError, ConfigReadError


class Config:
    """An interface for interacting with the num2vid config.json.

    :attr _path: path to the current instance's config json.
    :type _path: str
    :attr _config: python dictionary mirror of the json.
    :tpye _config: dict
    """
    def __init__(self, path: str):
        """Initialize with config path.

        :param path: path to the config json.
        """
        self._path = path
        self._config = self.load()

    def get(self, key: str, default: str = None) -> str:
        """Get value by key from current instance's config.

        :param key: key to retrieve.
        :param default: default value to return if key not found
        """
        return self._config.get(key, default)

    @property
    def path(self) -> str:
        """Retrieve path to current instance's config json."""
        return self._path

    def update(self, new_config_dict: dict) -> dict:
        """Update the instance dict.

        :param new_config_dict: dictionary of preferences to update.
        """
        self._config.update(new_config_dict)

        return self._config

    def clear(self):
        """Reset the prefs json to an empty dict and save."""
        self.save({})

    def save(self, config_dict:dict) -> dict:
        """Apply given config_dict to disk and update isntance dict.

        :param config_dict: the dict to write to disk.
        """
        try:
            with open(self._path, "w+") as config_fo:
                config_fo.write(json.dumps(config_dict))
        except (FileNotFoundError, PermissionError, json.decoder.JSONDecodeError) as err:
            if isinstance(err, json.decoder.JSONDecodeError):
                raise ConfigReadError(err)
            raise ConfigPathError(err)

        self._config = config_dict

        return self._config

    def load(self) -> dict:
        """Retrieve the contents of config.json and set to the current instance."""
        config_dict = {}
        try:
            with open(self._path, "r") as config_fo:
                config_dict = json.load(config_fo)
        except (FileNotFoundError, PermissionError, json.decoder.JSONDecodeError) as err:
            if isinstance(err, json.decoder.JSONDecodeError):
                raise ConfigReadError(err)
            raise ConfigPathError(err)

        self._config = config_dict

        return self._config
