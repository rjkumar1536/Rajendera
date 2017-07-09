from pyparsing import *
from collections import defaultdict
import pymysql
import logging
import re
import os
VarcharPrecise=1000
BigTables=['newcarpurchaseinquires','pq_clientinfo','newpurchasecities','pqdealeradleads']
Warnings=[]
NotParseable=[]
Dict=defaultdict(list)
#===============================================KEYWORD THAT SHOULDN'T APPEAR IN FUNCTION AND PROCEDURE ====================================
BlockKeyword=["master","slave","alter","show",
            "kill","start","stop","grant","purge","shutdown","flush","lock","restart","start","stop","revoke"]


#=============================================IMPORTANT KEYWORDS THAT WOULD GENERALLY APPEAR IN QUERIES ==============================================
keywords = ["create procedure","select","begin","end","from", "where", "group by",
            "order by", "and", "or","union","union all","alter","drop","inner","left",
            "right","on","temporary","if exists","if not exists","table","stored procedure",
            "column","database","truncate","add","modify","index","unique","primary key",
            "change","rename","integer","numeric","float","decimal","not null","auto_increment",
            "varchar","null","join","delete","update","insert into","values","set","create",
            "int","smallint","tinyint","bigint","mediumint","char","double","date","time","year",
            "timestamp","sql security invoker","default","into","declare","as","datetime","call",
            "case","when","else","then","else if","if","end if","while","end while","is null",
            "is not null","asc","desc","limit","ifnull","nullif","do","unsigned","distinct",
            "having","between","return","returns","create function","in","out","left outer"
            ,"right outer","inout","like","bit","interval","minute","nvarchar","not in","bool"]
[createProcedure,select,_begin,_end,_from, where, groupby, 
orderby, _and, _or,_union,_union_all,_alter,_drop,_inner,_left,
_right,_on,_temporary,_if_exists,_if_not_exists,_table,_procedure,
_column,_database,_truncate,_add,_modify,_index,_unique,_primary_key,
_change,_rename,_integer,_numeric,_float,_decimal,_not_null,_auto_incr,
_varchar,_null,_join,_delete,_update,_insert_into,_values,_set,_create,
_int,_smallint,_tinyint,_bigint,_mediumint,_char,_double,_date,_time,
_year,_timestamp,_sql_security_invoker,_default,_into,_declare,_as,
_datetime,_call,_case,_when,_else,_then,_else_if,_if,_end_if,_while,
_end_while,_is_null,_is_not_null,_asc,_desc,_limit,_if_null,_null_if,_do,
_unsigned,_distinct,_having,_between,_return,_returns,createFunction,_in,
_out,_left_outer,_right_outer,_inout,_like,_bit,_interval,_minute,
_nvarchar,not_in,_bool] = [ CaselessKeyword(word)
        for word in keywords ]
KeywordForSurveillance=[_insert_into,select,_update,_delete,_drop,_truncate]


