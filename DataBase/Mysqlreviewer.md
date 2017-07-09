                                                      CodeReviewer 1.0


**Contents**   

**1.Objective  
2.Tools installation  
3.Introduction of Tools  
4.Description of Code Reviewer  
5.Results  
6.References**

**1. Objective:**     

To make a code reviewer such that without executing the sql statement it should give Notification about block keywords and also certain mysql statements.  

**Main Objectives :**    

(1)  wherever where clause is present check indexing on associated columns.  
(2) Select ,Delete,Update statements should appear with where clause   
(3) Join statement shouldn’t contain Left|Right Join  
(4) There Shouldn’t be any Join on Big Tables List of Big tables will be provided.  
(5) If there are More than 4 Join in a select statement  Then log Warnings.  
(6) Insert statements Contains columns for making entries of respective values.  
(7) Drop,Truncate  statements on allowed when Tables are Temporary  
(8) If size of any Declared column is meaningless than give warnings.Examples:varchar(200000),Decimal(20,0)  
(9) Alter statement is not permitted to add column,drop column  
(10) Delete statements should appear with where clause   
(11) Update statements should appear with where clause   

  

**Block Keywords are :**  

		"master","slave","alter","show"  "kill","start","stop","grant","purge","shutdown","flush","lock","restart","start","stop","revoke"

**Note:**  

These block keywords are Detected At the starting of code.And appearance of any out of them will Lead to abort the code with list   of all block keywords that are present in sql procedure/function       
That’s why at the starting of code we are splitting the  code and checking if block keyword is present or not.   




**2. Tools Installation :**    

To meet above objective and Requirements Parsing based approach is used.  
This is Python Implementation using Pyparser  
```python setup.py install    ```

```From pyparsing import  ```

**3. Introduction to Tools:**  

pyparsing contains  functions and their attributes to develop complex parsers.  
Two methods are used for parsing input string setParseAction() and parseString().   

Above methods gives different different parsing structure after scanning input string.    
SetResultsName is used for naming the grammar statements.    
SetDebug() is used for identify which token is matching with given grammar.  
Dump() is used to show structure of parse string with label.


**4. Description of Code Reviewer:**   

**Grammar Type:**    

**1. Select**    

	ColumnS=delimited List(ZeroOrMore(((lpar+casecolumn+rpar)|casecolumn)|functionbody|identifier|Word(nums) | quotedString|oneOf("=         <= >= <   > != + - * /")))

	reserved_words=(_inner|_left|_right|_join|_left_outer|_right_outer|where|_on|_into|_from|_in)
	
	identifier = ~reserved_words + column 

	whereCond = (((expression)+ Comparator +((lpar+(caseStmt|selectStmt)+rpar)|expression))|(expression+_between+expression+_and 
	
	+expression) |(expression+(_in|not_in)+Range) |(column.setResultsName("WhereColumn",listAllMatches=True)+   

	(_is_null|_is_not_null)) |((column.setResultsName("WhereColumn",listAllMatches=True)) 
	
	+_like+columnVal))

	whereExpr=Forward()      
	T = ((lpar+whereExpr+rpar)|whereCond)      
	E1 =Forward()      
	whereExpr <<= T + E1    
	E1 <<= Optional((_and|_or)+T+E1,'')    

	functionbody<<=Functionname+(lpar+Optional(delimitedList(ZeroOrMore(functionbody|identifier|Optional('-','')+Word(nums) |
	
	quotedString)|expression),'')+rpar)  

	columnVal = (Optional('-','')+Word(nums) | quotedString)  

	table=column=StoredProcedure=Database=Functionname=Word(alphanums+'_.`')  

 **Above Variables are used in below select grammer**  
 

		selectStmt<<=((select+  
		
		ColumnS.setResultsName("Columns") +  
		
		Optional(_into+   ('*' |columns).setResultsName("Columns"),'')+  
		
		_from +    Optional(lpar+selectStmt+rpar,'')+  
		
		table.setResultsName("Table",listAllMatches=True)+Optional((_as+table)|identifier,'')+  
		
		Optional(_into+column,'')+  
		ZeroOrMore(Optional((_inner|_left_outer|_right_outer|_left|_right),'').setResultsName("JoinType",listAllMatches=True)+_join+  
		
		(table.setResultsName("JoinTables",listAllMatches=True)|(lpar+selectStmt+rpar))+  
		
		Optional((_as+table)|(identifier),'')+  
		
		Optional(_on+ColumnS,''))+  

		Optional(where + Group(whereExpr), '').setResultsName("where",listAllMatches=True) +
		
		Each([Optional(groupby +        (column|functionbody)+Optional(_asc|_desc,''),'').setDebug(False),Optional(_having
		
		+Group(whereExpr) ,'').setDebug(False),  
		
		Optional(orderby + (column|functionbody),'').setDebug(False),Optional(_desc|_asc,''),Optional(_limit+ 
		
		(columnVal|column),'')]))+  

		Optional((_union_all|_union)+selectStmt,'')).setResultsName("SelectJoinUnion",listAllMatches=True)   

