from extract_vcf import get_vep_annotation

# {u'G': [{u'TSL': u'', u'SYMBOL': u'OR4F5', u'HGNC_ID': u'14825', u'Codons': u'tTt/tGt', u'MOTIF_NAME': u'', u'DOMAINS': u'Transmembrane_helices:Tmhmm&Pfam_domain:PF00001&Pfam_domain:PF10320&Prints_domain:PR00237&PROSITE_profiles:PS50262&Superfamily_domains:SSF81321', u'SIFT': u'deleterious', u'CDS_position': u'338', u'Allele': u'G', u'CCDS': u'CCDS30547.1', u'PolyPhen': u'possibly_damaging', u'MOTIF_SCORE_CHANGE': u'', u'HGVSp': u'ENSP00000334393.3:p.Phe113Cys', u'ENSP': u'ENSP00000334393', u'INTRON': u'', u'Existing_variation': u'', u'HGVSc': u'ENST00000335137.3:c.338N>G', u'HIGH_INF_POS': u'', u'cDNA_position': u'338', u'Feature_type': u'Transcript', u'Feature': u'ENST00000335137', u'SWISSPROT': u'OR4F5_HUMAN', u'UNIPARC': u'UPI0000041BC1', u'Consequence': u'missense_variant', u'Protein_position': u'113', u'Gene': u'ENSG00000186092', u'STRAND': u'1', u'DISTANCE': u'', u'SYMBOL_SOURCE': u'HGNC', u'Amino_acids': u'F/C', u'TREMBL': u'', u'MOTIF_POS': u'', u'BIOTYPE': u'protein_coding', u'EXON': u'1/1'}]}

def test_simple_vep():
    """Test how get_vep_annotations behaves in a simple case simple string"""
    vep_entry = {'G': [{'SYMBOL':"OR4FS"}]}
    vep_key = 'SYMBOL'
    splitters = [',']
    
    assert set(get_vep_annotation(vep_entry, vep_key, splitters)) == set(["OR4FS"])

def test_no_annotation():
    """Test how get_vep_annotations behaves in a simple case simple string"""
    vep_entry = {'G': [{'HGNCID':"14825"}]}
    vep_key = 'SYMBOL'
    splitters = [',']
    
    assert set(get_vep_annotation(vep_entry, vep_key, splitters)) == set([])

def test_no_vep_entries():
    """Test how get_vep_annotations behaves in a simple case simple string"""
    vep_entry = {}
    vep_key = 'SYMBOL'
    splitters = [',']
    
    assert set(get_vep_annotation(vep_entry, vep_key, splitters)) == set([])


def test_multiple_alleles():
    """Test how get_vep_annotations behaves in a simple case simple string"""
    vep_entry = {
        'G': [{'Consequence':"missense_variant"}],
        'A': [{'Consequence':"stop_gain"}]
    }
    vep_key = 'Consequence'
    splitters = [',']
    
    assert set(get_vep_annotation(vep_entry, vep_key, splitters)) == set(["missense_variant", "stop_gain"])

def test_multiple_annotations():
    """Test how get_vep_annotations behaves in a simple case simple string"""
    vep_entry = {
        'G': [
            {'Consequence':"missense_variant"},
            {'Consequence':"regulatory_region_variant"}]
    }
    vep_key = 'Consequence'
    splitters = [',']
    
    assert set(get_vep_annotation(vep_entry, vep_key, splitters)) == set(["missense_variant", "regulatory_region_variant"])

def test_splitted_annotations():
    """Test how get_vep_annotations behaves in a simple case simple string"""
    vep_entry = {
        'G': [{'Consequence':"missense_variant&stop_gain"}]
    }
    vep_key = 'Consequence'
    splitters = ['&']
    
    assert set(get_vep_annotation(vep_entry, vep_key, splitters)) == set(["missense_variant", "stop_gain"])

def test_complex_annotations():
    """Test how get_vep_annotations behaves in a simple case simple string"""
    vep_entry = {
        'G': [
            {'Consequence':"missense_variant&stop_gain"}
            ],
        'A': [
            {'Consequence':"regulatory_region_variant"}
        ]
    }
    vep_key = 'Consequence'
    splitters = ['&']
    
    assert set(get_vep_annotation(vep_entry, vep_key, splitters)) == set([
        "missense_variant", "regulatory_region_variant", "stop_gain"])

def test_simple_no_splitters():
    """Test how get_vep_annotations behaves in a simple case simple string"""
    vep_entry = {'G': [{'SYMBOL':"OR4FS"}]}
    vep_key = 'SYMBOL'
    
    assert set(get_vep_annotation(vep_entry, vep_key)) == set(["OR4FS"])
