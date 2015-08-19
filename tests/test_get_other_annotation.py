from extract_vcf import get_other_annotation

def test_simple_info():
    """Test how get_other_annotations behaves in a simple case"""
    variant = {'FILTER': 'PASS'}
    field = 'FILTER'
    splitters = [';']
    
    assert set(get_other_annotation(variant, field, splitters)) == set(["PASS"])

def test_no_entry():
    """Test how get_other_annotations behaves in a simple case"""
    variant = {'FILTER': '.'}
    field = 'FILTER'
    splitters = [';']
    
    assert set(get_other_annotation(variant, field)) == set([])

def test_no_splitters():
    """Test how get_other_annotations behaves in a simple case"""
    variant = {'FILTER': 'PASS'}
    field = 'FILTER'
    
    assert set(get_other_annotation(variant, field)) == set(["PASS"])

def test_splitted_entry():
    """Test how get_other_annotations behaves in a simple case"""
    variant = {'FILTER': 'PASS;LowQual'}
    field = 'FILTER'
    splitters = [';']
    
    assert set(get_other_annotation(variant, field, splitters)) == set(["PASS", "LowQual"])

