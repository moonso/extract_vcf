
class Plugin(object):
    """Class for holding information about a plugin"""
    def __init__(self, name, field, data_type, separators, info_field=None, 
                category=None, csq_field=None):
        super(Plugin, self).__init__()
        self.name = name
        self.field = field
        self.data_type = data_type
        self.separators = separators
        
        self.info_field = info_field
        self.category = category
    
    
    def get_annotation(self):
        """
        Return the annotation found in the field specified for plugin.
        """
        annotations = []
        value = None
        if self.field == 'INFO':
            pass
        
    def get_value(self, variant):
        """
        Return the value as specified in plugin
        """
        annotations = []
        value = None
        if self.field == 'INFO':
            pass
            # if self.info_field == 'CSQ':
            #     vep_dict = variant.get('vep_info', {})
            #     for allele in vep_dict:
            #         for vep_annotation in vep_dict[allele]:
            #             annotation = vep_annotation.get(self.csq_key, None)
            #             if annotation:
            #                 annotations.append(annotation)
        
                        
        value = variant[self.field]
        return value
    
    def __repr__(self):
        return "Plugin(name={0},field={1},data_type={2},separators={3})".format(
            self.name, self.field, self.data_type, self.separators
        )