#================================================GARMMER  OF VERIOUS QUERIES ===============================================================
def GetGrammer(sql):

    option=Optional(_if_exists,'')

    table=column=StoredProcedure=Database=Functionname=Word(alphanums+'_.`')
    tables=Group(delimitedList(table))
    columns = Group(delimitedList(column))
    Size=SizeInt=SizeFraction=Word(nums)
    Sizes=Group(delimitedList(Size))

    functionbody=Forward()
    lpar=Literal("(")
    rpar=Literal(")")
    Comparator=oneOf("= != >= <= <> < >")
    columnVal = (Optional('-','')+Word(nums) | quotedString)
    selectStmt=Forward()

    reserved_words=(_inner|_left|_right|_join|_left_outer|_right_outer|where|_on|_into|_from|_in|_when|_then)
    identifier = ~reserved_words + column 

    #================================================== Arthimatic Expression Tokenizer =============================================================
    expression=Forward()
    expression1=Forward()
    term=Forward()
    expression <<= term + expression1
    factor= (lpar+expression+rpar)|Word(nums)|functionbody|identifier.setResultsName("WhereColumn",listAllMatches=True)|quotedString
    term1=Forward()
    term1 <<= Optional(oneOf("* /")+factor+term1,'')
    term <<= Optional(factor + term1,'')
    expression1 <<= Optional(oneOf("+ -")+ term + expression1,'')
    Value=expression
    #==================================================================================================================================================



    #=============================================================Function and given Argument EX. COUNT(*),MIN(),MAX(),CONCACT() ETC =====================================================================
    functionbody<<=Functionname+(lpar+Optional('*'|delimitedList(ZeroOrMore(functionbody|identifier|Optional('-','')+Word(nums) | quotedString)|expression),'')+rpar)
    





    #==============================================================DATATYPE AND DATATYPESIZE DECLARATION =====================================================================
    DataTypeSize=Optional(lpar+(SizeInt.setResultsName("IntegerPartSize")+','+SizeFraction.setResultsName("FractionPartSize")|Size.setResultsName("DataTypeSize"))+rpar,'')
    DataType=((_int|_varchar|_numeric|_decimal|_float|_double|_integer|_datetime|_tinyint|_smallint|_bigint|_date|_time|_year|_char|_timestamp|_bit|_nvarchar|_bool).setResultsName("Data",listAllMatches=True)+DataTypeSize.setResultsName("DataSize",listAllMatches=True))+Optional(_unsigned,'')+Optional(Optional(_default,'')+(_not_null|_null|(Word(nums) + "." + Word(nums))|Optional('-','')+Word(nums)|(lpar+selectStmt+rpar)),'')+Optional(_auto_incr,'')+Optional(_primary_key,'')
    
    
    #============================================================CALL PROCEDURE STATEMENT ========================================================
    callStmt=_call+StoredProcedure+lpar+delimitedList(Value)+rpar


    whereExpr=Forward()
    #=============================================================CASE STATEMENT USED GENERALLY LIKE(SWITCH CASE)=============================
    caseStmt=_case+Optional(Value,'')+ZeroOrMore(_when+(Group(whereExpr)|Value)+_then+Value)+Optional(_else +Value,'')+_end


    #====================================================SET VALUES OF LOCAL VARIABLES ============================================================
    setStmt=_set+column.setResultsName("ValueName")+Literal('=')+((lpar+(caseStmt|selectStmt)+rpar)|caseStmt|selectStmt|Value)

    

    #=======================================================  RETURNS FUNCTIONS VALUES ==================================================
    Return=_return +(Value)



    #=============================================================RANGE THAT IS USED INSIDE SELECT STATEMENT ==============================================
    Range=lpar+(selectStmt|delimitedList(Value))+rpar



    #=============================================================JOIN CONDITION ==============================================
    joinCond =(Value+Comparator+(Value))
    joinFullCond=Forward()
    JT = ((lpar+joinFullCond+rpar)|joinCond)
    JE1=Forward()
    joinFullCond<<=JT+JE1
    JE1<<=Optional((_and|_or)+JT+JE1,'')
    


    #============================================================WHERE CONDITION USEFUL IN DELETE,UPDATE,SELECT STATEMENTS ============================================================================
    whereCond = (((selectStmt|expression)+ Comparator +((lpar+(caseStmt|selectStmt)+rpar)|expression))|(expression+_between+expression+_and +expression)|(expression+(_in|not_in)+Range)|(expression+(_is_null|_is_not_null))|((expression+_like+columnVal)))
    T = ((lpar+whereExpr+rpar)|whereCond)
    E1 =Forward()
    whereExpr <<= T + E1
    E1 <<= Optional((_and|_or)+T+E1,'')
    #===========================================================================================================================================



    ColumnsDefine=(delimitedList(column.setResultsName("Column",listAllMatches=True)+DataType))
    InsertIntoColumns=Optional((lpar+delimitedList(column).setResultsName("InsertColumns",listAllMatches=True)+rpar),'')
    InsertColumnValues=lpar+delimitedList((caseStmt|Value).setResultsName("ColumnValue"))+rpar

    cond = (Value)+oneOf("= != <= >= < > <>")+(Value)
    yes = (Value)
    no = (Value)
    IF = _if+lpar+cond+','+yes+','+no+rpar

    SetColumnValues=(delimitedList(column.setResultsName("Column",listAllMatches=True)+Literal('=')+((lpar+(caseStmt|selectStmt)+rpar)|caseStmt|selectStmt|IF|Value)))
    DeclarativeSyntax=_declare+DataType+';'

 

    #====================================================SELECT,JOIN,UNION STATEMENT ====================================================================
    ColumnS=delimitedList(ZeroOrMore(((lpar+caseStmt+rpar)|caseStmt)|functionbody|identifier|Word(nums) | quotedString|oneOf("= <= >= < > != + - * /")))
    selectStmt<<=((select+
            ColumnS.setResultsName("Columns") +
            Optional(_into+('*' |columns).setResultsName("Columns"),'')+
            _from +Optional(lpar+selectStmt+rpar,'')+
            table.setResultsName("Table",listAllMatches=True)+Optional((_as+table)|identifier,'')+
            Optional(_into+column,'')+
             ZeroOrMore(Optional((_inner|_left_outer|_right_outer|_left|_right),'').setResultsName("JoinType",listAllMatches=True)+_join+
            (table.setResultsName("JoinTables",listAllMatches=True)|(lpar+selectStmt+rpar))+
            Optional((_as+table)|(identifier),'')+
            Optional(_on+joinFullCond,''))+
            Optional(where + Group(whereExpr), '').setResultsName("where",listAllMatches=True) +
            Each([Optional(groupby + delimitedList((column|functionbody)+Optional(_asc|_desc,'')),'').setDebug(False),Optional(_having +Group(whereExpr) ,'').setDebug(False),
                Optional(orderby + delimitedList((column|functionbody)+Optional(_desc|_asc,'')),'').setDebug(False),Optional(_limit+(columnVal|column),'')
                ]))+Optional((_union_all|_union)+selectStmt,'')).setResultsName("SelectJoinUnion",listAllMatches=True)
   
    #===================================================================================================================================================================
    


    #=======================================================ALTER STATEMENTS ===============================================================================================
    DropColumnStmt=_drop+Optional(_column,'')+column.setResultsName("column").setResultsName("DropColumn")
    ChangeColumnStmt=_change.setResultsName("Change")+column.setResultsName("ColumnFirst")+column.setResultsName("ColumnSecond")+DataType
    RenameTableStmt=_rename.setResultsName("Rename")+table.setResultsName("Tables")
    addDropStmt=(_add|_modify)+Group((_index.setResultsName("Index")|_unique.setResultsName("Unique")|_primary_key.setResultsName("PrimaryKey"))+lpar+(column+ZeroOrMore(','+column)).setResultsName("Columns")+rpar|(Optional(_column,'')+column.setResultsName("Columns")+DataType))
    
    alterStmt=(_alter +_table+table.setResultsName("Table")+ delimitedList(DropColumnStmt.setResultsName("DropColumnStmt",listAllMatches=True)|
        addDropStmt.setResultsName("AddDropStmt",listAllMatches=True)|ChangeColumnStmt.setResultsName("ChangeColmnStmt",listAllMatches=True)|
        RenameTableStmt.setResultsName("RenameTableStmt",listAllMatches=True))).setResultsName("Alter",listAllMatches=True)
    #========================================================================================================================================
   




    #========================================================TRUNCATE STATEMENT =====================================================
    truncateStmt=(_truncate+Optional(_temporary,'').setResultsName("Temporary")+_table+option+table.setResultsName("Table")).setResultsName("Truncate",listAllMatches=True)
    



    #==========================================================DROP STATEMENT =======================================================================================
    dropStmt =(_drop+Optional(_temporary,'').setResultsName("Temporary")+(_table+option+tables.setResultsName("Table"))).setResultsName("Drop",listAllMatches=True)
    




    #======================================================INSERT STATEMENT ==============================================================================================
    insertStmt=(_insert_into+table.setResultsName("Table")+InsertIntoColumns+(_values+InsertColumnValues.setResultsName("ColumnValues")|selectStmt)).setResultsName("Insert",listAllMatches=True)
    



    #=======================================================CREATE STATEMENT ======================================================================================================================================
    createStmt=(_create+Optional(_temporary,'').setResultsName("Temporary")+_table+table.setResultsName("Table")+((lpar+(selectStmt|ColumnsDefine.setResultsName("ColumnsDetails"))+rpar)|((selectStmt|ColumnsDefine)))).setResultsName("Create",listAllMatches=True)
    



    #=====================================================UPDATE STATEMENT ================================================================================================================
    updateStmt=(_update+table.setResultsName("Table")+_set+(SetColumnValues)+Optional(where+ Group(whereExpr), '').setResultsName("where")).setResultsName("Update",listAllMatches=True)
    



    #=====================================================DELETE STATEMENT ===================================================================================================
    deleteStmt=(_delete+_from+table.setResultsName("Table")+Optional(where + Group(whereExpr), '').setResultsName("where")).setResultsName("Delete",listAllMatches=True)
    



    #================================================SELECT STATEMENT WITH FUNCTION =========================================================================
    callWithSelect=select+functionbody+_into+column

    ifStmt=Forward()
    WhileStmt=Forward()
    statementList=(setStmt|updateStmt|  selectStmt|callWithSelect|insertStmt|truncateStmt|deleteStmt|alterStmt|createStmt|callStmt|dropStmt|ifStmt|WhileStmt)
