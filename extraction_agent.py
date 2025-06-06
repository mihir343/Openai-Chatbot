from pydantic import BaseModel
from typing import List,Dict
import pandas as pd

class text_formate_1(BaseModel):
    extracted_data: List[Dict[str, str]]

    class Config:
        json_schema_extra = {
            "properties": {
                "extracted_data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "company_website": {"type": "string"},
                            "Description of deal & business": {"type": "string"},
                            "Its Customers industries": {"type": "string"},
                            "Operational Focus": {"type": "string"},
                            "Revenue in mEUR": {"type": "string"},
                            "Billing Country": {"type": "string"},
                            "Material or Media of products": {"type": "string"}
                        },
                        "required": [
                            "Its Customers industries",
                            "Operational Focus",
                            "Revenue in mEUR",
                            "Billing Country",
                            "Material or Media of products"
                        ],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["extracted_data"]
        }
        
def get_required_excel_data(file_name):
    df = pd.read_excel(file_name)
    columns=[
        "Its Customers industries",
        "Operational Focus",
        "Revenue in mEUR",
        "Billing Country",
        "Material or Media of products",
    ]

    excel_data=[]
    for _, row in df.iterrows():

        item={}
        for column in columns:
            value=row[column]
            if pd.notna(value):
                item[column] = value
            else:
                item[column]=None
        excel_data.append(item)
        # print()
    lists=[[],[],[],[],[]]

    for item in excel_data:
        for index,col in enumerate(columns):
            value=item[col]
            if value:
                lists[index].append(value)
        
    list_1=list(set(lists[0]))
    list_2=list(set(lists[1]))
    list_3=list(set(lists[2]))
    list_4=list(set(lists[3]))
    list_5=list(set(lists[4]))
    return list_1,list_2,list_3,list_4,list_5


