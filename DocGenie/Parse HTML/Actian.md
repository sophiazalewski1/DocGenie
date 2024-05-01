# .NET Data Provider Classes
The .NET Data Provider is the runtime component that provides the interface between the .NET application and Actian databases.

The .NET Data Provider namespace (Ingres.Client) and its contents follow the same pattern as the Microsoft data providers.

All public static members are safe for multithreaded operations. To reduce unnecessary overhead, instance members are not guaranteed to be thread safe. If a thread-safe operation on the instance is needed, wrap the operation in one of .NET's System.Threading synchronization methods to protect the state of the critical section of code.

The base class and interface definition for each class is provided in C# and VB.NET syntax as shown below. However, .NET's language interoperability feature allows any managed language to use the .NET Data Provider.

**C#:** Public sealed class IngresParameter : System.Data.Common.DbParameter, IDataParameter, IDbDataParameter, ICloneable

**VB.NET:** NotInheritable public class IngresParameter 

 Inherits System.Data.Common.DbParameter  Implements IDataParameter, IDbDataParameter, ICloneable

For more information on data provider classes, including information on other .NET language syntax and inherited methods and properties, see the *Microsoft .NET Framework Developer's Guide*  and Microsoft .NET Framework Class Library documentation.

## IngresCommand Class
The IngresCommand class represents an SQL command or a database procedure that executes against an Actian database.

Parameter placeholders in the SQL command text are represented by a question mark (?).

Database procedures can be invoked by either setting CommandText=”myproc” and CommandType=CommandType.StoredProcedure, or by using the escape sequence format and setting CommandText=”{ call myproc }” and CommandType=CommandType.Text.

The .NET Data Provider does not currently support the following features:

* 	Multiple active results-sets
* 	Batched commands consisting of multiple Ingres SQL commands in one IngresCommand object
* 	Support for Ingres SQL command COPY TABLE
* 	Support for Ingres SQL command SAVEPOINT
* 	IngresCommand.ExecuteReader(CommandBehavior.SchemaOnly) is supported for SELECT commands only
### IngresCommand Class Declaration
The IngresCommand class declarations are:

**C#:** public sealed class IngresCommand : System.Data.Common.DbCommand, IDbCommand, IDisposable, ICloneable

**VB.NET:** NotInheritable Public Class IngresCommand  Inherits System.Data.Common.DbCommand  Implements IDbCommand, IDisposable, ICloneable

### IngresCommand Class Example
```
IngresCommand cmd = new IngresCommand(
"SELECT id, name FROM employee WHERE id = ?");
```
### IngresCommand Class Properties
The IngresCommand class properties are:

|Property|Accessor|Description|
|--|--|--|
|CommandText|get  set|SQL statement string to execute or procedure name to call.|
|CommandTimeout|get  set|The time, in seconds, for an attempted query to time-out if the query has not yet completed. Default is 0 seconds.|
|CommandType|get  set|An enumeration describing how to interpret the CommandText property. Valid values are Text, TableDirect, or StoredProcedure.|
|Connection|get  set|The IngresConnection object that is used to identify the connection to execute a command. For more information, see IngresConnection Class.|
|Parameters|get|The IngresParameterCollection for the parameters associated with the SQL query or database procedure. For more information, see IngresParameterCollection Class.|
|Transaction|get  set|The IngresTransaction object in which the IngresCommand executes. This transaction object must be compatible with the transaction object that is associated with the Connection, (that is, the IngresTransaction must be the object (or a copy) returned by IngresConnection.BeginTransaction).|
|UpdateRowSource|get  set|Defines how results are applied to a rowset by the DbDataAdapter.Update method. (Inherited from DbDataAdapter.)|
### IngresCommand Class Public Methods
The public methods for the IngresCommand class are:

