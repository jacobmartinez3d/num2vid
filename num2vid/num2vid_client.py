"""Core functions for Num2VidClient."""
from requests import Session, Request
from requests.exceptions import ConnectionError

from .num2vid import Config
from .errors import ConnectionError as Num2VidConnectionError

class Num2VidClient:
    """Core API for Num2Vid Client functionality.

    :attr _session: Session object which handles our http traffic.
    :attr config: Config instance for current client process.
    """
    def __init__(self, config_path: str):
        """Initialize with path to config json."""
        self._session = Session()
        self.config = Config(config_path)

    def submit_num(self, num: int, download_path: str = None) -> str:
        """Submit num to Num2Vid server via http GET request for resulting vid.

        :param num: the integer between 1 and 10 to send to server.
        :param download_path: if supplied a file will be created at the given location, and its
            path returned as a str.
        """
        flask_server_url = "http://{host}:{port}".format(
            host=self.config.get("flask_host"),
            port=self.config.get("flask_port"))

        # construct GET request url
        url = "/".join([flask_server_url, "convert", str(num)])
        req = Request("GET", url)
        prepped = self._session.prepare_request(req)
        # send request
        try:
            res = self._session.send(prepped)
        except ConnectionError as err:
            raise Num2VidConnectionError(
                "Could not connect to num2vid server. Make sure it is running, see README.md " \
                "for instructions on how to start the num2vid server.")

        if download_path:
            # download the file to given path and return the filepath as a str
            with open(download_path, "wb") as vid_fo:
                vid_fo.write(res.content)
            return download_path
        # if no download path supplied, a `requests.models.Response` object is returned
        return res

    @property
    def session(self):
        """Return current Session isntance."""
        return self._session
