from extract_vcf import ConfigParser
from tempfile import NamedTemporaryFile
from validate import ValidateError

import pytest

def setup_config_file(name = None, version = None, config_lines = []):
    """
    Create a config file and return its path
    
    Arguments:
        name (str): The name of this config
        version (str): The version of the config
        config_lines (iterator): An iterator with the lines of a config file.
    
    Returns:
        str : Path to config file
    """
    config_file = NamedTemporaryFile(delete=False)
    if config_lines:
        for line in config_lines:
            config_file.write(line)
    else:
        config_file.write("[Version]\n")
    if name:
        config_file.write("  name = {0}\n".format(name))
    if version:
        config_file.write("  version = {0}\n".format(version))
    
    config_file.close()
    
    return config_file.name
    

def test_version():
    """
    Test if a minimal config is read correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_file = setup_config_file(config_name, config_version)
    
    parser = ConfigParser(config_file)
    
    assert parser.version == float(config_version)
    assert parser.name == config_name

def test_empty_file():
    """
    Test if raise exception when no name
    """
    # Error should be raised since there is information in the config
    with pytest.raises(ValidateError):
        parser = ConfigParser(setup_config_file())

def test_no_version_section():
    """
    Test if a raise exception when no version section
    """
    config_name = 'example'
    config_version = '0.1'
    
    config_file = NamedTemporaryFile(delete=False)
    config_file.write("name = {0}\n".format(config_name))
    config_file.write("version = {0}\n".format(config_version))
    config_file.close()
    
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file.name)
    

def test_no_name():
    """
    Test if raise exception when no name
    """
    config_version = '0.1'
    # Error should be raised since there is no name of the config
    with pytest.raises(ValidateError):
        parser = ConfigParser(setup_config_file(version=config_version))

def test_no_version():
    """
    Test if raise exception when no version
    """
    config_name = 'example'
    # Error should be raised since there is no version of the config
    with pytest.raises(ValidateError):
        parser = ConfigParser(setup_config_file(name=config_name))

def test_wrong_version():
    """
    Test if raise exception when version is not a float
    """
    config_name = 'example'
    config_version = 'example'
    with pytest.raises(ValidateError):
        parser = ConfigParser(setup_config_file(name=config_name, version=config_version))

def test_simple_plugin():
    """
    Test if a simple plugin is parsed correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = flag\n"
    ]
    config_file = setup_config_file(config_lines=config_lines)
    parser = ConfigParser(config_file)
    assert list(parser.plugins.keys()) == ["Plugin"]

def test_no_separators():
    """
    Test if a raise error when no separators data type
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = integer\n"
    ]
    config_file = setup_config_file(config_lines=config_lines)
    
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)

def test_wrong_record_rule():
    """
    Test if a raise error when wrong record rule is used
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = integer\n"
        "  separators = ','\n"
        "  record_rule = medium\n"
    ]
    config_file = setup_config_file(config_lines=config_lines)
    
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)


def test_unknown_data_type():
    """
    Test if a raise error when unknown data type
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = test\n"
    ]
    config_file = setup_config_file(config_lines=config_lines)
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)

def test_category():
    """
    Test if the category feature works correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin1]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = flag\n"
        "  category = test\n"
        "[Plugin2]\n",
        "  field = INFO\n"
        "  info_key = MS\n"
        "  data_type = flag\n"
        "  category = test\n"
    ]
    config_file = setup_config_file(config_lines=config_lines)
    parser = ConfigParser(config_file)
    assert "test" in parser.categories
    

def test_filter_plugin():
    """
    Test if parses plugin correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = FILTER\n",
        "  data_type = string\n",
        "  separators = ';'\n",
        "  [[PASS]]\n",
        "    string = AD\n",
        "    priority = 2\n",
        "  [[FAIL]]\n",
        "    string = AD_dn\n",
        "    priority = 1\n",
        
    ]
    config_file = setup_config_file(config_lines=config_lines)
    parser = ConfigParser(config_file)
    
    assert list(parser.plugins.keys()) == ["Plugin"]

def test_plugin_no_field():
    """
    Test if parses plugin correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
    ]
    config_file = setup_config_file(config_lines=config_lines)
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)