|Method|Description|
|--|--|
|Cancel|Cancels the execution of the SQL command or database procedure.|
|CreateParameter|Creates a new instance of IngresParameter. For more information, see IngresParameter Class.|
|Dispose|Releases allocated resources of the IngresCommand and base Component.|
|ExecuteNonQuery|Executes a command that does not return results. Returns the number of rows affected by the update, delete, or insert SQL command.|
|ExecuteReader|Executes a command and builds an IngresDataReader. For more information, see IngresDataReader Class.|
|ExecuteScalar|Executes a command and returns the first column of the first row of the result set.|
|Prepare|Prepares the SQL statement to be executed later.|
|ResetCommandTimeout|Resets the CommandTimeout property to its default value of 30 seconds.|
### IngresCommand Class Constructors
The constructors for the IngresCommand class are:

|Constructor Overloads|Description|
|--|--|
|IngresCommand()|Instantiates a new instance of the IngresCommand class using default property values|
|IngresCommand(string)|Instantiates a new instance of the IngresCommand class using the defined SQL command or database procedure|
|IngresCommand(string, IngresConnection)|Instantiates a new instance of the IngresCommand class using the defined SQL command or database procedure and the connection to the Actian database|
|IngresCommand(string, IngresConnection, IngresTransaction)|Instantiates a new instance of the IngresCommand class using the defined SQL command or database procedure, the connection to the Actian database, and the IngresTransaction object|
## Sample Program Constructed with .NET Data Provider
To construct an application using the .NET Data Provider, the developer creates a series of objects from the data provider's classes. The following is a simple C# program employing four data provider classes.

#### .NET 2.0 Programming Model
```
using System;
using System.Configuration;
using System.Data;
using System.Data.Common;
using System.IO;
using Ingres.Client;
 
class App
{
static public void Main()
{
ConnectionStringSettingsCollection connectionSettings =
        ConfigurationManager.ConnectionStrings;
if (connectionSettings.Count == 0)
        throw new InvalidOperationException(
         "No connection information specified in application configuration file.");
ConnectionStringSettings connectionSetting = connectionSettings[0];
 
string invariantName      = connectionSetting.ProviderName;
string myConnectionString = connectionSetting.ConnectionString;
 
DbProviderFactory factory = DbProviderFactories.GetFactory(invariantName);
 
DbConnection conn =
         factory.CreateConnection();
conn.ConnectionString = myConnectionString;
 
conn.Open();   // open the Ingres connection
 
string cmdtext =
        "select table_owner, table_name, " +
        " create_date from iitables " +
        " where table_type in ('T','V') and " +
        " table_name not like 'ii%' and" +
        " table_name not like 'II%'";
DbCommand cmd = conn.CreateCommand();
cmd.CommandText = cmdtext;
 
//          read the data using the DataReader method
DbDataReader   datareader = cmd.ExecuteReader();
 
//          write header labels
Console.WriteLine(datareader.GetName(0).PadRight(18) +
datareader.GetName(1).PadRight(34) +
datareader.GetName(2).PadRight(34));
int i = 0;
while (i++ < 10  &&  datareader.Read())
// read and write out a few data rows
{     // write out the three columns to the console
        Console.WriteLine(
        datareader.GetString(0).Substring(0,16).PadRight(18) +
        datareader.GetString(1).PadRight(34) +
                datareader.GetString(2));
}
datareader.Close();
 
DataSet  ds  = new DataSet("my_list_of_tables");
//          read the data using the DataAdapter method
DbDataAdapter adapter = factory.CreateDataAdapter();
DbCommand adapterCmd = conn.CreateCommand();
adapterCmd.CommandText = cmdtext;
adapter.SelectCommand = adapterCmd;
adapter.Fill(ds);  // fill the dataset
 
//          write the dataset to an XML file
ds.WriteXml("c:/temp/temp.xml");
 
conn.Close();   // close the connection
}  // end Main()
}  // end class App
```
#### .NET 1.1 Programming Model
```
using System;
using System.IO;
using System.Data;
using Ingres.Client;
 
class App
{
static public void Main()
{
string myConnectionString =
"Host=myserver.mycompany.com;" +
"User Id=myname;PWD=mypass;" +
"Database=mydatabase";
IngresConnection conn = new IngresConnection(
myConnectionString );
conn.Open();   // open the Ingres connection
 
string cmdtext = "select table_owner, table_name, " +
"create_date from iitables " +
" where table_type in ('T','V') and " +
" table_name not like 'ii%' and" +
" table_name not like 'II%'";
IngresCommand cmd = new IngresCommand(cmdtext, conn);
 
//          read the data using the DataReader method
IngresDataReader   datareader = cmd.ExecuteReader();
 
//          write header labels
Console.WriteLine(datareader.GetName(0).PadRight(18) +
datareader.GetName(1).PadRight(34) +
datareader.GetName(2).PadRight(34));
int i = 0;
while (i++ < 10  &&  datareader.Read())
// read and write out a few data rows
{     // write out the three columns to the console
        Console.WriteLine(
        datareader.GetString(0).Substring(0,16).PadRight(18) +
        datareader.GetString(1).PadRight(34) +
                datareader.GetString(2));
}
datareader.Close();
DataSet  ds  = new DataSet("my_list_of_tables");
//          read the data using the DataAdapter method
IngresDataAdapter adapter = new IngresDataAdapter();
adapter.SelectCommand = new IngresCommand(cmdtext, conn);
adapter.Fill(ds);  // fill the dataset
 
//          write the dataset to an XML file
ds.WriteXml("c:/temp/temp.xml");
 
conn.Close();   // close the connection
}  // end Main()
}  // end class App
```
## IngresCommandBuilder Class
The IngresCommandBuilder class automatically generates INSERT, DELETE, and UPDATE commands into an IngresDataAdapter object for a simple single-table SELECT query. These commands can be used to reconcile DataSet changes through the IngresDataAdapter associated with the Actian database.