#======================================================IF ELSEIF ENDIF STATEMENT  ================================================

    ifCondition=(Group(whereExpr))|(selectStmt)
    ifStmt<<=((_if_exists|_if_not_exists|_if)+(ifCondition|(lpar+ifCondition+rpar))+_then
    +(ZeroOrMore(statementList+';')|(Return+';'))
    +ZeroOrMore(_else_if+((lpar+ifCondition+rpar)|ifCondition)+_then
    +(ZeroOrMore(statementList+';')|(Return+';')))+Optional(_else+(ZeroOrMore(statementList+';'))|(Return+';'),'')+_end_if).setResultsName("IfStmt")




#=======================================================WHILE ENDWHILE STATEMENT ================================================================================================================
    WhileStmt<<=_while+Group(whereExpr)+_do+ZeroOrMore((setStmt|ifStmt.setResultsName("IfStmt")|callStmt|insertStmt|createStmt|dropStmt|deleteStmt|alterStmt|truncateStmt|selectStmt|updateStmt|WhileStmt)+';')+_end_while




#=================================================PROCEDURE AND FUNCTION STANDARD STRUCTURE =======================================================================================================
    InputParameters=delimitedList(Optional((_in|_out|_inout),'')+column+DataType)
    DeclarativeSyntax=(_declare+column+DataType+';')
    createProcedureStmt=createProcedure + StoredProcedure.setResultsName("Procedure")+lpar+Optional(InputParameters.setResultsName("Input"),'')+rpar+Optional(_sql_security_invoker,'').setResultsName("SQLSECURITY")+_begin+ZeroOrMore(DeclarativeSyntax).setResultsName("Declare")+ZeroOrMore(statementList+';')+_end+Optional(';','')
    createfunctionStmt=createFunction + Functionname.setResultsName("Function")+lpar+Optional(InputParameters.setResultsName("Input"),'')+rpar+_returns+DataType+Optional(_sql_security_invoker,'').setResultsName("SQLSECURITY")+_begin+ZeroOrMore(DeclarativeSyntax).setResultsName("Declare")+ZeroOrMore((statementList|Return)+';')+_end+Optional(';','')



