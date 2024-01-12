import argparse
import json
import os
import sys

import requests

# 解析命令行参数
parser = argparse.ArgumentParser(description='Run gpt4_api-based script with different configurations.')
parser.add_argument('--in_file', type=str, required=True, default=None, help='in_file_path')
parser.add_argument('--out_file', type=str, required=True, default=None, help='out_file_path')

args = parser.parse_args()
data_file = args.in_file
out_file = args.out_file

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取脚本所在目录
script_directory = os.path.dirname(script_path)
# 获取文件的绝对路径
data_file = script_directory + data_file
out_file = script_directory + out_file

# 获取 API KEY 和 API BASE
api_key = os.environ.get("OPENAI_API_KEY").split(';')[0]  # 存在多个api_key
api_url = os.environ.get("OPENAI_API_BASE") + r'/chat/completions'

# 运行前需要确保运行环境中存在对应的环境变量，或者通过修改以下代码
# ********************************************************* #
# api_key = "your_api_key"
# api_url = "your_api_url"
# ********************************************************* #

if api_key is None or api_url is None:
    print("API info not found in environment variables.")

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}


def load_prompts(file_name):
    """
    Args:
        file_name: 输入文件的文件名（需要包含路径）

    Returns:
        从输入文件中读取的json串列表
    """
    data = []
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line))
    return data


def write_answer(out_file_name: str, answers_dict: dict):
    """
        Args:
            file_name: 输出文件的文件名（需要包含路径）

        Returns:
            空
    """
    with open(out_file_name, 'w', encoding='utf-8') as file:
        json.dump(answers_dict, file, ensure_ascii=False, indent=4)
    return


def read_json_file(file_path):
    """
    读取包含一个 JSON 串的文件，并返回解析后的字典对象。

    Args:
    - file_path (str): JSON 文件路径。

    Returns:
    - dict: 解析后的字典对象。如果文件不存在返回 None，如果 JSON 串为空返回空字典。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            if not content:
                # JSON 串为空，返回空字典
                return {}

            # 解析 JSON 串
            return json.loads(content)

    except FileNotFoundError:
        # 文件不存在，返回 None
        return None
    except json.JSONDecodeError:
        # JSON 解码失败，可能是文件内容不是有效的 JSON 串
        print(f"Error: Unable to decode JSON from {file_path}.")
        return None


def get_result(prompt):
    """
    Args:
        prompt: 要发送给模型的提示词

    Returns:
        如果结果有效则返回，否则返回None
    """
    data = {
        "model": 'gpt-4',
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    result = None

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data))

        # 检查网络请求是否成功
        response.raise_for_status()

        if response.status_code == 200:
            result = response.json()["choices"][0]["message"]["content"]
            return result
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None


if __name__ == '__main__':
    datas = load_prompts(data_file)
    last_run = read_json_file(out_file)
    answers = {}

    # 上次运行已经写入了部分内容，则先读取上次运行的结果
    if last_run is not None and last_run:
        answers = last_run
        # 只需要考虑那些还没有获取到回复的prompt
        datas = [d for d in datas if d['id'] not in last_run.keys()]

    # 处理回复
    for one in datas:
        answer = get_result(one['content'])
        if answer is None:
            sys.exit(1)  # 子进程执行出错
        if answer.startswith('```python') and answer.endswith('```'):
            # 去除前后缀的```python```
            answer = answer[9:-3].strip()
        answers[one['id']] = [answer]

    write_answer(out_file, answers)
    sys.exit(0)

# 下面是一个带进度条的版本
# if __name__ == '__main__':
#     datas = load_prompts(data_file)
#     unprocessed_datas = datas
#     last_run = read_json_file(out_file)
#     answers = {}
#
#     # 上次运行已经写入了部分内容，则先读取上次运行的结果
#     if last_run is not None and last_run:
#         last_key = list(last_run.keys())[-1]
#         answers = last_run
#         # 只需要考虑那些还没有获取到回复的prompt
#         unprocessed_datas = [d for d in datas if d['id'] not in last_run.keys()]
#
#     # 处理回复
#     for one in tqdm(datas, desc=f"Processing...", ncols=100, file=sys.stdout):
#         if one not in unprocessed_datas:
#             continue

#         answer = get_result(one['content'])
#         if answer is None:
#             sys.exit(1)  # 子进程执行出错
#         if answer.startswith('```python') and answer.endswith('```'):
#             # 去除前后缀的```python```
#             answer = answer[9:-3].strip()
#         answers[one['id']] = [answer]
#
#     write_answer(out_file, answers)
#     sys.exit(0)
