from openai import OpenAI
import json
from pydantic import BaseModel
from typing import List
import pandas as pd
from extraction_agent import *
from collections import Counter
import re,os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPEN_API_KEY = os.getenv('OPEN_API_KEY')

def write_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data.model_dump(),f,indent=2)
    print("gpt response is saved")

def write_simple_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data,f,indent=2)
    print("simple data is saved")

def remove_file(xlsx_path):
    if os.path.exists(xlsx_path):
        os.remove(xlsx_path)
       
def generate_first_response(company_urls,instruction,text_format):
    client = OpenAI(api_key=OPEN_API_KEY)
    company_url_str = '<CompanyList>\n' + "\n".join(company_urls) + '\n<CompanyList>'
    user_input = f"Analyze these companies:\n{company_url_str}"

    response = client.responses.parse(
        model="gpt-4.1",
        tools=[{"type": "web_search_preview"}],
        input=user_input,
        instructions=instruction,
        text_format=text_format,
    )
    if len(response.output)>1:
        # extracted_data = response.output[1].content[0]['parsed']['extracted_data']
        extracted_data = response.output[1].content[0].text
    else:
        # extracted_data = response.output[0].content[0]['parsed']['extracted_data']
        extracted_data = response.output[0].content[0].text
    
    # print("\nresponse_type: ",type(response))
    # write_json('data/gpt_first_response.json',response)
    extracted_data=json.loads(extracted_data)
    print("First Response Generated...")
    return extracted_data['extracted_data']

def generate_second_response(company_data,instruction,text_format):
    client = OpenAI(api_key=OPEN_API_KEY)
    company_data_str = f'<InputCompanies>\n {str(company_data)} \n<InputCompanies>'
    user_input = f"Analyze these company's data:\n{company_data_str}"

    response = client.responses.parse(
        model="gpt-4.1",
        tools=[{"type": "web_search_preview"}],
        input=user_input,
        instructions=instruction,
        text_format=text_format,
    )
    if len(response.output)>1:
        # extracted_data = response.output[1].content[0]['parsed']['extracted_data']
        extracted_data = response.output[1].content[0].text
    else:
        # extracted_data = response.output[0].content[0]['parsed']['extracted_data']
        extracted_data = response.output[0].content[0].text
    
    # print("\nresponse_type: ",type(response))
    # write_json('data/gpt_second_response.json',response)
    extracted_data=json.loads(extracted_data)
    return extracted_data['extracted_data'][0]


def calculate_text_similarity_score(text1,text2,primary_score):

    text1 = re.findall(r'[A-Za-z]+|\d+', text1)
    text2=re.findall(r'[A-Za-z]+|\d+', text2)
    text2=" ".join([char.lower() for char in text2])
    score=0
    for i in text1:
        if i.lower() in text2:
            score += primary_score
    return score

def get_top_10_after_sort_result(sorted_file_name):
    columns=['Record Id','Description of deal & business']
    sorted_data=[]
    df_sorted=pd.read_excel(sorted_file_name)
    # df_sorted=df_sorted[columns]
    for _, row in df_sorted.head(10).iterrows():
        row_data = {col: row[col] for col in columns if pd.notna(row[col])}
        sorted_data.append(row_data)
        
    # write_simple_json("sorted_data.json",sorted_data)
    return sorted_data

def calculate_row_score(row, data, columns, low_score_cols, primary_score, secondary_score):
    score=0
    for column in columns:
        col_value=row[column]
        if pd.notna(col_value):
            # if col_value in batch_result_data[0][column]:
            if column in low_score_cols:
                if str(col_value).lower().strip()==str(data[column]).lower().strip() and str(col_value).lower().strip()!='0':
                    # print("str(col_value).lower():",str(col_value).lower()," added")
                    score+=secondary_score
            else:
                score+=calculate_text_similarity_score(str(col_value),str(data[column]),primary_score)
    return score

def get_matched_top_10(index,file_name,data,Last=False):
    primary_score=10
    secondary_score=5
    # file_name="excelfile/250506 EBN Targets Cleaned.xlsx"
    df = pd.read_excel(f'excelfile/{file_name}')
    columns=[
        "Its Customers industries",
        "Operational Focus",
        "Revenue in mEUR",
        "Billing Country",
        "Material or Media of products",
    ]
    low_score_cols=[columns[2],columns[3]]

    # for data in batch_result_data:
    for _, row in df.iterrows():
        score=calculate_row_score(row, data, columns, low_score_cols, primary_score, secondary_score)
        df.at[_, "score"] = score

    # sorted_file_name=f"excelfile/sorted/sorted_{file_name}"
    sorted_file_name=f"excelfile/sorted/sorted_{file_name}"

    df_sorted = df.sort_values(by='score', ascending=False)
    remove_file(sorted_file_name)
    df_sorted.to_excel(sorted_file_name, index=False, engine='openpyxl')
    top_10_data=get_top_10_after_sort_result(sorted_file_name)
    if Last:
        remove_file(sorted_file_name)
    return top_10_data


def get_final_second_response(file_name,first_result_data):
    final_result=[]
    for index,data in enumerate(first_result_data):
        if len(first_result_data)==index+1:
            top_10=get_matched_top_10(index,file_name,data,True)
        else:
            top_10=get_matched_top_10(index,file_name,data)
        input_company_data={
            'company_website':data['company_website'],
            'Description of deal & business':data['Description of deal & business'],
            'excel_data':top_10
        }
        result=generate_second_response(input_company_data,instruction_2,text_formate_2)
        final_result.append(result)
        print(f"{index+1} Second Response Generated...")


    # write_simple_json('data/final_result.json',final_result)
    print("All second responses are Generated...")
    return final_result

def generate_final_result(file_path,result_data):
    df = pd.read_excel(f"excelfile/{file_path}")
    columns=[
        "Short Title",
        "Description of deal & business",
    ]
    df=df[["Short Title", "Description of deal & business", 'Record Id']]

    for data in result_data:
        recode_id_1 = data['excel_data'][0].get('record_id')
        recode_id_2 = data['excel_data'][1].get('record_id')

        for _, row in df.iterrows():
            row_record_id = row.get('Record Id')
            for column in columns:
                value = row.get(column)
                if pd.notna(value):
                    if row_record_id == recode_id_1:
                        data['excel_data'][0][column] = value
                    elif row_record_id == recode_id_2:
                        data['excel_data'][1][column] = value
                        
    write_simple_json('data/update_final_result.json',result_data)
    print(f"✅ All done! Updated Results are saved")