#=================================================RETURN GRAMMER OF SELECTIVE PARSER ========================================================================================================================
    if "function" in sql.lower():
        return createfunctionStmt
    else:
        return createProcedureStmt




################################            SHOW INDEXING ON GIVEN COLUMN ###########################################################
def ShowIndexOnColumn(database,table,column,local_database_host = '172.16.0.26',local_user = 'cwadmin',local_password = 'cwadmin',DATABASE_PORT = 3306):
    # where table_name.col2 != table_name.col and table_name.col2 <= table_name.col or table_name.col3 in (1,6) and table_name.col4 between col1 and col2 
    # <-> table_name.col.. contain Indexing or not ??
    master_database=database
    # This function is checking whether the table name is associated with database.
    # if it is There split it and connect to that database and if not present than default database is used.
    # Same  for Tables, if table name is appearing in  the column name then extarct it and used it to show indexing on that column itself otherwise take from database.table/table from above statements
    if '.' in table:
        tabledatabase,table=table.split('.')
        master_database=tabledatabase
    conn = pymysql.connect(host=local_database_host, port=DATABASE_PORT, user=local_user, passwd=local_password, db=master_database)
    cur = conn.cursor()
    if '.' in column:
        selecttable,column=column.split('.')
    # After extarcting column name and table name
    query="SHOW INDEX FROM %s where Column_name = '%s';" %(table,column)
    cur.execute(query)   
    rows = cur.fetchall()
    conn.close()
    if len(rows)>0:
        return True;
    return False;

