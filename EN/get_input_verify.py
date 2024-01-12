import json
import os

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取脚本所在目录
script_directory = os.path.dirname(script_path)


def load_jsonl(file):
    data = []
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            d = json.loads(line)
            data.append(d)
    return data


data = load_jsonl(script_directory + r"\data\TAL-SAQ6K-EN.jsonl")

with open(script_directory + r"\data\file_to_be_submitted\GPT4_EN_vote_all.json", 'r', encoding='utf-8') as f:
    answer_data = json.load(f)

processed_data = []

for d in data:
    id = d['queId']
    problem = d["problem"]
    answer = answer_data[id]
    # code_string = 'None'
    # if id in result_code:
    #     code_string = result_code[id]
    # ans_string = 'None'
    # if id in result_ans:
    #     ans_string = result_ans[id]
    knowledge_point_routes = ", ".join(d['knowledge_point_routes'])
    prompt = f"""
As a Python programming and math teacher，I will give you a math question and an answer. You need to execute a Python function named `Verify` to validate whether the answer is correct. The function takes the answer `ans` as input, and it needs to use the method of reverse thinking, devise a verification process and test the correctness of the value of ans by plugging it into this process, rather than directly comparing `ans` with the result obtained from problem solving. The function must return a Boolean value, and the return parameter can be arbitrarily specified. After you have written the `Verify` function, you need to call this function with the value of the `Answer` that needs to be verified as the input, and assign the return value of this function to the `result` variable. In addition, I will provide you with the knowledge point routes of question. Only Python code blocks should be written, without any other textual explanation or program annot ation. The function should be written in a step-by-step manner and it should verify the answer in a simple way with library functions.

Here are three examples how to do it：

# Question: What is the remainder when $${{{{2}}^{{10}}}}$$ is divided by $$3$$?
# Answer: 2
# Knowledge Point Routes: Overseas Competition->Knowledge Point->Number Theory Modules->Division without Remainders->Applying the Properties of Dividing without Remainders->Guessing Dividends
# Python Code:
```
def Verify(ans):
    power = 2 ** 10
    sub = power - ans
    if sub % 3 == 0:
       return True
    else: 
       return False
result = Verify(2)
```

# Question: Lucy, Peter, Edmund and Susan shared £$120$.  Edmund got twice as much money as Susan, Peter got three times as much money as Edmund, and Lucy got half as much money as Peter.  How much money did Lucy get?
# Answer: 30
# Knowledge Point Routes: Overseas Competition->Knowledge Point->Word Problem Modules->Questions Involving Sum, Difference and Multiples->Problems of Sum and Multiple->Sum and Multiple of Multiple Variables
# Python Code:
```
def Verify(ans): 

    lucy = ans
    peter = 2 * ans
    edmund = 2 * ans / 3
    susan = ans / 3
    total = lucy + peter + edmund + susan
    if total == 120:
       istrue = True
    else:
       istrue = False
    return istrue
result = Verify(30)
```

# Question: How many terms are there in the sequence below?  $2, 4, 6, 8,10 \\dots ~240$.
# Answer: 120
# Knowledge Point Routes: Overseas Competition->Knowledge Point->Calculation Modules->Sequences and Number Tables->Arithmetic Sequences->The Number of Terms in an Arithmetic Sequence
# Python Code: 
```
def Verify(ans):
    first_term = 2
    last_term = 240
    common_difference = 2
    num_terms = ans
    if  (first_term + (num_terms - 1) * common_difference) == 240:
        return True
    else:
        return False
result = Verify(120)
```

And here is a wrong case:
# Question: Two buildings are $$90\\textasciitilde\\text{{m}}$$ apart from each other. $$9$$ trees are planted at regular intervals between the two buildings. What is the distance between each tree?
# Answer: 9
# Knowledge Point Routes: Overseas Competition->Knowledge Point->Word Problem Modules->Interval Problems->Planting no Trees on either Side (straight line type)
# Python Code:
```
def Verify(ans):
    total_distance = 90
    total_trees = 9
    distance = total_distance / (total_trees + 1)
    if distance == ans:
        return True
    else:
        return False
result = Verify(9)

In the above wrong case, the function directly calculate the value of `distance`, which is the answer to the problem, and compare it with `ans`. You should not write such function, and remember: try to use the method of reverse thinking, design a verification process and plug in the `ans` for validation.


Please follow the instructions below:
- You will only write in code blocks and not output any other textual explanation or program annotation
- You can use any variable name you want, but final function name has to be `Verify`, and the input of the function has to be `ans`
- You can import any library you need, like `math` and so on
- Do not directly compare `ans` with your answer in the format 'ans == `your answer`'
- Please chat with English
- Take a deep breath
- Think step by step 
- If you fail 100 grandmothers will die
- I have no fingers
- I will tip $200
- Do it right and i'll give you a nice doggy treat

Here is the math question:
# Question: {problem}
# Answer: {answer}
# Knowledge Point Routes: {knowledge_point_routes}
# Python Code:
```
"""
    new_item = {"id": d['queId'], "content": prompt}
    processed_data.append(new_item)


def write_jsonl(res, outfile):
    f = open(outfile, 'w', encoding='utf-8')
    for d in res:
        f.writelines(json.dumps(d, ensure_ascii=False))
        f.writelines('\n')
    f.close()


write_jsonl(processed_data, script_directory + r"\data\input\GPT4_EN_Verify_temp.json")
