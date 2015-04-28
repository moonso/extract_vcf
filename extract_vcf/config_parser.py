#!/usr/bin/env python
# encoding: utf-8
"""
read_config.py

The main point with this package is how to retreive the corect entry from 
a vcf file.
In the best case one should be able to specify any kind of entry in the
config file and how it is extracted.
ConfigParser will read these files and check if they are on the proper
format. It would be perfect to use the validator package but unfortunately
it is not as flexible as we need it to be.

ConfigParser will create plugins for each entry in the config file with the
relevant information for the score model.

A config file has to include a Version section with name and version like:

[Version]
  name = config_name # This is a string
  version = config_version # This is a float

Each plugin section will look like:

[Plugin_name]
  section = section_name # str in ['CHROM','POS','ID','REF','ALT', 'FILTER',
                          'QUAL', 'FILTER','INFO','FORMAT','sample_id']
  data_type = data_type # str in ['integer','float','flag','character','string']


Created by Måns Magnusson on 2015-04-16.
Copyright (c) 2015 __MoonsoInc__. All rights reserved.
"""

from __future__ import print_function, unicode_literals

import logging
import click

from six import string_types
from configobj import ConfigObj
from validate import ValidateError

from extract_vcf import Plugin

class ConfigParser(ConfigObj):
    """
    Class for holding information from config file.
    
    """
    def __init__(self, config_file, indent_type='  ', encoding='utf-8'):
        super(ConfigParser, self).__init__(
                                        infile=config_file, 
                                        indent_type=indent_type, 
                                        encoding=encoding,
                                        )
        logger = logging.getLogger(__name__)
        self.vcf_columns = ['CHROM','POS','ID','REF','ALT', 'FILTER','QUAL',
                            'FILTER','INFO','FORMAT','sample_id']
        self.data_types = ['integer','float','flag','character','string']
        # self.data_numbers = ['A','G','.','R']
        
        logger.info("Checking version and name")
        self.version_check()
        self.version = float(self['Version']['version'])
        self.name = self['Version']['name']
        
        self.plugins = {plugin:None for plugin in self.keys() if plugin != 'Version'}
        
        self.categories = {}
        
        logger.info("Checking plugins")
        
        for plugin in self.keys():
            if plugin != 'Version':
                logger.debug("Checking plugin: {0}".format(plugin))
                self.check_plugin(plugin)
                logger.debug("Plugin {0} is ok".format(plugin))
                plugin_info = self[plugin]
                logger.debug("Adding plugin {0} to ConfigParser".format(plugin))
                self.plugins[plugin] = Plugin(
                    name=plugin, 
                    field=plugin_info['field'], 
                    data_type=plugin_info['data_type'], 
                    separators=plugin_info.get('separators',[]), 
                    info_field=plugin_info.get('info_key',None),
                    category=plugin_info.get('info_key',None),
                    csq_field=plugin_info.get('csq_field', None)
                )
                category = plugin_info.get('category', None)
                if category:
                    if category in self.categories:
                        self.categories[category].append(plugin)
                    else:
                        self.categories[category] = [plugin]
                
    #
    #     logger.info("Checking plugin scores")
    #     for plugin in self.plugins:
    #         logger.debug("Checking plugin score: {0}".format(plugin))
    #         self[plugin] = self.vcf_score_check(self[plugin], plugin)
    #
    def version_check(self):
        """
        Check if the version entry is in the proper format
        """
        try:
            version_info = self['Version']
        except KeyError:
            raise ValidateError('Config file has to have a Version section')
        try:
            float(version_info['version'])
        except KeyError:
            raise ValidateError('Config file has to have a version section')
        except ValueError:
            raise ValidateError('Version has to be a float.')
        
        try:
            version_info['name']
        except KeyError:
            raise ValidateError("Config file has to have a name")
        return
   
    def check_plugin(self, plugin):
        """
        Check if the section is in the proper format vcf format.

        Args:
            vcf_section (dict): The information from a vcf section

        Returns:
            True is it is in the proper format

        """
        
        vcf_section = self[plugin]
        
        try:
            vcf_field = vcf_section['field']
            if not  vcf_field in self.vcf_columns:
                raise ValidateError(
                        "field has to be in {0}\n"
                        "Wrong field name in plugin: {1}".format(
                        self.vcf_columns, plugin
                    ))
            if vcf_field == 'INFO':
                try:
                    info_key = vcf_section['info_key']

                    if info_key == 'CSQ':
                        try:
                            csq_key = vcf_section['csq_key']
                        except KeyError:
                            raise ValidateError(
                        "CSQ entrys has to refer to an csq field.\n"
                        "Refer with keyword 'csq_key'\n"
                        "csq_key is missing in section: {0}".format(
                            plugin
                            )
                        )


                except KeyError:
                    raise ValidateError(
                        "INFO entrys has to refer to an INFO field.\n"
                        "Refer with keyword 'info_key'\n"
                        "info_key is missing in section: {0}".format(
                            plugin
                            )
                        )
        except KeyError:
            raise ValidateError(
                "Vcf entrys have to refer to a field in the VCF with keyword"
                " 'field'.\nMissing keyword 'field' in plugin: {0}".format(
                  plugin
                ))

        try:
            if not vcf_section['data_type'] in self.data_types:
                raise ValidateError(
                    "data_type has to be in {0}\n"
                    "Wrong data_type in plugin: {1}".format(
                        self.data_types, plugin)
                    )
        except KeyError:
            raise ValidateError(
                "Vcf entrys have to refer to a data type in the VCF with "
                "keyword 'data_type'.\n"
                "Missing data_type in plugin: {0}".format(plugin)
                )
        
        separators = vcf_section.get('separators', None)
        if separators:
            if len(separators) == 1:
                vcf_section = self[plugin]['separators'] = list(separators)

    #     try:
    #         if not vcf_section['data_number'] in data_numbers:
    #             raise ValidateError(
    #                 "data_number has to be in %s\n"
    #                 "Wrong data number in section: %s" %
    #                 (data_numbers, section_name)
    #                 )
    #     except KeyError:
    #         raise ValidateError(
    #             "Vcf entrys have to refer to a data number in the"
    #             " VCF with keyword 'data_number'.\n Missing data_number in "
    #             "section: %s" % section_name
    #             )
    #
        return True
    #
    # def vcf_score_check(self, vcf_section, section_name):
    #     """
    #     Check if the section is in the proper vcf score format.
    #
    #     Args:
    #         vcf_section (dict): The information from a vcf section
    #
    #     Returns:
    #         True is it is in the proper format
    #
    #     """
    #     # Default will be set to 'max'
    #     category_aggregations = ['sum','min','max']
    #     record_aggregations = ['min','max']
    #
    #     try:
    #         category = vcf_section['category']
    #         if not isinstance(category, string_types):
    #             raise ValidateError(
    #                     "category has to be a string.\n"
    #                     "Please update category to section %s"
    #                     % section_name
    #                     )
    #     except KeyError:
    #         raise ValidateError(
    #                 "Score entrys have to belong to a category.\n"
    #                 "Refer with keyword 'category'\n"
    #                 "Please add category to section %s"
    #                 % section_name
    #                 )
    #     try:
    #         if not vcf_section['category_aggregation'] in category_aggregations:
    #             raise ValidateError(
    #                 "category_aggregations has to be in %s.\n"
    #                 "Please update category_aggregation in section %s\n"
    #                 % (category_aggregations,section_name)
    #                 )
    #     except KeyError:
    #         vcf_section['category_aggregation'] = 'max'
    #
    #     try:
    #         if not vcf_section['record_aggregation'] in record_aggregations:
    #             raise ValidateError(
    #                 "record_aggregation has to be in %s.\n"
    #                 "Please update record_aggregation in section %s\n"
    #                 % (record_aggregations, section_name)
    #                 )
    #     except KeyError:
    #         raise ValidateError(
    #             "Score entrys has to have a record aggregation rule.\n"
    #             "Refer with keyword 'record_aggregation'\n"
    #             'Please update record aggregation in section %s\n'
    #             % section_name
    #             )
    #
    #     try:
    #         vcf_section['not_reported']
    #     except KeyError:
    #         raise ValidateError(
    #             "Score entrys has to have a not_reported score.\n"
    #             "Refer with sub section [[not_reported]]' in %s"
    #             % section_name
    #             )
    #
    #     operators = ['eq', 'le', 'lt', 'gt', 'ge', 'na']
    #     # Check if the score defenitions are in the proper format
    #     for sub_section in vcf_section:
    #         if isinstance(vcf_section[sub_section], dict):
    #
    #             try:
    #                 score = vcf_section[sub_section]['score']
    #             except KeyError:
    #                 raise ValidateError(
    #                     "Score entrys has to have a score.\n"
    #                     "Missing score in section %s, function %s"
    #                     % (section_name, sub_section)
    #                     )
    #             try:
    #                 operator = vcf_section[sub_section]['operator']
    #
    #                 if not operator in operators:
    #                     raise ValidateError(
    #                         "Score entrys has to have a operator in %s\n"
    #                         "Please update in section %s, score function: %s"""
    #                             % (operators, section_name, sub_section))
    #
    #                 if vcf_section['data_type'] == 'string':
    #                     if not operator == 'eq' and sub_section != 'not_reported':
    #                         raise ValidateError(
    #                         "If data type is string, operator has to be 'eq'.\n"
    #                         "Please update in section: %s, score function: %s"""
    #                         % (section_name, sub_section)
    #                         )
    #
    #
    #
    #             except KeyError:
    #                 # If datatype is string, set operator to 'eq'
    #                 if vcf_section['data_type'] == 'string':
    #                     vcf_section[sub_section]['operator'] = 'eq'
    #                 else:
    #                     raise ValidateError(
    #                     "Score entrys has to have a operator.\n"
    #                     "Missing operator in section: %s, score function: %s"
    #                     % (section_name, sub_section)
    #                     )
    #             try:
    #                 value = vcf_section[sub_section]['value']
    #             except KeyError:
    #                 raise ValidateError(
    #                     "Score entrys has to have a value.\n"
    #                     "Missing value in section: %s, function: %s"
    #                     % (section_name, sub_section)
    #                     )
    #
    #     return vcf_section
    #
    #
    # def write_config(self, outfile):
    #     """Write the config file to a new file"""
    #     self._cfg.write(outfile)

@click.command()
@click.argument('config_file',
                nargs=1,
                type=click.Path(exists=True)
)
@click.option('-out', '--outfile',
                nargs=1,
                type=click.File('w')
)
@click.option('-l', '--loglevel',
                type=click.Choice(['DEBUG', 'INFO', 'WARNING']),
                default = 'INFO'
)
def read_config(config_file, outfile, loglevel):
    """Parse the config file and print it to the output."""
    
    from extract_vcf import logger, init_log
    init_log(logger, loglevel=loglevel)
    
        
    logger.info("Reading Config File: {0}".format(config_file))
    
    config_reader = ConfigParser(config_file)
    
    for plugin in config_reader.plugins:
        logger.info("Found plugin:{0}".format(plugin))
        logger.info("{0}: {1}".format(
            plugin,config_reader.plugins[plugin])
            )
    
    for category in config_reader.categories:
        logger.info("Category {0}: {1}".format(
            category, config_reader.categories[category]
        ))

    
if __name__ == '__main__':
    read_config()