################################# LOGS DETAILS OF WARNING AND ERRORS ######################################################################
def logWarning(warning,file):
    # list and log the warning if they are not given before
    if warning not in Warnings:
        Dict[file].append(warning)
        logger.debug(warning)
        Warnings.append(warning)

def get_Logger(loggerName,fileName):
    logger = logging.getLogger(loggerName)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(fileName)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger
logger = get_Logger("Database","C:\Users\\rajender.kumar\Block.log")

def sqlsecurityStmtWarning(result,rst,FuncPro,file):
    # declare varname datatypedeclarartion
    # sql security invoker
    try:
        if not result.SQLSECURITY:
            WarningofUndefinedSqlSecurity='Warning :: Sql Secuirty Invoker is not defined in %s %s'%(FuncPro,rst)
            logWarning(WarningofUndefinedSqlSecurity,file)
    except:
        pass
def whereClauseWarning(database,result,file,rst,FuncPro,table,StmtType):
    # Do result.dump() in Review() to get to know structre/formatting of the parsed output.
    checker=0
    if StmtType=="SelectJoinUnion":
       checker=len((result.where)[0])
    else:
        checker=len((result.where))
    if checker>1:
        if StmtType=="SelectJoinUnion":
            whereClause=((result.where)[0][1]).WhereColumn
        else:
            whereClause=((result.where)[1]).WhereColumn
        for name in range(0,len(whereClause)):
            if not ShowIndexOnColumn(database,table,whereClause[name][0]):
                WarningofIndex="Error :: %s %s ,In %s Statement Table %s nO Indxing on Column %s" % (FuncPro,rst,StmtType,table,whereClause[name][0])
                logWarning(WarningofIndex,file)
    else:
        WarningOfWhere="Warning In %s %s There is No Where Clause In %s Statement of Table %s"%(FuncPro,rst,StmtType,table)
        logWarning(WarningOfWhere,file)

