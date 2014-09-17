.. _select:

***********
Select
***********

Query Principles
-----------------

The query language in nimbodata is driven by a few primary considerations:

-  Terseness: use Pythonic/Mathematical notation and JSON-like structures
   rather than chaining method calls where possible.
-  Flexibility: since nimbodata is a distributed system, support exists for 
   advanced overriden operators in Python, as well a string-clause or
   JSON/string parser.
-  Beyond SQL: be inspired by the power of SQL, but do not be limited by it.

An example of a minimal query in Python is::

    >>> table = cloud.Database('spam').Table('eggs')
    >>> table.select()

While a more complex (contrived) query would look like (all of the variables in
the parameters would be column objects, easy to get)::

    >>> a, b = from_table.Column('a'), from_table.Column('b')
    >>> join_target = cloud.Database('SomeOtherDB').Table('SomeOtherTable')
    >>> join_fk = join_target.Column('fk') # The Foreign Key Column
    >>> join_val = join_target.Column('val') # The Interesting Value
    >>> results = cloud.select(
    ...     from_table,
    ...     cols = [b,avg(join_val)],
    ...     where = ((a < b) && (b != 2)),
    ...     join = a == join_fk,
    ...     group_by = b,
    ...     order_by = a,
    ...     limit = 3
    ... )

Which could also be represented as a JSON Payload to ./select::

    {
        "from":"from_table",
        "cols":["b","avg(join.val)"],
        "where":["a < b","b != 2"],
        "join":"a == join.fk",
        "group_by":"b",
        "order_by":"a",
        "limit":3
    }

Or the entities could be represented by the objid, but since those are 36 chars
of nonsense, they're not too interesting to look at.

Query A Single Relation
-------------------------

In the case where we want to query a single relation (be it a table, view) 
we can do it directly via the relation object as shown in the first example 
above.  A more complete example would be::

    >>> db = cloud.Database('MyDatabase')
    >>> table = db.Table('MyTable')
    >>> a, b, c = table.columns()
    >>> result = table.select() # SELECT * FROM "MyDatabase"."MyTable"
    >>> result = table.select([a,b]) # SELECT A, B FROM "MyDatabase"."MyTable"
    
    >>> result = table.select([a,b],a < b)
    >>> other_result = table.select(['a','b'],'a < b')
    >>> assert result == other_result
    
    
