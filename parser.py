from pyparsing import CaselessKeyword,Dict, delimitedList, Each, Forward, Group,Optional, Word, alphas,alphanums, nums, oneOf, ZeroOrMore, quotedString,OneOrMore
 
keywords = ["create procedure","select","begin","end","from", "where", "group by", "order by", "and", "or","union","union all"]
[createProcedure,select,_begin,_end,_from, where, groupby, orderby, _and, _or,_union,_union_all] = [ CaselessKeyword(word)
        for word in keywords ]
 
table = column = Word(alphas)
spname=Word(alphas)
tables=Group(delimitedList(table))
columns = Group(delimitedList(column))
columnVal = (nums | quotedString)
 
whereCond = (column + oneOf("= != < > >= <=") + columnVal)
whereExpr = whereCond + ZeroOrMore((_and | _or) + whereCond)

selectStmt = (select +
        ('*' | columns).setResultsName("columns") +
        _from +
        tables.setResultsName("tables") +
        Optional(where + Group(whereExpr), '').setResultsName("where").setDebug(False) +
        Each([Optional(groupby + columns("groupby"),'').setDebug(False),
            Optional(orderby + columns("orderby"),'').setDebug(False)
            ])
        )
spStmt = (createProcedure +spname+_begin+selectStmt+_end)
unionStmt=Forward().setName("select statement")
unionStmt<<selectStmt +OneOrMore((_union|_union_all) +selectStmt)
def log(sql, parsed):
    # print "-------------------------------------------------------"
    print sql
    print parsed.tables
    print parsed.columns
    print parsed.where
    # print parsed.groupby
    # print parsed.orderby
    # print parsed.unionStmt
    # print "-------------------------------------------------------"
 
sqls = [
        # """select * from users where username='johnabc'""",
        # """SELECT * FROM users WHERE username='johnabc'""",
        """SELECT * FRom users union select add from customers union select new from rajendera""",
        # """SELECT * FRom USERS""",
        # """SELECT * FROM users WHERE username='johnabc' or email='johnabc@gmail.com'""",
        # """SELECT id, username, email FROM users WHERE username='johnabc' order by email, id""",
        # """SELECT id, username, email FROM users WHERE username='johnabc' group by school""",
        # """SELECT id, username, email FROM users WHERE username='johnabc' group by city, school order by firstname, lastname union select * from jodhpuri """
        ]
 
for sql in sqls:
    try:
        result= unionStmt.parseString(sql)
        print result
        print result[0]['tables']
        print result['columns']
        # log(sql, unionStmt.parseString(sql))
        # log(sql,selectStmt.parseString(sql))
    except:
        pass
