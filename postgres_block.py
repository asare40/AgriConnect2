from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('postgresql://user:password@host/dbname')
df = pd.read_sql("SELECT * FROM farmers", engine)