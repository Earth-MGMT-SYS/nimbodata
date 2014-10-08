
from prototype import BinaryExpression

class Join(object):
    """Represent a Nimbodata query join expression."""
    
    def __init__(self,target,on=None):
        
        if on is None:
            try:
                self.target, on = target
            except KeyError:
                self.target = target
                on = None
        else:
            self.target = target
            
        if on is not None:
            self.on = BinaryExpression(on)
        else:
            self.on = None
        
        self.data = (self.target,self.on)
