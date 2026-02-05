import pandas as pd
from db import assessment_collection

file_path = "DataSurvey(Cleaned) (2).xlsx"

df = pd.read_excel(file_path)

data = df.to_dict(orient="records")

assessment_collection.delete_many({})
assessment_collection.insert_many(data)

print("Dataset Imported Successfully")