### IngresCommandBuilder Class Declaration
The IngresCommandBuilder class can be declared as follows:

**C#:**  public sealed class IngresCommandBuilder : DbCommandBuilder

**VB.NET:**  NotInheritable Public Class IngresCommandBuilder Inherits DbCommandBuilder

### IngresCommandBuilder Class Properties
The IngresCommandBuilder class properties are: 

|Property|Accessor|Description|
|--|--|--|
|CatalogLocation|get set|Position of the catalog name in a qualified table name.|
|CatalogSeparator|get set|The string of characters that defines the separation between a catalog name and the table name.|
|ConflictOption|get set|Controls how to compare for update conflicts.|
|DataAdapter|get set|The IngresDataAdapter object that is associated with the CommandBuilder. The IngresDataAdapter contains the InsertCommand, DeleteCommand, and UpdateCommand objects that are automatically derived from the SelectCommand.|
|QuotePrefix|get set|The string of characters that are used as the starting delimiter of a quoted table or column name in an SQL statement.|
|QuoteSuffix|get set|The string of characters that are used as the ending delimiter of a quoted  table or column name in an SQL statement.|
|SchemaSeparator|get set|The string of characters that defines the separation between a table name and column name. Always a period (.)|
### IngresCommandBuilder Class Methods
The public methods available to the IngresCommandBuilder class are:

|Method|Description|
|--|--|
|Derive Parameters|Retrieves the parameter metadata of the database procedure specified in the IngresCommand object and populates the IngresCommand.Parameters collection. |
|GetDeleteCommand|Gets the generated IngresCommand to perform DELETE operations on the table.|
|GetInsertCommand|Gets the generated IngresCommand to perform INSERT operations on the table.|
|GetUpdateCommand|Gets the generated IngresCommand to perform UPDATE operations on the table.|
|QuoteIdentifier|Wrap quotes around an identifier.|
|RefreshSchema|Refreshes the IngresCommandBuilder's copy of the metadata of a possibly changed SELECT statement in the IngresDataAdapter.SelectCommand object.|
|UnquoteIdentifier|Removes quotes from an identifier.|
### IngresCommandBuilder Class Constructors
The IngresCommandBuilder class has the following constructors:

|Constructor Overloads|Description|
|--|--|
|IngresCommandBuilder ()|Instantiates a new instance of the IngresCommandBuilder class using default property values|
|IngresCommandBuilder (IngresDataAdapter)|Instantiates a new instance of the IngresCommandBuilder class using the specified IngresDataAdapter|
## IngresConnection Class
The IngresConnection class represents an open connection to an Actian database. This class requires a connection string to connect to a target server and database.

IngresConnection implements IDisposable and is closed safely when disposed, so the following code using the disposable pattern is safe:

```
using (var connection = new IngresConnection(connectionString))
{
    // Do something with the connection
    // No need to close
}
```
which is equivalent to the following code:

```
var connection = new IngresConnection(connectionString);
try
{
    // Do something with the connection
}
finally
{
    connection.Dispose();
}
```
### IngresConnection Class Declaration
The IngresConnection class declaration method signature is:

**C#:** public sealed class IngresConnection : System.Data.Common.DbConnection, IDbConnection, IDisposable

**VB.NET:** NotInheritable Public Class IngresConnection  Inherits System.Data.Common.DbConnection Implements IDbConnection, IDisposable

### IngresConnection Class Example
```
IngresConnection conn = new IngresConnection(
“Host=myserver.mycompany.com;Database=mydatabase;” +“User ID=myuid;Password=mypassword;”);
conn.Open( );
```
### IngresConnection Class Properties
The IngresConnection class has the following properties:

|Property|Accessor|Description|
|--|--|--|
|ConnectionString|get  set|String that specifies the target server machine and database to connect to, the credentials of the user who is connecting, and the parameters that define connection pooling and security.Default is "".Consists of keyword=value pairs, separated by semicolons. Leading and trailing blanks around the keyword or value are ignored. Case and embedded blanks in the keyword are ignored. Case and embedded blanks in the value are retained. Can only be set if connection is closed. Resetting the connection string resets the ConnectionTimeOut and Database properties.For a list of valid keywords and their descriptions, see Connection String Keywords.|
|ConnectionTimeOut|get|The time, in seconds, for an attempted connection to abort if the connection cannot be established.Default is 15 seconds.|
|Database|get|The database name specified in the ConnectionString's Database value.Default is "".|
|DataSource|get|The name of the target server.|
|ServerVersion|get|The server version number. May include additional descriptive information about the server. This property uses an IngresDataReader. For this reason, no other IngresDataReader can be active at the time that this property is first invoked.|
|State|get|The current state of the connection:  ConnectionState.Closed or ConnectionState.Open.|
### IngresConnection Class Public Methods
The public methods for the IngresConnection class are:

|Method|Description|
|--|--|
|BeginTransaction|Begins a local transaction. The connection must be open before this method can be called. Nested or parallel transactions are not supported. Mutually exclusive with the EnlistDistributedTransaction method.|
|ChangeDatabase|Changes the database to be used for the connection. The connection must be closed before this method can be called.|
|Close|Closes the connection (rollback pending transaction) and returns the connection to the connection pool.|
|CreateCommand|Creates an IngresCommand object.|
|Dispose|Closes the connection and releases allocated resources.|
|EnlistDistributedTransaction|Enlists in an existing distributed transaction (ITransaction). Mutually exclusive with the BeginTransaction method.|
|EnlistTransaction|Enlists in an existing distributed transaction (System.Transactions.Transaction). Mutually exclusive with the BeginTransaction method.|
|GetSchema|Returns schema metadata from the Actian database catalog for the specified collection name. Valid collection names include:•	MetaDataCollections•	DataSourceInformation•	DataTypes•	Restrictions•	ReservedWords•	Tables•	Views•	Columns•	Indexes•	Procedures|