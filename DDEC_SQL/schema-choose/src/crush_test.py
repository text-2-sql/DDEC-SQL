import json
from utils import read_pkl_file,create_prompt_schema
from votes import votes

def get_dbs(res:list):
    db_ids = []
    for item in res:
        db_id = item.split(".")[0]
        if db_id not in db_ids:
            db_ids.append(db_id)
    
    return db_ids
    # print(res)

def merge_crush_data(pkl_path,json_path):
    data = read_pkl_file(pkl_path)
    json_data = json.load(open(json_path,'r'))

    assert len(json_data) == len(data),f"length error len_json = {len(json_data)},while len_pkl = {len(data)}"
    for index,(crush,ours) in enumerate(zip(data,json_data)):
        ours['crush_pred'] = crush
    return json_data

def get_db_recall(data,recall_num=-1,key='crush_pred'):
    num = 0
    if recall_num == 0:
        length = len(data)
    else:
        length = recall_num

    for item in data:
        db_ids = get_dbs(item[key][:length])
        if item['db_id'] in db_ids:
            num += 1
    return num 

def crush_res_to_tables(res):
    new_res = []
    for item in res:
        new_item = "&".join(item.split(".")[:2])
        new_res.append(new_item)
    return new_res

def get_vote_recall(data,vote_num):
    num = 0
    print(vote_num)
    for item in data:
        new_res = crush_res_to_tables(item['crush_pred'])
        
        voted_db = votes(new_res,vote_num)
        if voted_db == item["db_id"]:
            num += 1
    return num

def get_table_recalls(data,recall_num=1):
    num = 0
    for item in data:
        tables = [table for table in item['table']]

        pred_tables = ["&".join(table.split(".")[:2]) for table in item["crush_pred"][:recall_num]]
    
        # pred_tables = set(["&".join(table.split(".")[:2]) for table in item["crush_pred"][:recall_num]])
        print(tables)
        print(pred_tables)
        if set(tables) <= set(pred_tables):
            num +=1
        break
    return num

def get_recalls(pkl_path,json_path):
    print(pkl_path)
    data = merge_crush_data(pkl_path,json_path)
    length = len(data)
    print(length)
    table_recalls_num = get_table_recalls(data,recall_num=2)
    print(table_recalls_num/length)
    # 各个列投票
    # vote_recall =  get_vote_recall(data,20)
    # print(f"vote {vote_recall/length}")
    # for i in [15,20]:
    #     print(f"----{i}----")
    #     db_recall = get_db_recall(data,i)
    #     print(db_recall/length)
    for item in data:
        item["crush_pred"] = item["crush_pred"][:10]
        del item["predicted_res"]
    output_path = pkl_path.replace(".pkl",".json")
    json.dump(data,open(output_path,'w'),indent=4)

def get_pred_schemas(pkl_path,json_path,db_path,output_path):
    data = merge_crush_data(pkl_path,json_path)
    

    for pred in data:
        # tables = [".".join(item.split(".")[:2]) for item in pred[:10]]
        
        table_dict = {}
        # init table_dict
        # print(pred["crush_pred"])

        for table in pred["crush_pred"][:10]:
            db_id = table.split(".")[0]
            table_dict[db_id] = []
        # 
        table_names = []
        for table in pred["crush_pred"][:10]:
            print(table)
            db_id = table.split(".")[0]
            table_name = table.split(".")[1]
            if table_name not in table_dict[db_id]:
                table_dict[db_id].append(table_name)
                table_names.append(table_name)
        
        # assert len(set(table_names)) == len(table_names),f"length error!\n{table_names} "
        
        schema = create_prompt_schema(db_path,table_dict)
        pred['schema'] = schema
        pred["crush_pred"] = pred["crush_pred"][:10]
        del pred["predicted_res"]
        
    json.dump(data,open(output_path,'w'),indent=4)

if __name__ == "__main__":
    # crush pkl paths
    bird_dev_pkl_path = "CRUSH_DATA/bird_dev_predicts_openai.pkl"  
    spider_dev_pkl_path = "CRUSH_DATA/spider_dev_predicts_openai.pkl"
    spider_test_pkl_path = "CRUSH_DATA/spider_test_predicts_openai.pkl"
    
    bird_dev_pkl_llama_path = 'CRUSH_DATA/bird/predicts_llama_70b.pkl'
    spider_dev_pkl_llama_path = 'CRUSH_DATA/spider/dev/predicts_llama_70b.pkl'
    spider_test_pkl_llama_path = 'CRUSH_DATA/bird/spider_test_predicts_llama_70b.pkl'
    
    # json.paths
    bird_dev_json_path = "data/bird/predict.json"  
    spider_dev_json_path = 'data/spider/dev/predict.json'
    spider_test_json_path = "data/spider/test/predict.json"

    # db paths
    bird_db_path = '/data/inspur/base_model_exp/test/Bird/dev_tables.json'
    spider_dev_db_path = '/data/inspur/base_model_exp/test/spider_train/tables.json'
    spider_test_db_path = '/data/inspur/base_model_exp/test/Spider/test_data/tables.json'
    # output paths
    bird_output_path = 'CRUSH_DATA/bird/predicts_llama_schema_70b.json'
    spider_dev_output_path = 'CRUSH_DATA/spider/dev/predicts_llama_schema_70b.json'
    spider_test_output_path = 'CRUSH_DATA/spider_test_predicts_llama_schema.json'
    # get bird
    # get_recalls(bird_dev_pkl_llama_path,bird_dev_json_path)
    # get_recalls(spider_dev_pkl_llama_path,spider_dev_json_path)
    # get_recalls(spider_test_pkl_path,spider_test_json_path)

    get_pred_schemas(bird_dev_pkl_llama_path,bird_dev_json_path,bird_db_path,bird_output_path)
    get_pred_schemas(spider_dev_pkl_llama_path,spider_dev_json_path,spider_dev_db_path,spider_dev_output_path)
    # get_pred_schemas(spider_test_pkl_llama_path,spider_test_json_path,spider_test_db_path,spider_test_output_path)
    
    
