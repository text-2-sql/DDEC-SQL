import json
import random
from crush_test import merge_crush_data

if __name__ == "__main__":
    path = 'data/spider/test/predict.json'
    pkl_path = "CURSH_DATA/spider_test_predicts_openai.pkl"
    sampled_path = 'data/spider/test/predict_sample.json'
    sampled_data = json.load(open(sampled_path,'r'))
    sample_output_path = 'CURSH_DATA/spider_test_predict_sample.json'
    data = merge_crush_data(pkl_path,path)
    new_data = []
    querys = [(item["question"],item["sql_query"]) for item in data]
    for item in sampled_data:
        question_id = querys.index((item["question"],item["sql_query"]))
        new_data.append(data[question_id])
    
    json.dump(new_data,open(sample_output_path,'w'),indent=4)