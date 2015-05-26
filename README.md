# Extract VCF

Many times one would like to extract values from different fields of a vcf file but there is no simple way to achieve this since the annotations can look very different.

extract_vcf takes a simple .ini config file that specifies rules of how the information should be treated and build objects that return the correct values.

examples of config files can be found in ```extract_vcf/examples```

## Installation

    pip install extract-vcf

## Idea

This package is made for extracting data from vcf files. Each type of data is described in a config file and a Plugin object is created based on these rules. The plugin can be given data for a variant and based on the rules it returns the proper value.
For integers and floats it is easy to understand rules like 'min' and 'max'.
Strings are a bit more complicated, here we will need rules for string matching. So for possible values of a string one can specify a score for each value, then we can apply rules such as min and max. 
If no rules are used the entry will be extracted in its raw form.
Flags will be returned as booleans.