from logging import getLogger
import operator
import click

class Plugin(object):
    """Class for holding information about a plugin"""
    def __init__(self, name, field, data_type, separators, info_key=None, 
                category=None, csq_key=None, record_rule=None, 
                string_rules={}):
        """
        The plugin class hold plugin information. The main task for a plugin
        is to return the correct value from a vcf field based on a number of
        rules. 
        field determines where in the vcf the value should be collected.
        data_type determines the type of the record that should be extracted
        separators define how the values are separated
        info_key and csq_key determines more specific where to look
        record_rule determines what value to return (If there are multiple values)
        string_rules determine how string matches should be prioritized.
        
        Arguments:
            name (str): The name of the plugin
            field (str): The field of the vcf that should be searched. Anyone of
                ['CHROM','POS','ID','REF','ALT', 'FILTER','QUAL',
                    'FILTER','INFO','FORMAT','sample_id']
            data_type (str): the data type of the record. Anyone of
                ['integer','float','flag','string']
            separators (list): A list of strings that describes how the record is
                                separated
            info_key (str): The name of the INFO field
            csq_key (str): The name of the Vep entry
            record_rule (str): Anyone of ['min', 'max']
            string_rules (dict): A dictionary with priority order of string matches
        
        """
        super(Plugin, self).__init__()
        self.logger = getLogger(__name__)
        self.logger = getLogger('extract_vcf.plugin')
        
        # These are the valid data types for a entry
        self.data_types = ['integer','float','flag','string']
        self.name = name
        self.logger.info("Initiating plugin with name: {0}".format(
            self.name
        ))
        self.field = field
        self.logger.info("Field: {0}".format(self.field))
        if data_type not in self.data_types:
            raise SyntaxError("data_type has to be in {0}".format(
                ','.join(self.data_types)
            ))
        self.data_type = data_type
        self.logger.info("Data type: {0}".format(self.data_type))
        self.separators = separators
        self.logger.info("Separators: {0}".format(self.separators))
        self.record_rule = record_rule
        self.logger.info("Record rule: {0}".format(self.record_rule))
        
        self.info_key = info_key
        self.logger.info("Info key: {0}".format(self.info_key))
        self.csq_key = csq_key
        self.logger.info("CSQ key: {0}".format(self.csq_key))
        self.category = category
        self.logger.info("Category: {0}".format(self.category))
        self.string_rules = string_rules
        self.logger.info("String rules: {0}".format(self.string_rules))
        

    
    def get_annotations(self, raw_annotation):
        """
        Return the annotations found in the field specified for plugin.
        
        get_annotation will split the string based on the separators and
        return a list with the annotations found.
        
        The annotations will be converted to the proper format based on 
        self.data_type for further process.
        
        Arguments:
            raw_annotation (str): A string with record information
        
        Returns:
            annotations (list): A list with the annotations found
        """
        annotations = []
        
        def get_values(string, splitters, i=1):
            """
            Split a string with arbitrary number of splitters.
            Add the elements of the string to global list result.
            
            Arguments:
                string : ex. "a:1|2,b:2"
                splitters (list): ex. [',',':','|']
            
            Returns:
                 Adds splitted string to results. ex. ['a','1','2','b','2']
            """
            if i == len(splitters):
                for value in string.split(splitters[i-1]):
                    annotations.append(value)
            else:
                for value in string.split(splitters[i-1]):
                    get_values(value, splitters, i+1)
                
        value = None
        
        # Raw annotation is the raw string from the vcf.
        if len(self.separators) > 0:
            get_values(raw_annotation, self.separators)
        
        else:
            annotations = [raw_annotation]
        
        typed_annotations = []
        
        for value in annotations:
            if self.data_type == 'integer':
                try:
                    typed_annotations.append(int(value))
                except ValueError:
                    pass
            elif self.data_type == 'float':
                try:
                    typed_annotations.append(float(value))
                except ValueError:
                    pass
            else:
                typed_annotations.append(value)
            
        
        return typed_annotations
    
    def get_raw_entry(self, variant):
        """
        Return a string that is the raw entry from the vcf
        
        Arguments:
            variant (dict): A variant dictionary
        
        Returns:
            raw_entry (str): A string that represents the raw entry
        """
        raw_annotation = None
        
        if self.field == 'INFO':
            if self.csq_key:
                
                vep_annotations = []
                vep_info = variant.get('vep_info', {})
                
                for allele in vep_info:
                    if self.csq_key in vep_info:
                        vep_annotations.append(vep_info[self.csq_key])
                raw_annotation = ','.join(vep_annotations)
                
            else:
                info_dict = variant.get('info_dict', {})
                
                if self.info_key in info_dict:
                    # If we are looking for a flag we search and see if we
                    # find the entry
                    if self.data_type == "flag":
                        raw_annotation = "True"
                    else:
                        raw_annotation = ','.join(info_dict[self.info_key])
        else:
            raw_annotation = variant.get(self.field, '.')

        if self.data_type == "flag":
            if raw_annotation == '.':
                raw_annotation = None
        return raw_annotation
        
    
    def get_value(self, variant):
        """
        Return the value as specified by plugin
        
        Get value will return one value or None if no correct value is found.
        
        Arguments:
            variant (dict): A vcf_parser style variant dictionary
        
        Returns:
            value (str): A string that represents the correct value
        
        """
        value = None
        raw_entry = self.get_raw_entry(variant)
        if self.data_type == 'flag':
            if raw_entry:
                value = "True"
            return value
        
        annotations = self.get_annotations(raw_entry)
        
        if self.record_rule:
            if self.data_type == 'string':
                string_dict = {}
                
                for entry in annotations:
                    if entry in self.string_rules:
                        string_dict[entry] = self.string_rules[entry]
                
                sorted_string_dict = sorted(
                    string_dict.items(), key=operator.itemgetter(1)
                )
                
                if len(sorted_string_dict) > 0:
                    return sorted_string_dict[0][0]
                else:
                    return ""
            
            if self.record_rule == 'max':
                return max(annotations)
            
            elif self.record_rule == 'min':
                return min(annotations)
        
        # If no record rule is given we return the raw annotation
        return raw_entry
    
    def __repr__(self):
        return "Plugin(name={0},field={1},data_type={2},separators={3},"\
                "record_rule={4},info_key={5},category={6},"\
                "string_rules={7})".format(self.name, self.field, 
                self.data_type, self.separators,self.record_rule, 
                self.info_key, self.category, self.string_rules)

