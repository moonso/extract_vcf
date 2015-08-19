from extract_vcf import get_info_annotation

def test_simple_info():
    """Test how get_info_annotations behaves in a simple case simple string"""
    info_dict = {'MQ':['1']}
    info_key = 'MQ'
    splitters = [',']
    
    assert set(get_info_annotation(info_dict, info_key, splitters)) == set(["1"])

def test_info_key():
    """Test how get_info_annotations behaves when missing info key"""
    info_dict = {'MQ':['1']}
    info_key = 'AF'
    splitters = [',']
    
    assert set(get_info_annotation(info_dict, info_key, splitters)) == set([])

def test_no_info():
    """Test how get_info_annotations behaves when no info"""
    info_dict = {}
    info_key = 'AF'
    splitters = [',']
    
    assert set(get_info_annotation(info_dict, info_key, splitters)) == set([])

def test_flag_data_type():
    """Test how get_info_annotations behaves when data type is flag"""
    info_dict = {}
    info_key = 'AF'
    splitters = [',']
    data_type = 'flag'
    
    assert set(get_info_annotation(info_dict, info_key, splitters, data_type)) == set([])

    info_dict = {'AF':[]}
    info_key = 'AF'

    assert set(get_info_annotation(info_dict, info_key, splitters, data_type)) == set([True])


def test_simple_split():
    """Test how get_info_annotations behaves with simple split"""
    info_dict = {'AF':['0.1','0.2']}
    info_key = 'AF'
    splitters = [',']
    
    assert set(get_info_annotation(info_dict, info_key, splitters)) == set(["0.1","0.2"])

def test_different_split():
    """Test how get_info_annotations behaves when special split is used"""
    info_dict = {'AF':['0.1|0.2']}
    info_key = 'AF'
    splitters = ['|']
    
    assert set(get_info_annotation(info_dict, info_key, splitters)) == set(["0.1","0.2"])


def test_complex_split():
    """Test how get_vep_annotations behaves in a simple case simple string"""
    info_dict = {'GeneticModels':['1:AD|AD_dn', '2:AR_hom']}
    info_key = 'GeneticModels'
    splitters = [',',':','|']
    
    assert set(get_info_annotation(info_dict, info_key, splitters)) == set([
        '1','AD','AD_dn','2','AR_hom'])
