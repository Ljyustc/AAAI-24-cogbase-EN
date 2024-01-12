# 将最终的result中的票数较少的 使用GPT-4-Official-EN-vote.json中的结果
import json
with open(r'data\file_to_be_submitted\GPT4_EN_vote_all_verify_may_be_wrong.json') as json_file:
    wrong_result = json.load(json_file)
with open(r'data\result\GPT-4-Official-EN-all.json') as json_file:
    gpt4_result = json.load(json_file)
with open(r'data\file_to_be_submitted\GPT4_EN_vote_all_verify.json') as json_file:
    result = json.load(json_file)

count = {}
for d in wrong_result:
    key = d["key"]
    if d["key"] in gpt4_result and d["vote"] < 20:
        result[key] = gpt4_result[key]
        count[d["vote"]] = count.get(d["vote"],0) + 1
print(count)

count_over_5 = 0
for k in count:
    if k < 20:
        count_over_5 += count[k]
print(count_over_5)
with open(r'C:\Users\mzy\OneDrive - USTC\文档\Codes\aaai2024comp\EN\data\file_to_be_submitted\test.json', 'w',encoding='utf-8') as json_file:
    json.dump(result,json_file,ensure_ascii=False)