"""SQL client to create or consuting a DB.

    Dev: franco@systemagency.com
"""

import os
import sqlite3
from time import gmtime, strftime

class dbMaker():

    def __init__(self, name, table_name=""):
        """
        @param name string, name of the db
        need to include the extension '.db'

            name = "MyDB.db'
        """
        self.name = name
        self.tableName = table_name
        

    def connect(self):
        self.conn = sqlite3.connect(self.name)


    def makeCursor(self):
        """Create the cursor of the instance
        """
        self.c = self.conn.cursor()    


    def setName(self, name):
        """Set another name for a DB
        """
        self.name = name


    def setTableName(self, name:str):
        """Set another name for a Table
        """
        self.tableName = name


    def executeLine(self, sourceLine):
        """Executing a string with a valid SQL syntax
        """
        self.c.execute(sourceLine)
        self.commit()


    def commit(self):
        """Commited the changes maked into the
        DataBase
        """
        self.conn.commit() 


    def close(self):
        """ Close the connection on the current cursor.
        """
        self.conn.close()


    def insertion(self, row):
        """Executing a insertion in the DB.

        Using a try/except to catch duplicates rows.

        output: Boolean
            True: Succesfull insertion

            False: Row exist in the Table, not gonna be inserted. 
        """
        out = True
        try:
            line = "INSERT INTO {} VALUES ({})".format(
                                                        self.tableName,
                                                        row
                                                )
            # print(line)
            self.c.execute(line)
            self.commit()
        except (sqlite3.IntegrityError, sqlite3.OperationalError):
            out =  False

        return out


    def selectAll(self, query):
        """Consult the database.
        Execute a query line with a SQL valid syntax.
        """
        print(query)
        self.c.execute(query)
        return self.c.fetchall()

    """
    Untested section.

    DBt = testdb('links.db', "links")

    DBt.makingdbTest()
    DBt.commit()

    DBt.insertion("google.com", "USA", date)

    row_1 = links("nasa.com", country="USA")
    DBt.insertion(row_1.get())

    l = DBt.selectAll("SELECT * FROM links WHERE Country=\"USA\"")
    for e in l:
        print(e)
    """
if __name__ == '__main__':
    
    # This section will run this just one time.
    Seekdb = os.listdir(path=os.getcwd())
    try:
        db = next(file for file in Seekdb if ".db" in file )
        db = dbMaker(name = db, table_name="AgencyBank")
        """
        db.executeLine("DROP AgencyUpdate")
        db.executeLine(
            CREATE TABLE AgencyUpdate(\
                    Date_Update text NOT NULL,\
                    Agency_Name text NOT NULL\
                )
        )
        db.close()
        """
    except StopIteration:
        print("Making a DB.\n")
        db = dbMaker(name = "Scouting.db", table_name="ScoutingList")
        db.connect()
        db.commit()
        db.executeLine(
            """CREATE TABLE AgencyBank (\
                    Agency_Name text NOT NULL,\
                    Country text NOT NULL,\
                    Date_In text NOT NULL\
                )"""
        )
        
"""    
Get on query
{ 
    TableName: 'family',
    IndexName: 'go-index',
    ExpressionAttributeValues: { ':vgo': { S: 'yes' }, ':vitemName0': { S: 'Fran' } },
    ExpressionAttributeNames: { '#g': 'go' },
    KeyConditionExpression: '#g = :vgo',
    FilterExpression: 'contains(itemName, :vitemName0) ' 
}
"""