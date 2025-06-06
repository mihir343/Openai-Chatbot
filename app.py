from utils import *
from extraction_agent import *
import re

batch_companies=[
    "https://business.nextdoor.com/en-us/small-business"
]

file_name="250506 EBN Targets Cleaned.xlsx"
result=generate_final_result(batch_companies,file_name)
print(result)
