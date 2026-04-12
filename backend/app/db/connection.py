from sqlalchemy import create_engine
from urllib.parse import quote_plus

# ✅ Raw ODBC string (WORKING)
odbc_str = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=real-estate-project.database.windows.net;"
    "DATABASE=RE-sql-db-8832029;"
    "UID=Realestate;"
    "PWD=Estate@1;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
    "Connection Timeout=30;"
)

# ✅ Convert to SQLAlchemy format
connect_str = "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc_str)

engine = create_engine(connect_str)