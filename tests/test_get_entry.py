from extract_vcf import Plugin
import pytest

variant = "2    191964633    rs7574865    T    G    1258.77    PASS;NOT_PASS    1000GAF=0.744609;AC=2;AF=1.00;AN=2;CLNSIG=255,10;CSQ=G|ENSG00000138378|ENST00000358470|Transcript|intron_variant||||||||-1|STAT4|HGNC|11365|protein_coding||CCDS2310.1|ENSP00000351255|STAT4_HUMAN|Q53S87_HUMAN&Q53RU2_HUMAN&E9PBE2_HUMAN&C9JM11_HUMAN&C9JFG0_HUMAN&B7SIX5_HUMAN|UPI00000015F2||||3/23||ENST00000358470.4:c.274-23582A>C|||||,G|ENSG00000138378|ENST00000392320|Transcript|intron_variant||||||||-1|STAT4|HGNC|11365|protein_coding||CCDS2310.1|ENSP00000376134|STAT4_HUMAN|Q53S87_HUMAN&Q53RU2_HUMAN&E9PBE2_HUMAN&C9JM11_HUMAN&C9JFG0_HUMAN&B7SIX5_HUMAN|UPI00000015F2||||3/23||ENST00000392320.2:c.274-23582A>C|||||,G|ENSG00000138378|ENST00000495326|Transcript|intron_variant&non_coding_transcript_variant||||||||-1|STAT4|HGNC|11365|retained_intron||||||||||3/3||ENST00000495326.1:n.344-23582A>C|||||,G|ENSG00000138378|ENST00000495849|Transcript|intron_variant&non_coding_transcript_variant||||||||-1|STAT4|HGNC|11365|retained_intron||||||||||3/20||ENST00000495849.1:n.342-23582A>C|||||,G|ENSG00000138378|ENST00000413064|Transcript|intron_variant||||||||-1|STAT4|HGNC|11365|protein_coding|||ENSP00000403238||C9JFG0_HUMAN|UPI000188188B||||3/3||ENST00000413064.1:c.193-23582A>C|||||;Clinical_db_gene_annotation=OMIM-141201,FullList;DB;DP=35;Dbsnp129LCAF=0.2493;Ensembl_gene_id=ENSG00000138378;Ensembl_transcript_to_refseq_transcript=STAT4:ENST00000358470>NM_001243835/XM_005246817|ENST00000392320>NM_003151|ENST00000409995|ENST00000413064|ENST00000432798|ENST00000450994|ENST00000463951|ENST00000470708|ENST00000495326|ENST00000495849;FS=0.000;GQ_MEAN=105.00;Gene_description=STAT4:signal_transducer_and_activator_of_transcription_4;GeneticRegionAnnotation=STAT4:G|ncRNA;HGNC_symbol=STAT4;HGVScp=G:STAT4:ENST00000358470:intron_variant:s.-:i.3/23:c.274-23582A>C,G:STAT4:ENST00000392320:intron_variant:s.-:i.3/23:c.274-23582A>C,G:STAT4:ENST00000495326:intron_variant&non_coding_transcript_variant:s.-:i.3/3:n.344-23582A>C,G:STAT4:ENST00000495849:intron_variant&non_coding_transcript_variant:s.-:i.3/20:n.342-23582A>C,G:STAT4:ENST00000413064:intron_variant:s.-:i.3/3:c.193-23582A>C;MLEAC=2;MLEAF=1.00;MQ=60.00;MQ0=0;MostSevereConsequence=STAT4:G|non_coding_transcript_variant;NCC=0;OMIM_morbid=STAT4:600558;POSITIVE_TRAIN_SITE;Phenotypic_disease_model=STAT4:612253;QD=28.42;SOR=1.148;SnpSift_AF=0.744609;SnpSift_CAF=[0.2493,0.7507];SnpSift_CLNSIG=255;VQSLOD=4.27;culprit=FS    GT:AD:GQ:PL    1/1:0,35:99:1287,105,0"

phased_variant = "2    191964633    rs7574865    T    G    1258.77    PASS;NOT_PASS    1000GAF=0.744609;GeneticModels=1:AD|AD_dn    GT:AD:GQ:PL    1|1:0,35:99:1287,105,0"