def get_instruction_1(file_name):
    # file_name="excelfile/250506 EBN Targets Cleaned.xlsx"

    list_1,list_2,list_3,list_4,list_5=get_required_excel_data(f'excelfile/{file_name}')

    instruction_1=f"""
    # Company Data Extraction Instructions

    ## Role and Purpose
    You are a data extraction specialist tasked with analyzing company websites and extracting specific information according to strict validation rules and predefined data lists.

    ## Model Selection
    Use the most advanced OpenAI model available (GPT-4 or latest) for maximum accuracy in data extraction and validation.

    ## Language Requirements
    - Process all information in English only
    - If source content is in other languages, translate to English before analysis

    ## Data Fields to Extract
    Extract exactly 5 data fields for each company:

    1. **Its Customers industries**
    2. **Operational Focus** 
    3. **Revenue in mEUR**
    4. **Billing Country**
    5. **Material or Media of products**
    6. **Description of deal & business**

    ## Strict Validation Rules

    ### Revenue in mEUR - CRITICAL VALIDATION
    - **MUST** be numbers only
    - **NO** text, letters, or special characters allowed
    - **NO** currency symbols (€, $, etc.)
    - **NO** units or descriptors (million, EUR, etc.)
    - **NO** ranges or approximations (~, -, etc.)
    - Format: Enter only the numerical value
    - Examples: 
    - ✅ Correct: `125` (for 125 million EUR)
    - ❌ Wrong: `125 mEUR`, `€125M`, `~125`, `125 million`

    ### Categorical Data Validation
    The following fields **MUST** only contain values from their respective predefined lists:

    - **Its Customers industries**: Select ONLY from List_1
    - **Operational Focus**: Select ONLY from List_2  
    - **Billing Country**: Select ONLY from List_3
    - **Material or Media of product**: Select ONLY from List_4

    **IMPORTANT**: If a perfect match is not found, select the closest applicable option from the respective list. Never create custom entries.

    ## Predefined Data Lists

    ### List_1: `Customer Industries` Options
    ```
    {list_1}
    ```

    ### List_2: `Operational Focus` Options
    ```
    {list_2}
    ```

    ### List_3: `Billing Country` Options
    ```
    {list_4}
    ```

    ### List_4: `Material or Media of Products` Options
    ```
    {list_5}
    ```

    ## Analysis Process

    ### Step 1: Website Analysis
    1. Thoroughly review the provided company website(s)
    2. Analyze all pages, subdomains, and available information
    3. Extract relevant data for each required field

    ### Step 2: Data Validation
    1. **Revenue Validation**: Ensure only numerical values 
    2. **List Matching**: Verify all categorical data matches predefined lists
    3. **Completeness Check**: Ensure all 5 fields are populated

    ### Step 3: Quality Control
    - Double-check all extractions against validation rules
    - Verify list selections are accurate
    - Confirm revenue format compliance

    ### Output Format
    Required JSON Schema
    CRITICAL: Always output data in this exact JSON format matching the TargetMatch model:
    json{{
        "Its_Customers_industries": "string from List_1",
        "Operational_Focus": "string from List_2", 
        "Revenue_in_mEUR": "numeric string (e.g., '120.5')",
        "Billing_Country": "string from List_3",
        "Material_or_Media_of_products": "string from List_4"
    }}

    Single Company Example
    json{{
        "Its_Customers_industries": "string",
        "Operational_Focus": "string",
        "Revenue_in_mEUR": "120.5",
        "Billing_Country": "string", 
        "Material_or_Media_of_products": "string"
        "Description of deal & business": "string"
    }}

    Multiple Companies
    Provide as JSON array:
    json[
    {{
        "Its_Customers_industries": "string",
        "Operational_Focus": "string", 
        "Revenue_in_mEUR": "120.5",
        "Billing_Country": "string",
        "Material_or_Media_of_products": "string"
        "Description of deal & business": "string"
    }},
    {{
        "Its_Customers_industries": "string",
        "Operational_Focus": "string",
        "Revenue_in_mEUR": "85.2", 
        "Billing_Country": "string",
        "Material_or_Media_of_products": "string"
        "Description of deal & business": "string"
    }}
    ]
    Large Batches (10+ Companies)

    Process in batches of 10 companies
    Show intermediate results after each batch
    Continue until all companies are processed
    Provide final combined table and CSV download

    Error Handling

    If information cannot be found: Use closest applicable option from respective lists
    If revenue is unavailable: Enter 0
    If country cannot be determined: Select Other from List_3
    Never leave fields empty or create custom entries

    Final Deliverables

    JSON Output: Always provide data in TargetMatch model format
    Single Company: JSON object with 5 required fields
    Multiple Companies: JSON array of TargetMatch objects
    Validation Confirmation: "Data extraction complete. All validations applied successfully."

    Critical Reminders

    ALWAYS output in exact JSON format matching TargetMatch model
    FIELD NAMES: Use exact field names: Its_Customers_industries, Operational_Focus, Revenue_in_mEUR, Billing_Country, Material_or_Media_of_product,Description of deal & business
    REVENUE FORMAT: Numeric string with quotes (e.g., "120.5")
    NEVER deviate from the predefined lists
    DOUBLE-CHECK all validations before providing results
    MAINTAIN consistency across all entries
    """
    return instruction_1


class ExcelData(BaseModel):
    record_id: str

class CompanyData(BaseModel):
    company_website: str
    original_description: str
    excel_data: List[ExcelData]

class text_formate_2(BaseModel):
    extracted_data: List[CompanyData]

    class Config:
        json_schema_extra = {
            "example": {
                "extracted_data": [
                    {
                        "company_website": "https://example.com",
                        "original_description": "Original company description exactly as provided",
                        "excel_data": [
                            {
                                "record_id": "zcrm_123456"
                            },
                            {
                                "record_id": "zcrm_123456"
                            }
                        ]
                    }
                ]
            }
        }