**Statement Types :**    

**(1) Statement and matching part of the select statement grammar**     

**Examples**  

	select+ 
	delimitedList(column)+
	Optional(_into+columns).setResultsName("Columns"),'')+ 
	_from+
	table.setResultsName("Table",listAllMatches=True)+
	Optional(identifier,'')+

	Optional((_inner),'').setResultsName("JoinType",listAllMatches=True)+
	_join+
	(table.setResultsName("JoinTables",listAllMatches=True))+
	Optional((identifier),'')+
	Optional(_on+ColumnS,'')+
	Optional(where + Group(whereExpr), '').setResultsName("where",listAllMatches=True) +Optional(_limit+(columnVa,'')  ]))


**Examples** 

	select
	p.inqptcategoryid ,
	cwctmap.packageenddate,
	i.ispremium
	into 
	v_packagetype,
	v_packageexpirydate ,
	v_ispremium
	from cwctdealermapping cwctmap  inner join packages p  on cwctmap.packageid=p.id
	inner join inquirypointcategory i  on p.inqptcategoryid=i.id  where cwdealerid=v_dealerid limit 1;



**(2) Statement and matching part of the select statement grammar**   




**Examples** 



	select concat(hosturl , directorypath , logourl) into v_certifiedlogourl
	from classified_certifiedorg 
	where id = v_certificationid;

**(3)**  
**Examples**    

	select s.id into v_inquiryid
	from sellinquiries s  
	inner join carphotos c  
	on c.inquiryid = s.id 
	where s.tc_stockid = v_stockid 
	and s.sourceid = v_sourceid 
	and c.tc_carphotoid = v_tc_carphotoid;



**(4) Case statement appearing inside select query**


**Examples**    

	select count(id)
	into v_photocount
	from carphotos 
	where inquiryid = v_inquiryid
	and isdealer = (
	case 
	when v_sellertype = 1  then 1
	else 0
	end	)
	and isactive = 1
	and isapproved = 1;


**(5) Function for returning value and putting back into a variable**  


 **Examples**  
 
		select CalculateSortScoreForIndividual(v_ispremium, v_score, null, v_photocount) into v_SortScoreNew;



