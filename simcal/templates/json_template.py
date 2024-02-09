from template import Template
import json


class JSONTemplate(Template):
    def __init__(self, file=None, string=None):
        if string is None and file is None:
            raise ValueError("JSONTemplate must have a json template document to use")
        elif string is not None and file is not None:
            raise ValueError("JSONTemplate only supports specifying string or file")
        elif file is not None:
            with open(file, 'r') as f:
                self.template = json.load(f)
        else:
            self.template = string
    def fill(self,args: json|dict|list) -> str:
        pass