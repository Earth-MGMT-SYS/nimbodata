"""Module implements Exceptions required by various aspects in the core."""
# Copyright (C) 2014  Bradley Alan Smith

class InvalidMethod(Exception):
    """Raised when an illegal method name is called"""
    strerror = '!ERROR! 000: Sorry, you requested an illegal method name.'

class RelationExists(Exception):
    """Database already exists in the registry."""
    strerror = '!ERROR! 001: Sorry, the relation already exists'
    
class RelationDoesNotExist(Exception):
    """Relation does not exist"""
    strerror = '!ERROR! 002: Sorry, the relation does not exist'

class TableExists(Exception):
    """Table/user combo already exists in the database."""
    strerror = '!ERROR! 002: Sorry, the table already exists'
    
class TableDoesNotExist(Exception):
    """Table does not exist in the database."""
    strerror = '!ERROR! 003: Sorry, the table does not exist'

class ViewDoesNotExist(Exception):
    """Table does not exist in the database."""
    strerror = '!ERROR! 003: Sorry, the table does not exist'
    
class DatabaseDoesNotExist(Exception):
    """Database does not exist."""
    strerror = '!ERROR! 004: Sorry, the database does not exist'
    
class PrimaryKeyError(Exception):
    """The insert violates a primary key condition."""

class ValueRequired(Exception):
    """Null value where not null required."""
    
class NoFromTable(Exception):
    """Query did not specify a table to query from."""

class BadData(Exception):
    """Bad data."""

class PermissionDenied(Exception):
    """User does not have permission."""

class NoResults(Exception):
    """There's no results for this query"""

class IntegrityError(Exception):
    """Operation would violate constraint"""
    strerror = '!ERROR! 003: Integrity Error'

class InvalidFunction(Exception):
    """Attempted to call SQL function not identified in allowed_funcs"""

class DataError(Exception):
    """Data and action are incompatable."""

class NotAuthorized(Exception):
    strerror = '!ERROR! 042: Not Authorized'

class QueryError(Exception):
    """The query is malformed.
    
    For instance it requests columns not specified in from or join.
    
    """
