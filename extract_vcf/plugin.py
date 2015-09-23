from logging import getLogger
import operator
import click

from extract_vcf import split_strings

class Plugin(object):
    """Class for holding information about a plugin"""
    def __init__(self, name, field, data_type=None, separators=[], info_key=None, 
                category=None, csq_key=None, record_rule=None, gt_key=None,
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
        self.regex = None
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
        
        self.gt_key = gt_key
        self.logger.info("gt_key: {0}".format(self.gt_key))
        
    
    def get_entry(self, variant_line=None, variant_dict=None, raw_entry=None, 
    vcf_header=None, csq_format=None, family_id=None, individual_id=None):
        """Return the splitted entry from variant information
            
            Args:
                variant_line (str): A vcf formated variant line
                vcf_header (list): A list with the vcf header line
                csq_format (list): A list with the csq headers
                family_id (str): The family id that should be searched. If no id 
                                 the first family found will be used
            
            Returns:
                entry (list): A list with the splitted entry
        """
        if not raw_entry:
            raw_entry = self.get_raw_entry(
                variant_line=variant_line, 
                variant_dict=variant_dict, 
                vcf_header=vcf_header, 
                individual_id=individual_id, 
            )
        
        entry = []
        
        if raw_entry:
            
            if self.field in ['CHROM', 'POS', 'REF', 'QUAL']:
                # We know these fields allways has one entry
                entry = [raw_entry]
            
            elif self.field in ['ID', 'FILTER']:
                # We know ID is allways splitted on ';'
                entry = raw_entry.split(';')
            
            elif self.field == 'ALT':
                # We know ALT is allways splitted on ','
                entry = raw_entry.split(',')
            
            elif self.field == 'FORMAT':
                entry = raw_entry.split(':')
            
            elif self.field == 'INFO':
                # We are going to treat csq fields separately
                if self.info_key == 'CSQ':
                    if not csq_format:
                        raise IOError("If CSQ the csq format must be provided")
                    if not self.csq_key:
                        raise IOError("If CSQ a csq key must be provided")
                    for i, head in enumerate(csq_format):
                        if head == self.csq_key:
                            # This is the csq entry we are looking for
                            csq_column = i
                    # CSQ entries are allways splitted on ','
                    for csq_entry in raw_entry.split(','):
                        entry += split_strings(csq_entry.split('|')[csq_column], self.separators)
                else:
                    entry = split_strings(raw_entry, self.separators)
            
            elif self.field == 'sample_id':
                if not self.separators:
                    entry = split_strings(raw_entry, '/')
                    #If variant calls are phased we need to split on '|'
                    if len(entry) == 1:
                        entry = split_strings(raw_entry, '|')
                else:
                    entry = split_strings(raw_entry, self.separators)
        
        return entry
    
    def get_raw_entry(self, variant_line=None, variant_dict=None, vcf_header=None, individual_id=None):
        """Return the raw entry from the vcf field
            
            If no entry was found return None
            
            Args:
                variant_line (str): A vcf formated variant line
                vcf_header (list): A list with the vcf header line
                individual_id (str): The individual id to get gt call
            Returns:
                The raw entry found in variant line
        """
        if variant_line:
            variant_line = variant_line.rstrip().split()
        
        entry = None
        
        if self.field == 'CHROM':
            if variant_line:
                entry = variant_line[0]
            elif variant_dict:
                entry = variant_dict['CHROM']
                
        elif self.field == 'POS':
            if variant_line:
                entry = variant_line[1]
            elif variant_dict:
                entry = variant_dict['POS']
            
        elif self.field == 'ID':
            if variant_line:
                entry = variant_line[2]
            elif variant_dict:
                entry = variant_dict['ID']
        
        elif self.field == 'REF':
            if variant_line:
                entry = variant_line[3]
            elif variant_dict:
                entry = variant_dict['REF']
        
        elif self.field == 'ALT':
            if variant_line:
                entry = variant_line[4]
            elif variant_dict:
                entry = variant_dict['ALT']
        
        elif self.field == 'QUAL':
            if variant_line:
                entry = variant_line[5]
            elif variant_dict:
                entry = variant_dict['QUAL']
        
        elif self.field == 'FILTER':
            if variant_line:
                entry = variant_line[6]
            elif variant_dict:
                entry = variant_dict['FILTER']
        
        elif self.field == 'INFO':
            if variant_line:
                for info_annotation in variant_line[7].split(';'):
                    splitted_annotation = info_annotation.split('=')
                    if self.info_key == splitted_annotation[0]:
                        if len(splitted_annotation) == 2:
                            entry = splitted_annotation[1]
            elif variant_dict:
                entry = variant_dict.get('info_dict',{}).get(self.info_key, None)
        
        elif self.field == 'FORMAT':
            if variant_line:
                entry = variant_line[8]
            elif variant_dict:
                entry = variant_dict['FORMAT']
        
        elif self.field == "sample_id":
            
            if not individual_id:
                raise IOError("If 'sample_id' a individual id must be provided")
            if not self.gt_key:
                raise IOError("If 'sample_id' a genotype key must be provided")
            
            if variant_line:
                if not vcf_header:
                    raise IOError("If 'sample_id' the vcf header must be provided")
                
                format_info = variant_line[8]
                
                for i, head in enumerate(vcf_header):
                    if head == individual_id:
                        raw_gt_call = variant_line[i]
            elif variant_dict:
                format_info = variant_dict['FORMAT']
                raw_gt_call = variant_dict[individual_id]
            
            entry_dict = dict(zip(
                format_info.split(':'), raw_gt_call.split(':')
            ))
            entry = entry_dict.get(self.gt_key, '.')
        
        return entry
    
    def get_value(self, variant_line=None, variant_dict=None, entry=None, 
        raw_entry=None, vcf_header=None, csq_format=None, family_id=None, 
        individual_id=None):
        """
        Return the value as specified by plugin
        
        Get value will return one value or None if no correct value is found.
        
        Arguments:
            variant_line (str): A vcf variant line
            variant_dict (dict): A variant dictionary
            entry (list): A splitted entry
            raw_entry (str): The raw entry from the vcf file
            vcf_header (list): The vcf header line with sample ids
            csq_format (list): The CSQ format
            family_id (str): The family id
            individual_id (str): The individual id
        
        Returns:
            value (str): A string that represents the correct value
        
        """
        value = None
        
        raw_entry = self.get_raw_entry(
            variant_line = variant_line, 
            variant_dict = variant_dict, 
            vcf_header=vcf_header, 
            individual_id=individual_id
        )
        # If data type is flag we only need to check if any entry exists
        if self.data_type == 'flag':
            if self.field == 'INFO':
                if variant_line:
                    for info_entry in variant_line.split()[7].split(';'):
                        if self.info_key == info_entry.split('=')[0]:
                            value = True
                
                elif variant_dict:
                    if self.info_key in variant_dict.get('info_dict',{}):
                        value = True
            else:
                if raw_entry != '.':
                    value = True
        
        # If we have a record rule we need to return the correct value
        elif raw_entry:
        # If there was no raw entry we will return None
            if self.record_rule:
            
                if self.data_type == 'string':
                
                    if self.record_rule == 'max':
                        sorted_strings = sorted(
                            self.string_rules.items(), 
                            key=operator.itemgetter(1), 
                            reverse=True
                        )
                    
                    if self.record_rule == 'min':
                        sorted_strings = sorted(
                            self.string_rules.items(), 
                            key=operator.itemgetter(1)
                        )
                    
                    for string_rule in sorted_strings:
                        if string_rule[0].lower() in raw_entry.lower():
                            value = string_rule[0]
                            break
                else:
                
                    typed_annotations = []
                
                    for value in self.get_entry(
                        raw_entry=raw_entry,
                        vcf_header=vcf_header, 
                        csq_format=csq_format, 
                        family_id=family_id, 
                        individual_id=individual_id):
                
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
            # We know that there exists a raw annotation
            else:
                # We will just return the first annotation found
                value = self.get_entry(
                        raw_entry=raw_entry,
                        vcf_header=vcf_header, 
                        csq_format=csq_format, 
                        family_id=family_id, 
                        individual_id=individual_id)[0]
                
                if self.data_type == 'float':
                        try:
                            value = float(value)
                        except ValueError:
                            pass
                    
                elif self.data_type == 'integer':
                    try:
                        value = int(value)
                    except ValueError:
                        pass
        
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