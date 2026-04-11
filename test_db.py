import pyodbc

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=real-estate-project.database.windows.net;"
    "DATABASE=RE-sql-db-8832029;"
    "UID=Realestate;"
    "PWD=Estate@1;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

print("✅ Connected successfully!")

conn.close()