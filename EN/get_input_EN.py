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

processed_data = []

for d in data:
    id = d['queId']
    problem = d["problem"]

    knowledge_point_routes = ", ".join(d['knowledge_point_routes'])
    prompt = f"""As a Python programming and math teacher, solve the following math question by implementing a Python function named `solution`. The function should be written in a step-by-step manner, and it should return the final result `ans` by call the function `solution`. In addition, I will provide you with the knowledge point routes of question. Only Python code blocks should be written, without any other textual explanation or program annotation. You should solve the question in a simple way with library functions.

Here are three examples how to do it：

# Question: If we want to divide $15$ pieces of candy into $4$ piles with different numbers in each pile, how many different ways can we divide them?
# Knowledge Point Routes: Overseas Competition->Knowledge Point->Counting Modules->Permutations and Combinations->Combinations", "Overseas Competition->Knowledge Point->Counting Modules->Questions Involving Enumeration->Splitting Whole Numbers
# Python Code:
```
def solution():
    count = 0
    for x1 in range(1, 15):
        for x2 in range(1, 15):
            for x3 in range(1, 15):
                for x4 in range(1, 15):
                    if x1 + x2 + x3 + x4 == 15 and len(set([x1, x2, x3, x4])) == 4:
                        count += 1
    return count

ans = solution()
```

# Question: Lucy, Peter, Edmund and Susan shared £$120$.  Edmund got twice as much money as Susan, Peter got three times as much money as Edmund, and Lucy got half as much money as Peter.  How much money did Lucy get?
# Knowledge Point Routes: Overseas Competition->Knowledge Point->Word Problem Modules->Questions Involving Sum, Difference and Multiples->Problems of Sum and Multiple->Sum and Multiple of Multiple Variables
# Python Code:
```
from sympy import symbols, Eq, solve
def solution():
    

    lucy, peter, edmund, susan = symbols('lucy peter edmund susan')

    equation1 = Eq(edmund, 2 * susan)
    equation2 = Eq(peter, 3 * edmund)
    equation3 = Eq(lucy, peter / 2)
    equation4 = Eq(lucy + peter + edmund + susan, 120)

    solutions = solve((equation1, equation2, equation3, equation4), (lucy, peter, edmund, susan))

    return solutions[lucy]

ans = solution()
```

# Question: How many terms are there in the sequence below?  $2, 4, 6, 8,10 \\dots ~240$.
# Knowledge Point Routes: Overseas Competition->Knowledge Point->Calculation Modules->Sequences and Number Tables->Arithmetic Sequences->The Number of Terms in an Arithmetic Sequence
# Python Code:
```
def solution():
    first_term = 2
    last_term = 240
    difference = 2

    num_terms = ((last_term - first_term) / difference) + 1

    return int(num_terms)

ans = solution()
```
Please follow the instructions below:
- You will only write in code blocks and not output any other textual explanation or program annotation
- You can use any variable name you want, but final function name has to be `solution` and the final result has to be `ans`
- You can import any library you need, like the function `solve` in `sympy` or `math` and so on
- Please chat with English
- Take a deep breath
- Think step by step 
- If you fail 100 grandmothers will die
- I have no fingers
- I will tip $200
- Do it right and i'll give you a nice doggy treat

Here is the math question:
# Question: {problem}
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


write_jsonl(processed_data, script_directory + r"\data\input\GPT4_EN_PAL_4.json")
