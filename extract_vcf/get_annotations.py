from __future__ import unicode_literals
import logging
import click


def split_strings(string, separators):
    """
    Split a string with arbitrary number of separators.
    Return a list with the splitted values
    
    Arguments:
        string (str): ex. "a:1|2,b:2"
        separators (list): ex. [',',':','|']
    
    Returns:
         results (list) : ex. ['a','1','2','b','2']
    """
    logger = logging.getLogger(__name__)
    logger = logging.getLogger('extract_vcf.split_strings')
    logger.debug("splitting string '{0}' with separators {1}".format(
        string, separators
    ))
    results = []
    
    def recursion(recursive_string, separators, i=1):
        """
        Split a string with arbitrary number of separators.
        Add the elements of the string to global list result.
        
        Arguments:
            string : ex. "a:1|2,b:2"
            separators (list): ex. [',',':','|']
        
        Returns:
             Adds splitted string to results. ex. ['a','1','2','b','2']
        """
        if i == len(separators):
            for value in recursive_string.split(separators[i-1]):
                logger.debug("Adding {0} to results".format(value))
                results.append(value)
        else:
            for value in recursive_string.split(separators[i-1]):
                recursion(value, separators, i+1)
    if len(separators) > 0:
        recursion(string, separators)
    else:
        results = [string]
    
    return results

def get_vep_annotation(vep_entry, vep_key, separators=[]):
    """
    Return the vep annotations found.
    
    Arguments:
        vep_entry (dict): A dictionary with alleles as keys and a list of 
        dictionarys with vep annotations as value
        
        separators (list): A list that defines how the annotations are splitted
    
    Returns:
        vep_annotations (list): A list with the splitted annotations
    """
    logger = logging.getLogger(__name__)
    logger = logging.getLogger('extract_vcf.get_vep_annotation')
    
    logger.debug("Finding vep annotations for {0} with separators {1}".format(
        vep_key, separators
    ))
    vep_annotations = []
    
    
    for allele in vep_entry:
        for annotation in vep_entry[allele]:
            if vep_key in annotation:
                
                csq_entry = annotation[vep_key]
                logger.debug("Found vep entry '{0}'".format(csq_entry))
                
                for splitted_result in split_strings(csq_entry, separators):
                    vep_annotations.append(splitted_result)
    
    
    return vep_annotations

def get_info_annotation(info_dict, info_key, separators = [], data_type=None):
    """
    Parse the info annotation and return a list with the relevant information
    """
    info_annotation = []
    
    if info_key in info_dict:
        if data_type == 'flag':
            info_annotation = [True]
        else:
            annotation = info_dict[info_key]
            # Remove ',' from separators since all info fields are splitted on ','
            # by vcf_parser
            new_separators = [separator for separator in separators if separator != ',']
            for annotation_string in annotation:
                for splitted_result in split_strings(annotation_string, new_separators):
                    info_annotation.append(splitted_result)
    
    return info_annotation

def get_other_annotation(variant, field, separators = []):
    """
    Parse a vcf field that is not info and return a list with the relevant information
    """
    other_annotation = []
    
    raw_annotation = variant.get(field, '.')
    
    if raw_annotation != '.':
        for splitted_result in split_strings(raw_annotation, separators):
            other_annotation.append(splitted_result)
    
    return other_annotation


def get_annotation(variant, field, data_type, separators=[], info_key=None, csq_key=None):
    """
    Return a list of splitted strings that is the raw entry from the vcf
    
    Arguments:
        variant (dict): A variant dictionary
        field (str): The field that should be checked in the vcf
        separators (list): A list of strings that describes how the string is splitted
        info_key (str): The key to the entry in the info field
        csq_key (str): The key to the vep entry in the CSQ field
    
    Returns:
        annotation (list): A list with annotations found that represents the raw entry
    """
    
    logger = logging.getLogger(__name__)
    
    #For testing
    logger = logging.getLogger("extract_vcf.get_annotations")
    
    logger.debug("Finding annotations for variant:{0}. Field:{1}, "\
                 "separators:{2}, info_key:{3}, csq_key:{4}".format(
                     variant.get('variant_id', 'unknown'), field, separators, info_key, csq_key
                 ))
    annotations = []
    logger.debug("Initializing annotations: {0}".format(annotations))
    
    logger.debug("Checking the {0} field".format(field))
    
    if field == 'INFO':
        
        logger.debug("Checking the info field {0}".format(field))
        
        if info_key == 'CSQ':
            
            vep_info = variant.get('vep_info', {})
            annotations = get_vep_annotation(
                vep_entry=vep_info, vep_key=csq_key, separators=separators)
        
        else:
            
            info_dict = variant.get('info_dict', {})
            annotations = get_info_annotation(info_dict=info_dict, 
                                info_key=info_key, separators = separators, data_type=data_type)
    else:
        annotations = get_other_annotation(variant=variant, field=field, separators=separators)

    return annotations


@click.command()
@click.argument('vcf_file',
                nargs=1,
                type=click.Path(exists=True)
)
@click.option('-l', '--loglevel',
                type=click.Choice(['DEBUG', 'INFO', 'WARNING']),
                default = 'DEBUG'
)
def cli(vcf_file, loglevel):
    """Parse the config file and print it to the output."""
    from vcf_parser import VCFParser
    from extract_vcf import logger, init_log
    init_log(logger, loglevel=loglevel)
    
    logger.info("Reading VCF File: {0}".format(vcf_file))
    
    vcf = VCFParser(vcf_file, skip_info_check = True)
    
    field = 'INFO'
    info_key = "CSQ"
    csq_key = 'Consequence'
    separators = ['&']
    data_type = 'string'
    
    for variant in vcf:
        print(get_annotation(variant, field, data_type, separators, info_key, csq_key))
    
if __name__ == '__main__':
    cli()