@click.command()
def cli():
    from extract_vcf import logger
    from extract_vcf.log import init_log
    init_log(logger, loglevel="DEBUG")
    name = "Example"
    field = "INFO"
    data_type = "integer"
    separators = [',',':','|']
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators, info_key='TEST', record_rule='max')

    print(test_plugin)
    
    thousand_g = Plugin(name='1000G', field='INFO', data_type='float', 
                        separators=',', info_key='1000GAF', record_rule='max')
    print(thousand_g)

    db = Plugin(name='DB', field='INFO', data_type='flag', 
                        separators=None, info_key='DB')
    print(db)

    id_plugin = Plugin(name='id', field='ID', data_type='flag', 
                        separators=None, info_key=None)
    print(id_plugin)
    
    variant = {
        'CHROM': '1',
        'POS': '1',
        'ID': 'rs1',
        'REF': 'A',
        'ALT': 'C',
        'QUAL': '100',
        'FILTER': 'PASS',
        'INFO': 'MQ=1,2;TEST=a:12|11,b:9|27;1000GAF=0.718251;DB',
        'info_dict': {
            'MQ': ['1', '2'],
            'TEST': ['a:12|11', 'b:9|27'],
            '1000GAF': ['0.718251'],
            'DB': []
        }
    }
    
    print(test_plugin.get_value(variant))
    print(thousand_g.get_value(variant))
    print(db.get_value(variant))
    print(id_plugin.get_value(variant))
    

    
if __name__ == '__main__':
    cli()