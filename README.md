# Extract VCF

Many times one would like to extract values from different fields of a vcf file. There is no simple way to achieve this since the annotations can look very different, sometimes they are a flag, sometimes there are multiple values etc.

extract_vcf takes a simple .ini config file that specifies rules of how the information should be treated and build objects that return the correct values.

examples of config files can be found in ```extract_vcf/examples```

## Installation

    pip install extract-vcf

## Idea

This package is made for extracting data from vcf files. 
Each type of data is described in a config file and a Plugin object will be created for each type of data.  
The plugin can be given data for a variant and based on the rules it returns the proper value.
For integers and floats it is easy to understand rules like 'min' and 'max'.
Strings are a bit more complicated, here we will need rules for string matching. So for possible values of a string one can specify a score for each value, then we can apply rules such as min and max. 
If no rules are used the entry will be extracted in its raw form.
Flags will be returned as booleans.

## Usage ##

```
> cat examples/smallest_test/small_config.ini
[Version]
  version = 0.1 # Float that describes the version number
  name = example # String with the name of the config

[CADD] # Plugin name
  ### Mandatory ###
  field = INFO # Anyone [ID, FILTER, QUAL, INFO]
  data_type = float # [float, int, str, flag]
  # Mandatory for any data type except flag
  record_rule = max # Description of how multiple values should be treated. [min, max, eq]
  separators = ',' # How is the field splitted, this is a list of separators
  ### Mandatory for INFO fields ###
  info_key = CADD # If field = INFO the info_key is mandatory
  ### optional ###
  description = The CADD predicted deleteriousness # A string that describes the plugin
  category = deleteriousness # What category does the plugin belong to

[Exac] # Plugin name
  ### Mandatory ###
  field = INFO # Anyone [ID, FILTER, QUAL, INFO]
  data_type = float # [float, int, str, bool]
  record_rule = min # Description of how multiple values should be treated. [min, max, eq]
  separators = ',' # How is the field splitted, this is a list of separators
  ### Mandatory for INFO fields ###
  info_key = EXAC # If field = INFO the info_key is mandatory
  ### optional ###
  description = The EXAC frequency # A string that describes the plugin
  category = allele_frequencies # What category does the plugin belong to
> cat examples/smallest_test/small_test.vcf
##fileformat=VCFv4.1
##contig=<ID=1,length=249250621,assembly=b37>
##INFO=<ID=CADD,Number=A,Type=Float,Description="The CADD relative score for this alternative.">
##reference=file:///humgen/gsa-hpprojects/GATK/bundle/current/b37/human_g1k_v37.fasta
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	proband_2
1	879537	.	T	C	100	PASS	MQ=1;CADD=12.5;EXAC=0.02	GT:AD:GQ	1/1:10,10:60
1	879538	.	T	A	100	PASS	MQ=1;EXAC=0.001	GT:AD:GQ	1/1:10,10:60
```


```python
> import extract_vcf
> configs = extract_vcf.ConfigParser("examples/smallest_test/small_config.ini")
> for plugin_name in configs.plugins:
   print(plugin_name)
   print(configs.plugins[plugin_name])
Exac
Plugin(name=Exac,field=INFO,data_type=float,separators=[u','],record_rule=min,info_key=EXAC,csq_key=None,category=allele_frequencies,string_rules={})
CADD
Plugin(name=CADD,field=INFO,data_type=float,separators=[u','],record_rule=max,info_key=CADD,csq_key=None,category=deleteriousness,string_rules={})
> import vcf_parser
> vcf = vcf_parser.VCFParser(infile="examples/smallest_test/small_test.vcf")
> for variant in vcf:
     print("Checking values for variant {0}:".format(variant["variant_id"]))
     for plugin_name in configs.plugins:
         plugin = configs.plugins[plugin_name]
         value = plugin.get_value(variant)
         print("\tPlugin name:{0}, value:{1}".format(plugin_name, value))
Checking values for variant 1_879537_T_C:
	Plugin name:Exac, value:0.02
	Plugin name:CADD, value:12.5
Checking values for variant 1_879538_T_A:
	Plugin name:Exac, value:0.001
	Plugin name:CADD, value:None
```

## How to build a config file

These files should be in the .ini format and follow the structure described in this section.
There are some mandatory fields for any plugin, for certain types of plugins there are extra mandatory fields.

The .ini format consists of sections that are specified by ```[]```, for example ```[Version]``` would be the Version section.  
It is allowed to use nestled sections by increasing the number of brackets, like ```[[]]```.
Then the information is specified in a key-value format like ```name = Example```.
 

### Mandatory sections

Each config file needs to have a **Version** section with a version and a name.

Example:  

```
[Version]
  version = 0.1 # Float that describes the version number
  name = example # String with the name of the config
```


## Plugins

The sections following the version section are describing the plugins.
The section name is therefore the name of the plugin and the fields in the section describe rules for how the information should be handeld.

### Mandatory fields ###

As mentioned the section name describes the plugin.

```[1000G]```

Then we need to describe what vcf field to look at with

```field = INFO # Anyone of [ID, FILTER, QUAL, INFO]```

The data type must be specified with

```data_type = float # Anyone of [float, int, str, flag]```


So a minimal definition of a plugin could look like:

```
[DBSNP]
  field = ID
  data_type = flag
```

This creates a plugin that would return True if a vcf variant have a entry that is not '.' in the ```ID``` field.

#### float, int, str ####

If the data type is float, int or str we need to specify a record rule and separators.
The record rule define what value to choose when there can be alternatives, like:

```record_rule = min # Description of how multiple values should be treated. [min, max]```

and separators like:

```separators = ','```

There can be multiple separators, these are then described like:

```separators = ',',':'```

### INFO fields ###

Info fields must have a info key that determines what info field to search for:

```info_key = 1000G_freq```

to finish up on the 1000G example the whole plugin could look like:

```
[1000G]
    field = INFO
    data_type = float
    record_rule = max
    separators = ','
    info_key = 1000G_freq
```

When sending a variant to this plugin it will search for the max value in the 1000g_freq key in the INFO field.


### CSQ keys

If ```info_key = CSQ``` we are searching in a vep annotation field and then need a vep key

```csq_key = Feature_type```

### String matches ###

If the values are strings we need some way to compare them to return the most interesting one.
This is being done by forming a subsection with each possible string match and its priority like:

```
[Filter]
  field = FILTER
  data_type = string
  record_aggregation = min
  field_separators = ';'
  description = Check the filters and return the worst
  
  [[PASS]]
    value = "PASS"
    priority = 3
  
  [[VSQRT]]
    value = "VQSRTrancheBOTH99.90to100.00"
    priority = 2

  [[LowQual]]
    value = "LowQual"
    priority = 1
```

In this case, if 'record_rule' is set to 'min' and a variant a annotation in the FILTER field that looks like:

```
FILTER
VQSRTrancheBOTH99.90to100.00;LowQual
```  
We would get 'LowQual' from the plugin.