def selectAndJoinStmtWarning(database,result,rst,FuncPro,file):
    # select a,b,c,d from table_name;
    # select 1 from table_name
    # select * from table_name

    ''' select var1,var2,var3..., 
    from table_name table_aliases
    inner join table_name aliases on table_name.col = Ttable_name.col and table_name.col=table_name.col
    left outer join table_name table_aliases on table_name.col = table_name.col and table_name.col = table_name.col and col  in (1,6) blah..blah
    right join table_name BIGtable_aliases on table_name.col = table_name.col and table_name.col = table_name.col and col in  (1,6)
    join table_name table_aliases on BIGtable_name.col = table_name.col and table_name.col = table_name.col and col between colval1 and colval2
    right outer join table_name table_aliases on table_name.col = table_name.col and table_name.col = table_name.col
    where table_name.col1 = table_name.col2
    '''
    select=""
    try:
        if result.SelectJoinUnion:
            select=result.SelectJoinUnion
        for tab in range(0,len(select)):
            table=(select[tab].Table)[0]
            if select[tab].JoinTables:
                tableofjoin=select[tab].JoinTables
                joiner=select[tab].JoinType
                if len(tableofjoin)>4:
                    WarningofJoin="Alert In %s %s,Join Statement Of table %s  More Than 4 Join is Applied"%(FuncPro,rst,table)
                    logWarning(WarningofJoin,file)
                for joinitem in range(0,len(tableofjoin)):
                    if joiner[joinitem]=='left' or joiner[joinitem]=='right':
                        WarningofJoinType="Warning %s Join is applied on table %s"%(joiner[joinitem],tableofjoin[joinitem])
                        logWarning(WarningofJoinType,file)
                    if tableofjoin[joinitem] in BigTables:
                        WarningOfBigTables="Alert In %s %s Join is Applied on BigTable %s"%(FuncPro,rst,tableofjoin[joinitem])
                        logWarning(WarningOfBigTables,file)    
            whereClauseWarning(database,select[tab],file,rst,FuncPro,table,"SelectJoinUnion")

    except:
        pass

def sizeStmtWarning(result,rst,FuncPro,file):

    # in/out/inout varname varchar(2000)
    # in/out/inout varname decimal/numeric(18,0)

    # declare varname varchar(2000)
    # declare varname decimal/numeric(18,0)
    InputData=""
    DeclareData=""
    InputDataSize=""
    DeclareDataSize=""
    try:
        InputData=result.Input.Data
        InputDataSize=result.Input.DataSize
    except:
        pass
    try:
        DeclareData=result.Declare.Data
        DeclareDataSize=result.Declare.DataSize
    except:
        pass
    for var in range(0,len(InputData)):
        if InputDataSize[var].DataTypeSize:
            if InputData[var]=="varchar"  and int(InputDataSize[var].DataTypeSize)>VarcharPrecise:
                WarningOfDefinedDataSize='Error :: in Input Data of %s %s , Size of Datatype Varchar is More Than Required varchar(%s)'%(FuncPro,rst,InputDataSize[var].DataTypeSize)
                logWarning(WarningOfDefinedDataSize,file)
        if InputDataSize[var].IntegerPartSize:
            if (InputData[var]=="numeric" or InputData[var]=="decimal") and int(InputDataSize[var].FractionPartSize)==0:
                WarningOfDefinedDataSize='Error :: in Input Data of %s %s , Size of Datatype %s is defined as %s(%s,%s)'%(FuncPro,rst,InputData[var],InputData[var],InputDataSize[var].IntegerPartSize,InputDataSize[var].FractionPartSize)
                logWarning(WarningOfDefinedDataSize,file)
    for var in range(0,len(DeclareData)):
        if DeclareDataSize[var].DataTypeSize:
            if DeclareData[var]=="varchar" and  int(DeclareDataSize[var].DataTypeSize)>VarcharPrecise:
                WarningOfDefinedDataSize='Error :: in Declared Data of %s %s , Size of Datatype Varchar is More Than Required varchar(%s)'%(FuncPro,rst,DeclareDataSize[var].DataTypeSize)
                logWarning(WarningOfDefinedDataSize,file)
        if DeclareDataSize[var].IntegerPartSize:
            if (DeclareData[var]=="numeric" or DeclareData[var]=="decimal")  and int(DeclareDataSize[var].FractionPartSize)==0:
                WarningOfDefinedDataSize='Error :: in Declared Data of %s %s , Size of Datatype %s is defined as %s(%s,%s)'%(FuncPro,rst,DeclareData[var],DeclareData[var],DeclareDataSize[var].IntegerPartSize,DeclareDataSize[var].FractionPartSize)
                logWarning(WarningOfDefinedDataSize,file)

