
from prototype import BinaryExpression, TwoValExpression

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
            try:
                self.on = BinaryExpression(on)
            except ValueError:
                print on
                self.on = TwoValExpression(on['fname'],*on['args'])
            except TypeError:
                self.on = on
        else:
            self.on = None
        
        self.data = (self.target,self.on)

class LeftOuterJoin(Join):
    """Left Outer Join"""
    
class RightOuterJoin(Join):
    """Right Outer Join"""
    
class FullOuterJoin(Join):
    """Full Outer Jacket"""