instruction_2 = f"""
# Company-Excel Data Matching Analysis Instruction

You are an expert business analyst specializing in semantic matching and business intelligence. Your task is to analyze company descriptions against a database of reference descriptions and identify the most relevant matches.

## Task Overview
For each company provided, you will:
1. Analyze the company's description to understand its business model, industry, products/services, and key characteristics
2. Compare this against all available excel_data descriptions using semantic similarity, business relevance, and contextual matching
3. Identify the TOP 2 best matching descriptions from excel_data based on business alignment, industry relevance, and descriptive similarity
4. Return structured results with the original company data and the top 2 matches

## Matching Criteria (in order of importance)
1. **Business Model Alignment**: Companies with similar business models, revenue streams, or operational approaches
2. **Industry/Sector Relevance**: Companies operating in the same or closely related industries
3. **Product/Service Similarity**: Similar offerings, solutions, or target problems being solved
4. **Target Market Overlap**: Similar customer segments, market focus, or business applications
5. **Semantic Similarity**: Textual and conceptual similarity in descriptions
6. **Company Stage/Scale**: Similar business maturity, size, or market position where applicable

## Analysis Process
1. **Parse Company Description**: Extract key business elements (industry, products, services, target market, business model)
2. **Analyze Excel Data**: Understand each excel_data description's business context
3. **Semantic Matching**: Use natural language understanding to identify conceptual similarities
4. **Business Logic Matching**: Apply business intelligence to identify strategically relevant matches
5. **Ranking**: Score and rank all excel_data entries, selecting the top 2 best matches
6. **Validation**: Ensure selected matches are genuinely relevant and not just textually similar

## Quality Standards
- Matches must be genuinely relevant from a business perspective, not just keyword matches
- Prioritize strategic business alignment over superficial textual similarity
- Consider industry context and business logic in matching decisions
- Ensure diversity in top 2 matches when possible (avoid two nearly identical matches)

## Input Data
You receive data which is provided in the <InputCompanies> tag.
Input Data in this exact JSON structure:
```json
{{
    "company_website": "https://company1.com",
    "Description of deal & business": "Description of deal & business of Company 1",
    "excel_data": [/* 10 exce_data */]
}}
```

## Required Output Format
Return results in this exact JSON structure:
```json
{{
    "company_website": "https://example.com",
    "original_description": "Original company description exactly as provided",
    "excel_data": [
        {{
            "record_id": "zcrm_123456"
        }},
        {{
            "record_id": "zcrm_123456"
        }}
    ]
}}
```

## Critical Requirements
1. **Always return exactly 2 matches** in the excel_data array, ordered by relevance (best match first)
2. **Preserve original data**: company_website and original_description must remain exactly as provided
3. **Business-first approach**: Prioritize business relevance over textual similarity
4. **No hallucination**: Only use record_ids and descriptions that exist in the provided excel_data

## Edge Cases
- If fewer than 2 relevant matches exist, still return the 2 best available options
- If multiple excel_data entries are equally relevant, prioritize based on business strategic value
- Handle cases where company description is vague by focusing on available business indicators
- For highly technical or niche companies, prioritize industry-specific matches

## Multiple Companies Processing
If multiple companies are provided in a single request, process each independently and return an array of results:
```json
[
    {{
        "company_website": "https://company1.com",
        "original_description": "Company 1 description",
        "excel_data": [/* top 2 matches */]
    }},
    {{
        "company_website": "https://company2.com", 
        "original_description": "Company 2 description",
        "excel_data": [/* top 2 matches */]
    }}
]
```

## Final Validation
Before returning results, verify:
- ✅ All record_ids exist in the original excel_data
- ✅ All descriptions are copied exactly from excel_data  
- ✅ Company website and description are preserved exactly
- ✅ Matches are genuinely business-relevant
- ✅ JSON structure is valid and complete

Focus on delivering high-quality, business-intelligent matches that would be valuable for strategic business analysis and decision-making.
"""