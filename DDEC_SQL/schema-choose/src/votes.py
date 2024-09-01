import json
from utils import read_pkl_file
def votes(pred:list,vote_num=2):
    vote_dict = {}
    tables = [item.split('&')[0] for item in pred][:vote_num]
    for table in tables:
        if table not in vote_dict.keys():
            vote_dict[table] = 1
        else:
            vote_dict[table] += 1
    
    max_value = None
    max_key = None
    for key, value in vote_dict.items():
        if max_value is None or value > max_value:
            max_value = value
            max_key = key

    return max_key

def res_vote():
    path = "data/spider/test/predict.json"
    data = json.load(open(path,'r'))
    vote_dict = {}
    for i in range(10):
        vote_dict[i+1] = 0
    
    for index,item in enumerate(data):
        # print(f"-------{index}------------")
        res = item["predicted_res"]
        tables = item['table']
        table = tables[0].split("&")[0]
        for key, value in vote_dict.items():
            vote_tables = [item.split('&')[0] for item in res][:int(key)]
            # voted_table = votes(res,int(key))
            # if voted_table == table:
            if table in vote_tables:
                vote_dict[key] += 1
        
    for key, value in vote_dict.items():
        print(f"{round(value *1.0 /len(data) *100,2)}")

def test_pred_db(test_path,pred_key="predicted_res",test_key="pred db_id",):
    num = 0
    all_num = 0
    
    data = json.load(open(test_path,'r'))
    for item in data:
        if item['db_id'] in item[test_key].split(" db")[0]:
            num += 1
        for db in item[pred_key]:
            if pred_key == "predicted_res":
                db_id = db.split("&")[0]
            else:
                db_id = db.split(".")[0]
            if item['db_id'] in db_id:
                all_num += 1
                break
    print(all_num/len(data),num/len(data))

if __name__ == "__main__":


    test_pred_db("output/0822/bird_predict_70b_postprocess.json")
    test_pred_db("output/0822/spider_dev_predict_70b_postprocess.json")
    test_pred_db("output/0822/spider_test_predict_70b_postprocess.json")

    # test_pred_db("output/CRUSH/spider_test_predict_sample.json",pred_key="crush_pred")
    # test_pred_db("output/CRUSH/spider_dev_predict_sample.json",pred_key="crush_pred")
    # test_pred_db("output/CRUSH/bird_predict_sample.json",pred_key="crush_pred")
    