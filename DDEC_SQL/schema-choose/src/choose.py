import re
import os
import json
from llm import completion,completion_llama
from utils import prompt_create_table

SPIDER = "spider"
BIRD = "bird"
DEV_MODE = "dev"
TEST_MODE = "test"
GPT = "GPT-4o"
LLAMA = "llama3 401B"

prompt = """
You are given a question and a list of databases with associated tables. Your task is to identify the most relevant database that contain the information needed to answer the question. The question will be related to specific topics that can be mapped to the tables provided. Select the database(s) that most likely contain the data needed to answer the question based on the keywords and context provided.

Question:
{Question}

Databases and Tables:
{Databases}

Output:
Please return the name of the single most relevant database in JSON format as follows:
{
  "selected_database": "database_name",
  "explanation": "Explain why this database was selected."
}
"""

def extract_db_ids(res,key="predicted_res"):
    if key == "predicted_res":
        db_ids = [item.split('&')[0] for item in res]
    elif key == "crush_pred":
        db_ids = set([item.split('.')[0] for item in res])

    # print(db_ids)
    return list(set(db_ids))

def extract_db_name(text):
    sql_query = text
    sql_match = re.search(r'"selected_database": "([^"]+)"', text, re.DOTALL)
    if sql_match:
        sql_query = sql_match.group(1).replace('\\n', '\n')
        sql_query = sql_query.replace("\n","")
    else:
        raise ValueError("extract_error")
    return sql_query

def get_bird_db(db_id):
    db = ""
    db_path = '/data/inspur/base_model_exp/test/Bird/dev_tables.json'
    db_data = json.load(open(db_path,'r'))
    for i,item in enumerate(db_data):
        if item['db_id'] == db_id:
            tables = prompt_create_table(item)
            db =  f"Tables in {db_id} db are below:\n\n" + tables
            # print(db)
            break
    if db == "":
        raise ValueError(f"db{db_id} not found!")
    return db

def get_db(db_id,dataset=BIRD,mode=DEV_MODE):
    db = ""
    if dataset == BIRD:
        db_path = '/data/inspur/base_model_exp/test/Bird/dev_tables.json'
    elif dataset == SPIDER and mode == DEV_MODE:    
        db_path = '/data/inspur/base_model_exp/test/spider_train/tables.json'
    elif dataset == SPIDER and mode == TEST_MODE:
        db_path = '/data/inspur/base_model_exp/test/Spider/test_data/tables.json'
    db_data = json.load(open(db_path,'r'))
    for i,item in enumerate(db_data):
        if item['db_id'] == db_id:
            tables = prompt_create_table(item)
            db =  f"Tables in {db_id} db are below:\n\n" + tables
            # print(db)
            break
    if db == "":
        raise ValueError(f"db:{db_id} not found!")
    return db
    


def choose(path,output_path,dataset="bird",mode="dev",model=GPT,key="predicted_res"):
    data = json.load(open(path,'r'))
    if os.path.exists(output_path):
        new_data = json.load(open(output_path,'r'))
    else:
        new_data = []
    num = 0
    for item in data:
        if num < len(new_data):
            num += 1
            continue
        db = item['db_id']
        query = item["question"]
        res = item[key]
        db_ids = extract_db_ids(res,key)
        print(db_ids)
        db_contents = [get_db(db_id,dataset,mode) for db_id in db_ids]
        db_str = "\n".join(db_contents)
        content = prompt.replace("{Question}",query).replace("{Databases}",db_str)
        
        
        retries = 0
        max_retries = 5
        while retries < max_retries:
            try:
                if model == GPT:
                    result = completion(content)
                elif model == LLAMA:
                    result = completion_llama(content)
                else:
                    raise ValueError(f"{model} model not supported!")
                db_name = extract_db_name(result)
                break
            except Exception as e:
                print(f"An Error {e} has happend")
                retries += 1
                print(f"Attempting Failed.Retrying!{retries}/{max_retries}")
        db_name = extract_db_name(result)
        item['pred db_id'] = db_name
        new_data.append(item)
        print(result)
        print(db_name)
        num += 1
        if num %5 == 0:
            json.dump(new_data,open(output_path,'w'),indent=4)

    json.dump(new_data,open(output_path,'w'),indent=4)


if __name__ == "__main__":
    bird_path = "data/bird/predict.json"
    spider_dev_path = 'data/spider/dev/predict.json'
    spider_test_path = "data/spider/test/predict.json"
    output_bird_path = "output/bird_predict_70b.json"
    output_spider_dev_path = 'output/spider_dev_predict_70b.json'
    output_spider_test_path = 'output/spider_test_predict_70b.json'
    gpt_output_bird_path = "output/bird_gpt_predict.json"
    gpt_output_spider_dev_path = 'output/spider_dev_gpt_predict.json'
    gpt_output_spider_test_path = 'output/spider_test_gpt_predict.json'


    CRUSH_bird_sample_path = 'CRUSH_DATA/bird_predoutput/CRUSH/bird_predict_sampleict_sample.json'
    CRUSH_bird_output_path = '.json'
    CRUSH_spider_dev_sample_path = 'CRUSH_DATA/spider_dev_predict_sample.json'
    CRUSH_spider_dev_output_path = 'output/CRUSH/spider_dev_predict_sample.json'
    CRUSH_spider_test_sample_path = 'CRUSH_DATA/spider_test_predict_sample.json'
    CRUSH_spider_test_output_path = 'output/CRUSH/spider_test_predict_sample.json'
    # choose_by_gpt4(spider_test_path,output_spider_test_path,SPIDER,TEST_MODE)
    # choose(bird_path,gpt_output_bird_path,BIRD,DEV_MODE,GPT)
    # choose(spider_test_path,gpt_output_spider_test_path,SPIDER,TEST_MODE,GPT)
    # choose(spider_dev_path,gpt_output_spider_dev_path,SPIDER,DEV_MODE,GPT)
    choose(bird_path,output_bird_path,BIRD,DEV_MODE,LLAMA)
    choose(spider_test_path,output_spider_test_path,SPIDER,TEST_MODE,LLAMA)
    choose(spider_dev_path,output_spider_dev_path,SPIDER,DEV_MODE,LLAMA)
    # choose_by_llama3(bird_path,output_bird_path,BIRD,DEV_MODE)

    # choose(CRUSH_spider_test_sample_path,CRUSH_spider_test_output_path,SPIDER,TEST_MODE,GPT,"crush_pred")
    # choose(CRUSH_spider_dev_sample_path,CRUSH_spider_dev_output_path,SPIDER,DEV_MODE,GPT,"crush_pred")
    # choose(CRUSH_bird_sample_path,CRUSH_bird_output_path,BIRD,DEV_MODE,GPT,"crush_pred")