**(6)   If Inside function body neither number,identifier,functionname,and neither a expression   occurs Than**



	functionbody<<=Functionname+(
	Lpar+
	Optional(delimitedList
	(ZeroOrMore(
	Functionbody|
	Identifier|
	Optional('-','')
	+
	Word(nums)),'')
	+rpar)

**Examples**   

	select distinct cfl.custemail, cfl.custmobile, cfl.inquiryid, cfl.custname, cfl.issenttosource, si.sourceid, cfl.isverified, cfl.id, si.dealerid, si.tc_stockid
	from  classifiedleads cfl 
	inner join sellinquiries si  on cfl.inquiryid = si.id and cfl.sellertype = '1'  -- sellertype is varchar 
	inner join ct_addonpackages cap  on si.dealerid = cap.cwdealerid 
	where cap.addonpackageid = 101 and cfl.issenttosource = 0 and date_add(now(),interval -15 minute) > entrydatetime 
	and cap.isactive=1;


**(7) Select column are like this than :**  
 **Examples**  

		ColumnS=delimitedList(
		ZeroOrMore(((
		lpar+
		Casecolumn+
		rpar)|casecolumn)|
		Functionbody|
		identifier|
		Word(nums)| 
		quotedString|
		oneOf("= <= >= < > != + - * /")))


		SELECT cma.Name + ' '+ cmo.Name+ ' '+cv.Name CarName

**(8)** 

	casecolumn=_case
	+
	(functionbody|
	column)
	+OneOrMore(_when
	+columnVal
	+_then+
	(columnVal|
	_null))+
	Optional(_else
	+(columnVal|
	Functionbody|
	column),'')
	+_end

**Examples**

	select lst.dealerid, 
	lst.owners  as noowners, 
	lst.sortscore, 
	Lst.videocount,
	lst.additionalfuel, 
	case lst.originalimgpath when null then '' else concat(lst.hosturl , '310x174' ,       lst.originalimgpath  end as imageurlmedium, 
	case vs.carfueltype when 1 then 'Petrol' when 2 then 'Diesel' when 3 then 'CNG' when 4 then 'LPG' when 5 then 'Electric' end as carfueltype,
	lst.rootid, lst.rootname     
	from livelistings lst  
	inner join cwmasterdb.carversions vs on lst.versionid=vs.id

	where lst.sellertype=1 and lst.dealerid not in (select listmember from fnsplitcsv)
	and 12*(year(now())-year(lst.makeyear)) + month(now()) - month(lst.makeyear)  <= 96 
	and lst.cityid in(select id from cwmasterdb.cities where name in ('Agra', 'gurgaon') and isdeleted=0);

**(9) In Declare statement we have select statement like this**

	DeclarativeSyntax=_declare + DataType + ';'

	DataType=((_int|_varchar|
	_numeric|_decimal|_float|_double|_integer|_datetime|_tinyint|_smallint|_bigint|
	_date|_time|_year|_char|_timestamp|_bit|_nvarchar).setResultsName("Data",listAllMatches=True)
	+DataTypeSize.setResultsName("DataSize",listAllMatches=True))
	+Optional(_unsigned,'')
	+Optional(
	Optional(_default,'')
	+(_not_null|_null|
	(Optional('-','')
	+Word(nums)|
	(lpar
	+selectStmt
	+rpar))|
	(Combine(Word(nums) + "." + Word(nums)))),'')+
	Optional(_auto_incr,'')


	DataTypeSize=Optional(
	Lpar+
	(SizeInt.setResultsName("IntegerPartSize")
	+
	','+SizeFraction.setResultsName("FractionPartSize")|
	Size.setResultsName("DataTypeSize"))
	+rpar,'')


**Example**  

	declare v_mobile varchar(20) default (
	select customermobile from customersellinquiries where id = v_carid limit 1
	);

**2. Delete:**  

	deleteStmt=(_delete+
	_from+
	table.setResultsName("Table")+
	Optional(where + Group(whereExpr), '').setResultsName("where")).setResultsName("Delete",listAllMatches=True)

**Examples**  

	Delete from mytable;
	Delete from mytable where (a>=b) and (b=c or b!=d)

**3.Update:**  

	updateStmt=(_update+
	table.setResultsName("Table")+
	_set+(SetColumnValues)+
	Optional(where+ Group(whereExpr), '').setResultsName("where")).setResultsName("Update",listAllMatches=True)




**Examples**

	Update table set a=b,b=d,a=now(12)*d, where a=d and b=c or v=i;

	update carphotos
	set ismain = 0
	where  tc_carphotoid <> v_tc_carphotoid and inquiryid=v_inquiryid and isactive = 1 and isapproved = 1;

	update carphotos
	set ismain = v_ismain,
	description = v_description,
	originalimgpath = v_originalimgpath,
	title=v_title
	where tc_carphotoid=v_tc_carphotoid and inquiryid=v_inquiryid;


**4. Create:**  

	ColumnsDefine =  delimitedList (column.setResultsName(" Column ",listAllMatches=True ) + DataType ))
	createStmt=(_create+
	Optional(_temporary,'').setResultsName("Temporary")+
	_table+
	table.setResultsName("Table")+
	((lpar + ( selectStmt | ColumnsDefine.setResultsName( " ColumnsDetails " )) + rpar)|
	(( selectStmt | ColumnsDefine )))).setResultsName( " Create",listAllMatches=True)

**Example**  

	create temporary table tempindividualresponseforct
	select carprice,
	cityname

	from
	(select
	c.id buyerid,
	c.name buyername,
	llc.cityname cityname
	from classifiedrequests cr 
	inner join ll_cities llc  on csi.cityid=llc.cityid -- added by afrose
	where cr.requestdatetime >= date_add(now(), interval v_individualresponseend minute) and cr.requestdatetime <= date_add(now(), interval v_individualresponsestart minute)
	union
	select
	-1 buyerid,
	cl.custname buyername,
	llc.cityname cityname
	from classifiedleads cl 
	inner join ll_cities llc  on csi.cityid=llc.cityid -- added by afrose
	where cl.isverified = 0 and cl.sellertype =2 
	and cl.entrydatetime >= date_add(now(), interval v_individualresponseend minute) and cl.entrydatetime <= date_add(now(), interval v_individualresponsestart minute)
	) a
	left join tc_customerdetails tcd   on a.buyermobile = tcd.mobile 
	and tcd.entrydate >= date_add(now(), interval v_dealerresponsedays day) and tcd.entrydate<= now()
	where tcd.mobile is  null;






**5. Insert:**

	InsertIntoColumns=Optional((
	Lpar+
	delimitedList(column).setResultsName("InsertColumns",listAllMatches=True)+
	rpar),'')

	InsertColumnValues=lpar+
	delimitedList((
	columnVal|
	Column|
	functionbody).setResultsName("ColumnValue"))+
	Rpar

	insertStmt=(_insert_into+
	((table.setResultsName("Table")+
	InsertIntoColumns+
	_values+
	InsertColumnValues.setResultsName("ColumnValues"))|
	(functionbody+
	selectStmt))).setResultsName("Insert",listAllMatches=True)

**Examples** 

	insert into sellinquiries
	(
	dealerid ,
	carversionid ,
	Sourceid
	)
	values
	(
	v_emi ,
	v_sourceid
	);





**6. Truncate:**   

	option=Optional(_if_exists,'')

	truncateStmt=(
	_truncate
	+
	Optional(_temporary,'').setResultsName("Temporary")
	+
	_table
	+
	option
	+
	table.setResultsName("Table")).setResultsName("Truncate",listAllMatche=True)


**Example**  


	truncate table if exists tempindividualresponseforct;

**7. Drop**   

	dropStmt=(_drop
	+Optional(_temporary,'').setResultsName("Temporary")
	+(_table
	+
	Option
	+
	tables.setResultsName("Table"))).setResultsName("Drop",listAllMatches=True)

**Example**  

	 drop table if exists tempindividualresponseforct;
**8. Call Procedure statement:**


	callStmt=
	_call
	+StoredProcedure
	+lpar
	+delimitedList(columnVal|
	column)
	+rpar

**Example**

**9. Set Statement:**  

	setStmt = _set + column.setResultsName("ValueName") + Literal(' = ')+( caseStmt | Value )

	Value=expression

	caseStmt = _case + ZeroOrMore( _when + column 
	+  oneOf(" = != >= <= <> < >  ''")  + 
	columnVal + 
	_ then + columnVal)
	+ _else  + columnVal + _end
**Example**  

	set v_lg = ifnull(v_longitude,0);

	Value includes cobination of functions/columns/columnvalues and arthimatic operations

	set v_currentdistance= sqrt( power(((v_lt - v_ltvaluation) * v_constlt), 2) 
	+ power(((v_lg - v_lgvaluation) * v_constlg), 2) );

	SET LASTNAME =CASE  WHEN LASTNAME = 'AAA' THEN 'BBB' 
	WHEN LASTNAME = 'CCC' THEN 'DDD' 
	WHEN LASTNAME = 'EEE' THEN 'FFF' 
	ELSE LASTNAME
	END

**10. If ( condition , Yes ,No ) is Like Condition?True:False**

	IF = _if + lpar + cond + ',' + yes + ',' + no + rpar
	cond = ( Value ) + oneOf(" = != <= >= < > <> ") + (Value)
	yes = ( Value )
	no = ( Value )

**Example**

	Set column_name=If( expression,expression,expression )


**11. If...Else  if …..Else….End if :**  

	ifStmt << = (( _if_exists | _if_not_exists | _if ) + 
	(( lpar + ifCondition + rpar)|
	ifCondition) + _then
	+( ZeroOrMore (( 
	setStmt | updateStmt | selectStmt | callWithSelect|insertStmt | truncateStmt | deleteStmt | alterStmt | createStmt | callStmt|dropStmt|ifStmt)+';')|
	(Return+';'))
	+ZeroOrMore(_else_if+((lpar+ifCondition+rpar)|ifCondition)+_then
	+(ZeroOrMore(( setStmt | updateStmt |   selectStmt | callWithSelect|  
	insertStmt| truncateStmt| deleteStmt| alterStmt|
	createStmt
	callStmt|
	dropStmt|
	ifStmt)+';')|
	(Return+';')))+
	Optional(_else+(ZeroOrMore((setStmt|updateStmt| selectStmt|callWithSelect|
	insertStmt|
	truncateStmt|
	deleteStmt|alterStmt|createStmt|callStmt|dropStmt|ifStmt)+';'))|
	(Return+';'),'')+
	_end_if).setResultsName("IfStmt")

	Other = ZeroOrMore( functionbody | identifier | columnVal )

	ifStmt = Forward( )
	ifCondition = ( ( Group ( whereExpr ) ) |  
	( column + ( _is_null | _is_not_null ))| 
	(selectStmt) | Other )

	**Example**
**(1)**  

		IF EXISTS (SELECT InquiryId FROM livelistings WHERE Inquiryid = v_CarId AND SellerType = 2) THEN
		SET v_IsLive = 1;
		ELSE
		SET v_IsLive = 0;
		END IF;


**(2)**   

	IF v_SellInquiryId = -1 THEN

	SELECT ID INTO v_AreaId
	FROM cwmasterdb.areas
	WHERE Name = v_AreaName AND PinCode = v_PinCode limit 1;

	VALUES(v_CustomerId, v_ShareToCT);

	SET v_ID = LAST_INSERT_ID();

	if(v_ID is not null and v_Owners is not null) then
	insert into customersellinquirydetails(InquiryId,Owners) values (v_ID,v_Owners);
	end if;
	ELSe
	UPDATE customersellinquiries 
	SET CityId = v_CityId,
	Price = v_Price,
	PinCode = v_PinCode,
	PackageId = IF(v_PackageId > 0, v_PackageId, PackageId),
	ShareToCT = IF(v_ShareToCT != -1, v_ShareToCT, ShareToCT),
	CustomerName = ifnull(v_CustomerName,CustomerName),
	CustomerEmail = ifnull(v_CustomerEmail,CustomerEmail),
	CustomerMobile = ifnull(v_CustomerMobile,CustomerMobile)
	WHERE ID = v_SellInquiryId;

	SET v_ID = v_SellInquiryId;
	update customersellinquirydetails set Owners = ifnull(v_Owners,Owners) where InquiryId = v_SellInquiryId;

	END IF;

**12. While…..End While:**


	WhileStmt=Forward()

	WhileStmt<<=_while             +            Group(whereExpr) +     _do     + ZeroOrMore((setStmt
	|ifStmt.setResultsName("IfStmt")
	|callStmt
	|insertStmt
	|createStmt
	|dropStmt|
	deleteStmt|
	alterStmt|
	truncateStmt
	|selectStmt|
	updateStmt
	|WhileStmt)+';')+_end_while

**Example**


	while v_p <= v_l do 
	set v_c = ascii(substring(v_s, v_p, 1));
	if (v_c between 48 and 57 or v_c between 65 and 90 or v_c between 97 and 122)
	then 
	set v_s2 = concat(v_s2,char(v_c));
	end if;
	set v_p = v_p + 1;
	end while ;

**13. Create Procedure Standard statement:**


	InputParameters=delimitedList(
	Optional((_in | _out | _inout),'')     +    column   +  DataType
	)

	DeclarativeSyntax=(    _declare   +  column   +   DataType   +  ';' 
	)

	createProcedureStmt  =  createProcedure +
	StoredProcedure.setResultsName("Procedure")  +  
	lpar   +  Optional(InputParameters.setResultsName("Input"),'') +  rpar +
	Optional(  _sql_security_invoker,'').setResultsName("SQLSECURITY")+
	_begin   + 
	ZeroOrMore(DeclarativeSyntax).setResultsName("Declare")+
	ZeroOrMore((  selectStmt|setStmt|ifStmt.setResultsName("IfStmt")|callStmt|updateStmt|createStmt|dropStmt|alterStmt|insertStmt|deleteStmt|WhileStmt.setResultsName("WhileStmt")|createStmt)+';'
	)    + 
	_end  + Optional(';','')


**Example:**

	CREATE PROCEDURE    InsertCustomerSellInquiriesPartial_v17_6_2    (v_SellInquiryId  NUMERIC,
	v_CustomerId DECIMAL,
	v_CityId INT,
	v_Owners decimal)
	SQL SECURITY INVOKER
	BEGIN
	declare column_name varchar(2000);
	update customersellinquirydetails set Owners = ifnull(v_Owners,Owners) where InquiryId = v_SellInquiryId;
	END ;


**14. Create Function Statement(Return)**

	createfunctionStmt = createFunction + Functionname.setResultsName("Function")+
	Lpar +
	Optional(InputParameters.setResultsName("Input"),'') +
	Rpar  +
	_returns+ DataType+ Optional(_sql_security_invoker,'').setResultsName("SQLSECURITY")+ 
	_begin+ 
	ZeroOrMore(DeclarativeSyntax).setResultsName("Declare")+
	ZeroOrMore((selectStmt|setStmt|ifStmt.setResultsName("IfStmt")|callStmt|updateStmt|createStmt|dropStmt|alterStmt|insertStmt|deleteStmt|WhileStmt.setResultsName("WhileStmt")|createStmt|Return)+';') + 
	_end+Optional(';','')

**Example:**  

	CREATE FUNCTION RemoveSpecialChars(v_s varchar(2500)) RETURNS varchar(2500)     SQL SECURITY INVOKER
	begin
	declare v_s2 varchar(2500);   
	if v_s is null then 
	return null;
	end if;
	set v_l = char_length(v_s)
	while v_p <= v_l do 
	set v_c = ascii(substring(v_s, v_p, 1));
	if (v_c between 48 and 57 or v_c between 65 and 90 or v_c between 97 and 122)
	then 
	set v_s2 = concat(v_s2,char(v_c));
	end if;
	set v_p = v_p + 1;
	end while ;
	if char_length(v_s2) = 0 
	then 
	return null;
	end if; 
	return v_s2;
	End



**15. Alter :**  

	alterStmt=(_alter +  
	_table  
	+table.setResultsName("Table")+ delimitedList(DropColumnStmt.setResultsName("DropColumnStmt",listAllMatches=True)|  
	addDropStmt.setResultsName("AddDropStmt",listAllMatches=True)|  
	ChangeColumnStmt.setResultsName("ChangeColmnStmt",listAllMatches=True)|  
	RenameTableStmt.setResultsName("RenameTableStmt",listAllMatches=True))).setResultsName("Alter",listAllMatches=True)  

	DropColumnStmt=_drop+Optional(_column,'')+column.setResultsName("column").setResultsName("DropColumn")  

	ChangeColumnStmt=_change.setResultsName("Change")+column.setResultsName("ColumnFirst")+column.setResultsName("ColumnSecond")+DataType  

	RenameTableStmt=_rename.setResultsName("Rename")+table.setResultsName("Tables")  

	addDropStmt = (_add|_modify)   
	+Group((_index.setResultsName("Index")  
	|_unique.setResultsName("Unique")  
	|_primary_key.setResultsName("PrimaryKey"))  
	+lpar +(column+ZeroOrMore(','+column)).setResultsName("Columns") +  
	rpar|(Optional(_column,'')+ column.setResultsName("Columns")+DataType))  

**Example:**

	Alter table table_name add column column_name,  
	drop column column_name,  
	add index(p,qa),   
	add primary key(b),  
	change bc bg varchar(200);  



**5. Results:**  :+1:

``` Average 75 % of Accuracy. ```

 ```Output : List_Of_warnings```
   
   
Input:Folder containing sql files or a file with database name    


**6. References :**   

   For More Details [Go To Pyparsing](http://pythonhosted.org/pyparsing/) 

 

















```
