import json
from openai import OpenAI
import time
import pandas as pd

client = OpenAI(
    api_key="your own key"
)


prompt = """
You are a SQL expert. Given database schema and the SQL generation description, output final sqlite SQL query.
Example:
Database schema:
CREATE TABLE Examination (
    ID integer,
    Examination Date date,
    aCL IgG real,
    aCL IgM real,
    ANA integer,
    ANA Pattern text,
    aCL IgA integer,
    Diagnosis text,
    KCT text,
    RVVT text,
    LAC text,
    Symptoms text,
    Thrombosis integer,
    foreign key (ID) references Patient(ID)
    )
CREATE TABLE Patient (
    ID integer,
    SEX text,
    Birthday date,
    Description date,
    First Date date,
    Admission text,
    Diagnosis text,
    primary key (ID)
    )
CREATE TABLE Laboratory (
    ID integer,
    Date date,
    GOT integer,
    GPT integer,
    LDH integer,
    ALP integer,
    TP real,
    ALB real,
    UA real,
    UN integer,
    CRE real,
    T-BIL real,
    T-CHO integer,
    TG integer,
    CPK integer,
    GLU integer,
    WBC real,
    RBC real,
    HGB real,
    HCT real,
    PLT integer,
    PT real,
    APTT integer,
    FG real,
    PIC integer,
    TAT integer,
    TAT2 integer,
    U-PRO text,
    IGG integer,
    IGA integer,
    IGM integer,
    CRP text,
    RA text,
    RF text,
    C3 integer,
    C4 integer,
    RNP text,
    SM text,
    SC170 text,
    SSA text,
    SSB text,
    CENTROMEA text,
    DNA text,
    DNA-II integer,
    primary key (ID, Date),
    foreign key (ID) references Patient(ID)
    )
    
SQL description:#1.Scan Table: Retrieve all rows from the [Patient] table aliased as T1.#2.Join the [Examination] table aliased as T2 on the condition that T1.ID equals T2.ID.#3.Reserve rows of #2 where the [SEX] in table T1 is 'F', the year part of [Examination Date] in table T2 is '1997', and [Thrombosis] in table T2 is 1.#4.Select Column: Select the count of rows from the result of #3.

Output SQL:SELECT COUNT(*) FROM Patient AS T1 JOIN Examination AS T2 ON T1.ID = T2.ID WHERE T1.SEX = 'F' AND STRFTIME('%Y', T2.`Examination Date`) = '1997' AND T2.Thrombosis = 1


Now it's your turn.

"""

def completion(instruction):
    max_retries = 100
    retries = 0

    while retries < max_retries:
        try:
            # try api
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": instruction,
                    }
                ],
                model="gpt-4o",
            )

            # success then break
            break

        except Exception as e:
            # print error
            print(f"An error occurred: {e}")
            retries += 1
            # wait and retry
            time.sleep(5)  # wait 5s
            print(f"Retrying... (attempt {retries + 1}/{max_retries})")
    return chat_completion.choices[0].message.content

def completion_llama(instruction):
    max_retries = 100
    retries = 0

    client = OpenAI(
        base_url="base_url_link",
        api_key="EMPTY",
    )
    while retries < max_retries:
        try:
            # try api
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": instruction,
                    }
                ],
                model='meta-llama-3.1-70b-instruct',
            )

            # success then break
            break

        except Exception as e:
            # print error
            print(f"An error occurred: {e}")
            retries += 1
            # wait and retry
            time.sleep(5)  # wait 5s
            print(f"Retrying... (attempt {retries + 1}/{max_retries})")
    return chat_completion.choices[0].message.content