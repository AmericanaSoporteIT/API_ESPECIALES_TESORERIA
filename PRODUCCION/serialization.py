from decimal import *

def toJsonDump(statement):
    data = data = [ 
        (round(value,6) if isinstance(value, Decimal) else value 
                if isinstance(value, int) else str(value).strip() 
                    for value in row
        ) for row in statement.fetchall()
    ]
    columns = [column[0] for column in statement.description]
    res = []
    for row in data:
        res.append(dict(zip(columns, row )))
    return res



def toStringAll(statement):
    data = [tuple(str(item).strip() for item in t) for t in statement.fetchall()]
    columns = [column[0] for column in statement.description]
    res = []
    for row in data:
        res.append(dict(zip(columns, row )))
    return res



def serializer(sql_statement):
    columns = [column[0] for column in sql_statement.description]
    results = []
    for row in sql_statement.fetchall():
        results.append(dict(zip(columns, row )))
    return results

def CamelCase(word):
        return ''.join(x.capitalize() or ' ' for x in word.split(' '))

        