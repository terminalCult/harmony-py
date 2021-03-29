"""Provides a Config class for conveniently specifying the environment for Harmony Py.

The ``Config`` class can be instantiated without parameters and will default to
the Harmony testing (UAT) environment. To create a configuration for the
production environment, for example::

    cfg = Config(Environment.PROD)

This configuration object can then be passed as an argument when creating
the ``harmony.Client``.
"""
import os
from enum import Enum
from typing import cast

from dotenv import load_dotenv

Environment = Enum('Environment', ['SBX', 'SIT', 'UAT', 'PROD'])

HOSTNAMES = {
    Environment.SBX: 'harmony.sbx.earthdata.nasa.gov',
    Environment.SIT: 'harmony.sit.earthdata.nasa.gov',
    Environment.UAT: 'harmony.uat.earthdata.nasa.gov',
    Environment.PROD: 'harmony.earthdata.nasa.gov',
}


class Config:
    """Runtime configuation variables including defaults and environment vars.

    Example::

      >>> cfg = Config()
      >>> cfg.foo
      'bar'

    Parameters:
        None
    """

    config = {
        'NUM_REQUESTS_WORKERS': '3',  # increase for servers
        'DOWNLOAD_CHUNK_SIZE': str(4 * 1024 * 1024)  # recommend 16MB for servers
    }

    def __init__(self, environment: Environment = Environment.UAT) -> None:
        """Creates a new Config instance for the specified Environment."""
        load_dotenv()
        for k, v in Config.config.items():
            setattr(self, k, v)
        self.environment = environment

    @property
    def harmony_hostname(self):
        """Returns the hostname for this Config object's Environment."""
        return HOSTNAMES[self.environment]

    @property
    def edl_validation_url(self):
        """Returns the full URL to a Harmony endpoint used to validate the
        user's Earthdata Login credentials for this Config's Environment.
        """
        return f'https://{self.harmony_hostname}/jobs'

    def __getattribute__(self, name: str) -> str:
        """Overrides attribute retrieval for instances of this class.

        Attribute lookup follow this order:
            1. .env file variables
            2. OS environment variables
            3. object attributes that match ``name``

        This dunder method is not called directly.

        Args:
            name: An EDL username.

        Returns:
            The value of the referenced attribute
        """
        var = os.getenv(name.upper())
        if var is None:
            try:
                var = object.__getattribute__(self, name)
            except AttributeError:
                var = None
        return cast(str, var)
