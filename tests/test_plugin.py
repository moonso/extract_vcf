from extract_vcf import Plugin

def setup_vcf():
    """
    Setup a vcf file and return the path to the vcf
    """
    header = [
        '##fileformat=VCFv4.2',
        '##INFO=<ID=MQ,Number=1,Type=Float,Description="RMS Mapping Quality"">',
        '##INFO=<ID=CNT,Number=A,Type=Integer,Description="Number of times'\
        ' this allele was found in external db">',
        '##contig=<ID=1,length=249250621,assembly=b37>',
        '##INFO=<ID=DP_HIST,Number=R,Type=String,Description="Histogram for'\
        ' DP; Mids: 2.5|7.5|12.5|17.5|22.5|27.5|32.5|37.5|42.5|47.5|52.5|57.5'\
        '|62.5|67.5|72.5|77.5|82.5|87.5|92.5|97.5">',
        '##FORMAT=<ID=AD,Number=.,Type=Integer,Description="Allelic depths '\
        'for the ref and alt alleles in the order listed">',
        '##FORMAT=<ID=DP,Number=1,Type=Integer,Description="Read Depth">',
        '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
        '##FORMAT=<ID=GQ,Number=1,Type=String,Description="GenotypeQuality">',
        '##reference=file:///humgen/gsa-hpprojects/GATK/bundle/current/b37/'\
        'human_g1k_v37.fasta',
        '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tfather\tmother'\
        '\tproband'
    ]
    

def setup_variant(chrom='1', pos='1', rs_id='.', ref='a', alt='c', qual='.', 
                   filt='.', info='.', form=None, info_dict=None):
    """
    Setup a variant dictionary with the info given
    
    Returns:
        variant (dict): A variant dictionary
    """
    variant = {
        'CHROM': chrom,
        'POS': pos,
        'ID': rs_id,
        'REF': ref,
        'ALT': alt,
        'QUAL': qual,
        'FILTER': filt,
        'INFO': info,
    }
    if form:
        variant['FORMAT'] = form
    
    if info_dict:
        variant['info_dict'] = info_dict
    
    return variant

def test_inititating_plugin():
    """
    Test if basic setup works
    """
    name = "Example"
    field = "FILTER"
    data_type = "string"
    separators = [';']
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators)
    
    assert test_plugin.name == name
    assert test_plugin.field == field
    assert test_plugin.data_type == data_type
    assert test_plugin.separators == separators

def test_inititating_info_plugin():
    """
    Test if basic setup works
    """
    name = "Example"
    field = "INFO"
    data_type = "integer"
    separators = [',']
    info_key = 'MQ'
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators, info_key=info_key)
    
    assert test_plugin.name == name
    assert test_plugin.field == field
    assert test_plugin.data_type == data_type
    assert test_plugin.separators == separators
    assert test_plugin.info_key == info_key
    
def test_minimal_plugin():
    """
    Test if basic setup works
    """
    name = "Example"
    field = "FILTER"
    data_type = "flag"
    test_plugin = Plugin(name=name, field=field, data_type=data_type)

    entry = 'PASS'
    variant = setup_variant(filt=entry)
    
    assert test_plugin.get_value(variant) == True

def test_minimal_negative_plugin():
    """
    Test if basic setup works
    """
    name = "Example"
    field = "FILTER"
    data_type = "flag"
    test_plugin = Plugin(name=name, field=field, data_type=data_type)

    entry = '.'
    variant = setup_variant(filt=entry)
    
    assert test_plugin.get_value(variant) == False


def test_get_value():
    """
    Test if basic get value works
    """
    name = "Example"
    field = "FILTER"
    data_type = "string"
    separators = [';']
    entry = 'PASS'
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators)
    
    variant = setup_variant(filt=entry)

    assert test_plugin.get_value(variant) == 'PASS'

def test_multi_value():
    """
    Test if a filter with two values return correct
    """
    name = "Example"
    field = "FILTER"
    data_type = "string"
    separators = [';']
    entry = 'PASS;LOWQual'
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators)
    
    variant = setup_variant(filt=entry)
    
    #Since there is no record rule the first annotation found will be returned
    assert test_plugin.get_value(variant) == "PASS"

def test_string_rules():
    """
    Test if a if the string rules work correct
    """
    name = "Example"
    field = "FILTER"
    data_type = "string"
    separators = [';']
    entry = 'PASS;LOWQual'
    string_rules = {'PASS':1, 'LOWQual':0}
    record_rule = 'min'
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators, record_rule=record_rule,
                        string_rules=string_rules)
    
    variant = setup_variant(filt=entry)

    assert test_plugin.get_value(variant) == 'LOWQual'

def test_string_rules_max():
    """
    Test if a if the string rules work correct
    """
    name = "Example"
    field = "FILTER"
    data_type = "string"
    separators = [';']
    entry = 'PASS;LOWQual'
    string_rules = {'PASS':1, 'LOWQual':0}
    record_rule = 'max'
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators, record_rule=record_rule,
                        string_rules=string_rules)
    
    variant = setup_variant(filt=entry)

    assert test_plugin.get_value(variant) == 'PASS'


def test_get_info_value():
    """
    Test if basic get value works
    """
    name = "Example"
    field = "INFO"
    data_type = "integer"
    separators = [',']
    info_dict = {'MQ': ['1', '2']}
    record_rule = 'max'
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators, info_key='MQ', 
                        record_rule=record_rule)
    
    variant = setup_variant(info='MQ=1,2', info_dict=info_dict)
    
    assert test_plugin.get_value(variant) == 2

def test_get_flag_value():
    """
    Test if get value with a flag works
    """
    name = "Example"
    field = "INFO"
    data_type = "flag"
    info_dict = {'MQ': True}
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=[], info_key='MQ')
    
    variant = setup_variant(info='MQ', info_dict=info_dict)
    
    assert test_plugin.get_value(variant) == True

def test_get_negative_flag_value():
    """
    Test if get value with a flag works
    """
    name = "Example"
    field = "INFO"
    data_type = "flag"
    info_dict = {}
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=[], info_key='MQ')
    
    variant = setup_variant(info='', info_dict=info_dict)
    
    assert test_plugin.get_value(variant) == False

def test_info_value_float():
    """
    Test if if getting a float value works
    """
    name = "Example"
    field = "INFO"
    data_type = "float"
    separators = [',']
    info_dict = {'TEST': ['0.1', '0.2']}
    record_rule = 'min'
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators, info_key='TEST', 
                        record_rule=record_rule)
    
    variant = setup_variant(info_dict=info_dict)
    
    assert test_plugin.get_value(variant) == 0.1

def test_info_value_float_wrong_entry():
    """
    Test if if getting a float value works
    """
    name = "Example"
    field = "INFO"
    data_type = "float"
    separators = [',']
    info_dict = {'TEST': ['True']}
    record_rule = 'min'
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators, info_key='TEST', 
                        record_rule=record_rule)
    
    variant = setup_variant(info_dict=info_dict)
    
    assert test_plugin.get_value(variant) == None


def test_complex_info_value():
    """
    Test if complex info value works
    """
    name = "Example"
    field = "INFO"
    data_type = "integer"
    separators = [',',':','|']
    info_dict = {'TEST': ['a:12|11', 'b:9|27']}
    record_rule = 'min'
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators, info_key='TEST', 
                        record_rule=record_rule)
    
    variant = setup_variant(info_dict=info_dict)
    
    assert test_plugin.get_value(variant) == 9
    
    