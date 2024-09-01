import json 

path = 'output/DDEC/bird_predict_llama3_schema_70b.json'

data = json.load(open(path,'r'))
for item in data:
    item['pred db_id'] = item['db_id']

json.dump(data,open(path,'w'),indent=4)