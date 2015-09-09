from logging import getLogger
import operator
import click

from extract_vcf import get_annotation

class Plugin(object):
    """Class for holding information about a plugin"""
    def __init__(self, name, field, data_type, separators=[], info_key=None, 
                category=None, csq_key=None, record_rule=None, 
                string_rules={}):
        """
        The plugin class hold plugin information. The main task for a plugin
        is to return the correct value from a vcf field based on a number of
        rules. 
        "field" determines where in the vcf the value should be collected.
        "data_type" determines the type of the record that should be extracted
        "separators" define how the values are separated
        "info_key" and csq_key determines more specific where to look
        "record_rule" determines what value to return (If there are multiple values)
        "string_rules" determin how string matches should be prioritized.
        
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
        # For testing only
        self.logger = getLogger('extract_vcf.plugin')
        
        # These are the valid data types for a entry
        self.data_types = ['integer','float','flag','string']
        self.name = name
        self.logger.info("Initiating plugin with name: {0}".format(
            self.name
        ))
        self.field = field
        self.logger.info("Field: {0}".format(self.field))
        
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
        # Get the correct annotation for the record
        annotations = get_annotation(
                        variant = variant,
                        field = self.field,
                        data_type = self.data_type,
                        separators = self.separators,
                        info_key=self.info_key,
                        csq_key=self.csq_key
                        )
        # Flags do not need a record type
        if self.data_type == 'flag':
            if annotations:
                value = True
            else:
                value = False
        
        # If we have a record rule we need to return the correct value
        elif self.record_rule and annotations:
            
            if self.data_type == 'string':
                string_dict = {}
                
                for entry in annotations:
                    if entry in self.string_rules:
                        string_dict[entry] = self.string_rules[entry]
                
                sorted_string_dict = sorted(
                    string_dict.items(), key=operator.itemgetter(1)
                )
                if len(sorted_string_dict) > 0:
                    
                    if self.record_rule == 'max':
                        value = sorted_string_dict[-1][0]
            
                    elif self.record_rule == 'min':
                        value = sorted_string_dict[0][0]
            # If there is no record rule
            else:
                typed_annotations = []
                
                for value in annotations:
                
                    if self.data_type == 'float':
                        try:
                            typed_annotations.append(float(value))
                        except ValueError:
                            pass
                    
                    elif self.data_type == 'integer':
                        
                        try:
                            typed_annotations.append(int(value))
                        except ValueError:
                            pass
                
                if typed_annotations:
                    if self.record_rule == 'max':
                        value = max(typed_annotations)
                    
                    elif self.record_rule == 'min':
                        value = min(typed_annotations)
                else:
                    value = None
        
        # If no record rule is given we return the raw annotation
        # Here the data_type is not flag, and there is no record rule
        else:
            # We will just return the first annotation found
            if annotations:
                value = annotations[0]
            
        return value
    
    def __repr__(self):
        return "Plugin(name={0},field={1},data_type={2},separators={3},"\
                "record_rule={4},info_key={5},csq_key={6},category={7},"\
                "string_rules={8})".format(self.name, self.field, 
                self.data_type, self.separators,self.record_rule, 
                self.info_key, self.csq_key, self.category, 
                self.string_rules)

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