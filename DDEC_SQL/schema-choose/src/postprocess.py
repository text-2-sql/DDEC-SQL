import json

if __name__ == "__main__":
    path = 'output/0822/spider_test_predict_70b.json'
    data = json.load(open(path,'r'))
    output_path = "output/0822/spider_test_predict_70b_postprocess.json"
    split_keys = [" db","_db"]
    new_data = []

    for item in data:
        for key in split_keys:
            if key in item["pred db_id"]:
                item["pred db_id"] = item["pred db_id"].split(key)[0]
                break
            tables = []
            for res in item["predicted_res"]:
                if res.split("&")[0] == item["pred db_id"]:
                    tables.append(res)
            item["pred tables"] = tables
        new_data.append(item)
    json.dump(new_data,open(output_path,'w'),indent=4)