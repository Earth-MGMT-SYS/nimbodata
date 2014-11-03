
from . import *

class GeoFunction(Function):
    """Base class for any GeoFunction in PostgreSQL."""

    

# SCALAR


# VALUE
class simplify(GeoFunction):
    """Reduce the number of verticies in a polygon or line."""