def updateStmtWarning(database,result,rst,FuncPro,file):
    # update table table_name set col1=colval,col2=colval2,col3=colval2+4;
    update=""
    try:
        if result.Update:
            update=result.Update
        for updates in range(0,len(update)):
            table=(update[updates].Table)[0]
            whereClauseWarning(database,update[updates],file,rst,FuncPro,table,"Update ")
    except:
        pass

def insertStmtWarning(result,rst,FuncPro,file):
    # insert into table_name values ('val1','val2','val3','val4','val5','val6');
    insert=""
    try:
        if result.Insert:
            insert=result.Insert
        for inserter in range(0,len(insert)):
            table=(insert[inserter].Table)[0]
            insertcolumns=insert[inserter].InsertColumns
            if not len(insertcolumns):
                WarningofInsertColumns="Alert In %s %s Query Insert On table %s there  is No column Specified"%(FuncPro,rst,table)
                logWarning(WarningofInsertColumns,file)
    except:
        pass

def deleteStmtWarning(database,result,rst,FuncPro,file):
    # delete from table_name;
    delete=""
    try:
        if result.Delete:
            delete=result.Delete
        for deletion in range(0,len(delete)):
            table=(delete[deletion].Table)[0]
            whereClauseWarning(database,delete[deletion],file,rst,FuncPro,table,"Delete ")
    except:
        pass

def dropStmtWarning(result,rst,FuncPro,file):
    # drop table if exists table1_name,table2_name,...,..;
    drop=""
    try:
        if result.Drop:
            drop=result.Drop
        for dropper in range(0,len(drop)):
            if not drop[dropper].Temporary:
                WarningofDrop="warning In %s %s Drop Tables %s are not Temporary"%(FuncPro,rst,drop[dropper].Table)
                logWarning(WarningofDrop,file)
    except:
        pass

def truncateStmtWarning(result,rst,FuncPro,file):
    # truncate table if exists table_name
    truncate=""
    try:
        if result.Truncate:
            truncate=result.Truncate
        for trunc in range(0,len(truncate)):
                if not truncate[trunc].Temporary:
                    WarningofTruncate="warning In %s %s Truncate  Tables %s are not Temporary"%(FuncPro,rst,truncate[trunc].Table)
                    logWarning(WarningofTruncate,file)
    except:
        pass
def createStmtWarning(result,rst,FuncPro,file):
    create=""
    try:
        if result.Create:
            create=result.Create
        for stmt in range(0,len(create)):
                if not create[stmt].Temporary:
                    WarningofCreate="warning In %s %s Create  Tables %s are not Temporary"%(FuncPro,rst,create[stmt].Table)
                    logWarning(WarningofCreate,file)
    except:
        pass
def alterStmtWarning(result,rst,FuncPro,file):
    # alter table table_name,add column varchar(2000),drop column column_name,add index(b,c,d),add primary key(b,c),change b c varchar(20);
    alter=""
    try:
        if result.Alter:
            alter=result.Alter
    except:
        pass