def test_plugin_no_data_type():
    """
    Test if parses plugin correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = FILTER\n",
    ]
    config_file = setup_config_file(config_lines=config_lines)
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)
    
def test_plugin_wrong_field_name():
    """
    Test if parses plugin correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = WRONG_FIELD_NAME\n"
        "  data_type = float\n",
    ]
    config_file = setup_config_file(config_lines=config_lines)
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)

def test_info_plugin_no_info_field():
    """
    Test if parses plugin correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  data_type = string\n",
    ]
    config_file = setup_config_file(config_lines=config_lines)
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)

def test_csq_plugin():
    """
    Test if parses plugin correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = CSQ\n"
        "  csq_key = Feature_type\n"
        "  data_type = float\n",
        "  separators = ','\n"
    ]
    config_file = setup_config_file(config_lines=config_lines)
    parser = ConfigParser(config_file)

def test_csq_plugin_no_csq_field():
    """
    Test if parses plugin correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = CSQ\n"
        "  data_type = string\n",
    ]
    config_file = setup_config_file(config_lines=config_lines)
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)

def test_plugin_separators():
    """
    Test if parses plugin correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = integer\n",
        "  separators = ',',':'\n"
    ]
    config_file = setup_config_file(config_lines=config_lines)
    
    parser = ConfigParser(config_file)
    
    assert parser.plugins['Plugin'].separators == [',',':']

def test_plugin_string_dict():
    """
    Test if parses string plugin works correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = string\n",
        "  separators = ','\n",
        "  [[AD]]\n",
        "    string = AD\n",
        "    priority = 2\n",
        "  [[AD_dn]]\n",
        "    string = AD_dn\n",
        "    priority = 1\n",
    ]
    config_file = setup_config_file(config_lines=config_lines)
    
    parser = ConfigParser(config_file)
    
    assert parser.plugins['Plugin'].string_rules == {
        'AD': 2,
        'AD_dn': 1,
    }

def test_string_plugin_no_priority():
    """
    Test if raise exception when string rules have no priority
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = string\n",
        "  separators = ','\n",
        "  [[AD]]\n",
        "    string = AD\n",
        "  [[AD_dn]]\n",
        "    string = AD_dn\n",
        "    priority = 1\n",
    ]
    config_file = setup_config_file(config_lines=config_lines)
    
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)

def test_string_plugin_no_priority():
    """
    Test if raise exception when string rules have no priority
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = string\n",
        "  separators = ','\n",
        "  [[AD]]\n",
        "    string = AD\n",
        "  [[AD_dn]]\n",
        "    string = AD_dn\n",
        "    priority = 1\n",
    ]
    config_file = setup_config_file(config_lines=config_lines)
    
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)

def test_plugin_string_non_integer_priority():
    """
    Test if parses plugin correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = string\n",
        "  separators = ','\n",
        "  [[AD]]\n",
        "    string = AD\n",
        "    priority = 2.5\n",
        "  [[AD_dn]]\n",
        "    string = AD_dn\n",
        "    priority = 1\n",
    ]
    config_file = setup_config_file(config_lines=config_lines)
    
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)

def test_string_plugin_no_string_rule():
    """
    Test if parses plugin correct
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = string\n",
        "  separators = ','\n",
    ]
    
    config_file = setup_config_file(config_lines=config_lines)
    
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)

def test_string_plugin_no_string_defined():
    """
    Test if raise error when no string is specified in string rule
    """
    config_name = 'example'
    config_version = '0.1'
    config_lines = [
        "[Version]\n"
        "  name = {0}\n".format(config_name),
        "  version = {0}\n".format(config_version),
        "[Plugin]\n",
        "  field = INFO\n"
        "  info_key = MQ\n"
        "  data_type = string\n",
        "  separators = ','\n",
        "  [[AD]]\n",
        "    priority = 2.5\n",
    ]
    
    config_file = setup_config_file(config_lines=config_lines)
    
    with pytest.raises(ValidateError):
        parser = ConfigParser(config_file)
