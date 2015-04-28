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
                   filt='.', info='.', form='.'):
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
        'FORMAT': form
    }
    
    return variant

def test_inititating_plugin():
    """
    Test if basic setup works
    """
    name = "Example"
    field = "FILTER"
    data_type = "str"
    separators = [';']
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators)
    
    assert test_plugin.name == name
    assert test_plugin.field == field
    assert test_plugin.data_type == data_type
    assert test_plugin.separators == separators
    

def test_get_value():
    """
    Test if basic get value works
    """
    name = "Example"
    field = "FILTER"
    data_type = "str"
    separators = [';']
    test_plugin = Plugin(name=name, field=field, data_type=data_type, 
                        separators=separators)
    
    variant = setup_variant(filt='PASS')
    
    assert test_plugin.get_value(variant) == 'PASS'
    
    