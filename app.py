from utils import *
from extraction_agent import *
import re

batch_companies=[
    "https://business.nextdoor.com/en-us/small-business",
    "https://citysquares.com/add_business",
    "https://www.cylex.us.com/",
    "https://www.callupcontact.com/",
    "https://navmii.com/",
]

file_name="250506 EBN Targets Cleaned.xlsx"
batch_result_data=generate_first_response(batch_companies,get_instruction_1(file_name),text_formate_1)

second_result=get_final_second_response(file_name,batch_result_data)

generate_final_result(file_name,second_result)
