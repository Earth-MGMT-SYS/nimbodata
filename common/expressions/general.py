
from . import *

class GeneralFunction(Function):
    """Base class for any general function in PostgreSQL."""

class unique(GeneralFunction):
    """Return only the unique values from a scalar."""
    
    def __init__(self,col):
        self.fargs = [col]

class AS(GeneralFunction):
    """Modify the name of the returned value."""

    def __init__(self,col,newname,newalias=None):
        self.info = {
            'col':col,
            'newname':newname,
            'newalias':newalias
        }
        
    @property
    def data(self):
        return self.info

class Union(GeneralFunction):
    """Combine two queries"""

class count(GeneralFunction):
    """Return the number of values in the scalar."""
