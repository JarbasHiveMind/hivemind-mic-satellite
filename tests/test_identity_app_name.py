"""The identity is this application's own (HIVEMIND-CRYPTO-1 §2).

Before this change the entry point called ``NodeIdentity()`` and shared
``~/.config/hivemind/_identity.json`` with every other HiveMind application of
the user, so a satellite, a bridge and the CLI on one account presented one
identifier and one static key. The application now names itself.
"""
from unittest.mock import MagicMock, patch

import pytest

APP_NAME = "mic-satellite"


def _empty_identity():
    identity = MagicMock()
    identity.password = ""
    identity.access_key = ""
    identity.site_id = ""
    identity.default_master = ""
    identity.default_port = 0
    return identity


def test_the_satellite_asks_for_its_own_identity():
    import hivemind_mic_sat as entry
    from click.testing import CliRunner
    with patch.object(entry, "NodeIdentity", return_value=_empty_identity()) as ctor:
        result = CliRunner().invoke(entry.run, ["--host", "hub"])
    ctor.assert_called_once_with(app_name=APP_NAME)
    assert isinstance(result.exception, RuntimeError)  # no key: stops after the identity
