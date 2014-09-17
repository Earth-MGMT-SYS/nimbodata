"""Module implements text types."""
# Copyright (C) 2014  Bradley Alan Smith

import json

from . import *


class Text(Datatype):
    
    from_literal = str
        
class Json(Datatype):
    
    from_literal = lambda x: json.dumps(x)