multi_allele_variant = "2    191964633    rs7574865    T    G,A    1258.77    PASS;NOT_PASS    1000GAF=0.744609,0.02    GT:AD:GQ:PL    1/2:0,35:99:1287,105,0"

csq_format = ["Allele", "Gene", "Feature", "Feature_type", "Consequence", 
"cDNA_position", "CDS_position", "Protein_position", "Amino_acids", "Codons",
 "Existing_variation", "DISTANCE", "STRAND", "SYMBOL", "SYMBOL_SOURCE", "HGNC_ID",
 "BIOTYPE", "TSL", "CCDS", "ENSP", "SWISSPROT", "TREMBL", "UNIPARC", "SIFT",
  "PolyPhen", "EXON", "INTRON", "DOMAINS", "HGVSc", "HGVSp", "MOTIF_NAME", 
  "MOTIF_POS", "HIGH_INF_POS", "MOTIF_SCORE_CHANGE"]

def test_chrom():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='Chrom', field='CHROM')
    assert plugin.get_entry(variant) == ['2']

def test_pos():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='Pos', field='POS')
    assert plugin.get_entry(variant) == ['191964633']

def test_id():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='ID', field='ID')
    assert plugin.get_entry(variant) == ['rs7574865']

def test_ref():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='ID', field='REF')
    assert plugin.get_entry(variant) == ['T']

def test_alt():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='ID', field='ALT')
    assert plugin.get_entry(variant) == ['G']

def test_multi_alt():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='ID', field='ALT')
    assert plugin.get_entry(multi_allele_variant) == ['G','A']

def test_qual():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='QUAL', field='QUAL')
    assert plugin.get_entry(variant) == ['1258.77']

def test_filter():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='Filter', field='FILTER')
    assert plugin.get_entry(variant) == ['PASS', 'NOT_PASS']

def test_1000G():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='thousand_g', field='INFO', info_key="1000GAF", separators=[','])
    assert plugin.get_entry(variant) == ['0.744609']

def test_non_existing():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='non_existing', field='INFO', info_key="non", separators=[','])
    assert plugin.get_entry(variant) == []

def test_CLNSIG():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='Clnsig', field='INFO', info_key="CLNSIG", separators=[','])
    assert plugin.get_entry(variant) == ['255','10']

def test_CSQ():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='CSQ', field='INFO', info_key="CSQ", csq_key="Gene", separators=['&'])
    assert plugin.get_entry(variant, csq_format=csq_format) == [
        'ENSG00000138378', 
        'ENSG00000138378', 
        'ENSG00000138378', 
        'ENSG00000138378',
        'ENSG00000138378'
    ]

def test_family_level():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='genetic_models', field='INFO', info_key="GeneticModels", separators=[','])
    assert plugin.get_entry(phased_variant) == ['1:AD|AD_dn']

def test_format():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='Format', field='FORMAT')
    assert plugin.get_entry(variant) == ['GT','AD','GQ','PL']

def test_gt_call():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='gt_call', field='sample_id', gt_key='GT')
    vcf_header = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT', 'ADM1003A3']
    assert plugin.get_entry(variant, vcf_header=vcf_header, individual_id='ADM1003A3') == ['1','1']

def test_gt_call_PL():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='gt_call', field='sample_id', gt_key='PL', separators=[','])
    vcf_header = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT', 'ADM1003A3']
    assert plugin.get_entry(variant, vcf_header=vcf_header, individual_id='ADM1003A3') == ['1287','105','0']

def test_phased_gt_call():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='gt_call', field='sample_id', gt_key='GT')
    vcf_header = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT', 'ADM1003A3']
    assert plugin.get_entry(phased_variant, vcf_header=vcf_header, individual_id='ADM1003A3') == ['1','1']

def test_gt_call_no_gt_key():
    """Test to get the raw chromosome"""
    plugin = Plugin(name='gt_call', field='sample_id')
    vcf_header = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT', 'ADM1003A3']
    with pytest.raises(IOError):
        plugin.get_raw_entry(variant, individual_id='ADM1003A3')

