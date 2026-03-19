import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://harsh:@localhost:5432/phase-2")

df = pd.read_csv("/Users/harsh/data-engineering/Phase-2/archive/olist_order_reviews_dataset.csv")
print(df.shape)
print(df.head())

df.to_sql("order_reviews", engine, if_exists="append", index=False)
print("Done!")