"""pytest framework for PolarisConfig module
"""

import json

import pytest

from polaris.common.config import PolarisConfig


def test_polaris_config_creation_non_existent_file(tmp_path):
    """Smoke test for object creation, non-existent file
    """
    with pytest.raises(FileNotFoundError):
        fullpath = tmp_path / 'does_not_exist.json'
        _ = PolarisConfig(file=fullpath)


def test_polaris_config_creation_simple_file(tmp_path):
    """Smoke test for object creation, simple config
    """

    simple_config = {'foo': 'bar', 'baz': 'bum', 'bling': 123}
    fullpath = tmp_path / 'simple_config.json'
    with open(fullpath.as_posix(), 'w') as f_handle:
        json.dump(simple_config, f_handle)

    config_from_file = PolarisConfig(file=fullpath)
    for key in simple_config:
        assert config_from_file[key] == simple_config[key]


def test_polaris_config_creation_simple_file_plus_defaults(tmp_path):
    """Smoke test for overrriding settings
    """
    defaults = {'default_to_override': 1, 'default_to_leave_alone': 2}

    new_config = {'default_to_override': 'OVERRIDDEN', 'other_setting': 'foo'}
    fullpath = tmp_path / 'simple_config.json'
    with open(fullpath.as_posix(), 'w') as f_handle:
        json.dump(new_config, f_handle)

    config_from_file = PolarisConfig(file=fullpath, defaults=defaults)

    assert config_from_file['default_to_override'] == new_config[
        'default_to_override']
    assert config_from_file['default_to_leave_alone'] == defaults[
        'default_to_leave_alone']
    assert config_from_file['other_setting'] == new_config['other_setting']