def QueryReviewer(database,result,file,resultFunPro):
    # FunPro -------------------> Function Or Procedure
    FuncPro=""
    try:
        if resultFunPro.Function:
            rst=resultFunPro.Function
            FuncPro="Function"
        else:
            rst=resultFunPro.Procedure
            FuncPro="Procedure"
        sizeStmtWarning(result,rst,FuncPro,file)
        sqlsecurityStmtWarning(result,rst,FuncPro,file)
        selectAndJoinStmtWarning(database,result,rst,FuncPro,file)
        updateStmtWarning(database,result,rst,FuncPro,file)
        insertStmtWarning(result,rst,FuncPro,file)
        deleteStmtWarning(database,result,rst,FuncPro,file)
        dropStmtWarning(result,rst,FuncPro,file)
        truncateStmtWarning(result,rst,FuncPro,file)
        createStmtWarning(result,rst,FuncPro,file)
        alterStmtWarning(result,rst,FuncPro,file)
    except:
        pass

######################### PARSE THE MYSQL QUERY USING SELECTED PARSER ##################################################
def Review(database,sql,file):
    try:
        stmt = GetGrammer(sql)
        result = stmt.parseString(sql,parseAll=False)
        # print result.dump()
        QueryReviewer(database,result,file,result)     
    except:
        # If parser not able to recognize the given pattern than append it to not parsable list of files
        NotParseable.append(file)
        print NotParseable
        pass
# # 
############################# READ MYSQL QUERIES ############################################################################
def main(database,file):
    #=====================For Better Undersatnding for Parsing structure, Do result.Dump() It will show the structre of underlying parsing tokens ======================

    # Change Argument given in the main function if one file at a time than-->'file' else 'foldername'
    #================================================Read Bulk of files from Given Argument('foldername')========================
    # for root,dirs,files in os.walk(folderlocation):
    #     for file in files:
    #         if file.endswith(".sql"):
    #             file=os.path.join(root,file)
    #             with open(file) as f:
    #                 sql =""
    #                 for line in f:
    #                     sql=sql+line
    #                     sql = re.sub(re.compile("#.*|--.*",re.DOTALL ) ,"" ,sql)
    #             sql = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,sql)
    #             sql = re.sub(re.compile(".*CREATE.*PROCEDURE",re.DOTALL),'CREATE PROCEDURE',sql)
    #             sql = re.sub(re.compile(".*CREATE.*FUNCTION",re.DOTALL),'CREATE FUNCTION',sql)
    #             sql=' '.join(sql.split())
    #             blacklist=0
    #             Splitter=[]
    #             Splitter=sql.split()
    #             for BlockerOn in BlockKeyword:
    #                 if BlockerOn in Splitter:
    #                     WarningFromBlocker="%s Keyword found in file %s"%(BlockerOn,file)
    #                     logger.debug(WarningFromBlocker)
    #                     blacklist=1
    #             if not blacklist:
    #                 Review(sql,file)
    # print len(NotParseable)
    #=================================================================================================================================

    #============================================Read One File At a time =================================================================
    with open(file) as f:
        sql =""
        for line in f:
            sql=sql+line
            sql = re.sub(re.compile("#.*|--.*",re.DOTALL ) ,"" ,sql)
    sql = re.sub(re.compile("/\*.*?\*/",re.DOTALL ) ,"" ,sql)
    sql = re.sub(re.compile(".*CREATE.*PROCEDURE",re.DOTALL),'CREATE PROCEDURE',sql)
    sql = re.sub(re.compile(".*CREATE.*FUNCTION",re.DOTALL),'CREATE FUNCTION',sql)

    sql=' '.join(sql.split())
    blacklist=0
    Splitter=[]
    Splitter=sql.split()
    # Splitter list contains the list of word that are separated by whitespace
    # check if in splitter block keyword is present or not.
    for BlockerOn in BlockKeyword:
        if BlockerOn in Splitter:
            WarningFromBlocker="%s Keyword found"%(BlockerOn)
            logWarning(WarningFromBlocker,file)
            blacklist=1
    # If blockkeyword is Not present than Parse it otherwise return with list of block keywords that are appearing.
    if not blacklist:
        Review(database,sql,file)
    #==========================================================================================================================================
def GetInput(args):
    global Dict
    Dict=defaultdict(list)
    for database,scripts in args.iteritems(): 
        for script in scripts:
            main(database,script)
    return Dict
