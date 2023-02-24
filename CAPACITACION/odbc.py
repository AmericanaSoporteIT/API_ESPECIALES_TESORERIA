import sys
import pyodbc
from configparser import ConfigParser

class Config:
	def __init__(self):
		self.section = 'MySQL'
		self.filename = 'config.ini'
		self.readFile = self.readFile()

	def readFile(self, absolut_paht_file='config.ini'):
		try:
			if absolut_paht_file:
				with open(absolut_paht_file, 'r') as file:
					self.filename = file.name
				return self.filename
		except FileNotFoundError:
			print("File Not Found")

	def params(self, section="MYSQL"):
		parser = ConfigParser(allow_no_value=True)
		parser.read(self.readFile)
		db = {}
		try:
			if section:
				params = parser.items(section)
				for param in params:
					db[param[0]] =param[1]
			return db
		except Exception as err:
			print(f"{err}")

class Odbc:
	dialect = None
	connection  = None
	cursor = None

	def __init__(self, dialect):
		self.conf = Config()
		self.dialect = dialect
		self.connection = self.connect()

	def connect(self,char_encode=None, charset=None, auto_commit=False):
		conf = self.conf.params(section=self.dialect)
		if char_encode:
			conn = pyodbc.connect(**conf, charset=charset, auto_commit=auto_commit)
			self.connection = conn
			conn.setdecoding(pyodbc.SQL_CHAR, char_encode)
			conn.setdecoding(pyodbc.SQL_WCHAR, char_encode)
			return self.connection
		else:
			conn = pyodbc.connect(**conf)
			self.connection = conn
			return self.connection

	def close():
		self.connection.close()
	
	def tables_information(self, type_object=None):
		if type_object:
			tables = [row for row in self.connection.cursor().tables() if row.table_type == type_object]
			return tables
		else:
			tables = [row for row in self.connection.cursor().tables()]
			return tables


	def columns_name(self,table):
		cursor = self.connection.cursor()		
		xcrsr = cursor.columns(table=table)
		columns = [col[3] for col in xcrsr.fetchall() ]
		return columns


def test():
	mssql = Odbc("MSSQLSERVER")
	conn = mssql.connect(char_encode='IBM437', auto_commit=False) #auto_comit defaul is false
	cursor = conn.cursor()
	tables = mssql.tables_information()
	print(tables)
	print(cursor.execute("SELECT * from QSYSTEMS.dbo.VENDEDOR where VEN_CODIGO = ?", 405).fetchall())

	# mysql = Odbc("MYSQL")
	# conn = mysql.connect(auto_commit=False) #auto_comit defaul is false
	# cursor = conn.cursor()
	# print(cursor.execute("SELECT * from sis_empresa").fetchall())
	# print(mysql.columns_name('sis_empresa'))
	# tables = mysql.tables_information(type_object="TABLE")
	# print(tables)

