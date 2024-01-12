import json
import os
import re

import func_timeout
import tqdm

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取脚本所在目录
script_directory = os.path.dirname(script_path)


def execute_code(code_string: str, keys=None, timeout_duration=5):
    def execute(x):
        try:
            local_namespace = {**locals(), **globals()}
            exec(x, local_namespace, local_namespace)
            if keys is None:
                return local_namespace.get('ans', None)
            else:
                return [local_namespace.get(k, None) for k in keys]
        except Exception as e:
            return f"Error in executing code: {e}"

    try:
        result = func_timeout.func_timeout(timeout_duration, execute, args=(code_string,))
    except func_timeout.FunctionTimedOut:
        result = "Error execution time exceeded the limit"
    except Exception as e:
        result = f"Error during execution: {e}"

    return result


# test = "from sympy import symbols, sin, pi, tan, simplify, solve\n\ndef solution():\n    # We need to find the exact sum of sin(5k) for k from 1 to 35.\n    # Since sin(5k) is periodic with period 360 degrees / 5 = 72,\n    # We can consider the sum of sin(k) from k=1 to k=35*5 with k in degrees.\n    sum_of_sines = sum(sin(5 * k * pi / 180) for k in range(1, 36))\n\n    # Simplify the sum to get an exact form\n    sum_of_sines = simplify(sum_of_sines)\n\n    # Since we know that sum_of_sines = tan(m/n), we can set up an equation\n    m, n = symbols('m n', integer=True)\n    equation = tan(m/n * pi/180) - sum_of_sines\n\n    # Solve the equation for m/n considering the constraint m/n < 90\n    # Which means m < 90n, we use nsolve to get a numerical solution\n    solution = solve(equation, m/n)\n\n    # Since we need m and n to be co-prime and m/n < 90,\n    # we pick the solution which is a rational number less than 90\n    rational_solution = min(s for s in solution if s.is_rational and s < 90)\n\n    # Sum of m and n, where rational_solution = m/n\n    m_val, n_val = rational_solution.as_numer_denom()\n\n    return m_val + n_val" +'\nans = solution()'
# ans = execute_code(test,timeout_duration=15)

def simplify_ans(ans, convert_to_str: bool = True):
    if 'relational' in str(type(ans)):
        return str(ans)
    elif 'numpy' in str(type(ans)):
        if ans.shape == ():
            # scalar value
            ans = round(float(ans), 2)
        else:
            # array value
            ans = round(float(ans[0]), 2)
        if convert_to_str:
            return str(ans)
        else:
            return ans
    elif not ans:
        return None
    else:
        if type(ans) in [list, tuple]:
            if 'sympy' in str(type(ans[0])):
                try:
                    ans = [round(float(x), 5) for x in ans]
                except Exception:
                    ans = [str(x) for x in ans]
            if len(ans) == 1:
                ans = ans[0]
        else:
            if 'sympy' in str(type(ans)):
                try:
                    ans = round(float(ans), 5)
                except Exception:
                    ans = str(ans)
        if convert_to_str:
            if type(ans) is str:
                return ans
            else:
                return str(round(ans, 5))
        else:
            return ans


def floatify_ans(ans):
    if ans is None:
        return None
    elif type(ans) == dict:
        ans = list(ans.values())[0]
    elif type(ans) == bool:
        ans = ans
    elif type(ans) in [list, tuple]:
        if not ans:
            return None
        else:
            try:
                ans = float(ans[0])
            except Exception:
                ans = str(ans[0])
    else:
        try:
            ans = float(ans)
        except Exception:
            if "Error" not in ans:
                # 找到 ans 中的浮点数
                ans = re.findall(r"[-+]?\d*\.\d+|\d+", ans)
                if ans:
                    ans = float(ans[0])
                else:
                    ans = str(ans)
    return ans


# Loop through indexes "06" to "15"
for i in range(0, 30):
    index = f"{i:02}"  # Format index with leading zero

    in_path = script_directory + rf'\data\output\GPT4_EN_PAL_3_{index}.json'
    out_path = script_directory + rf'\data\result\GPT4_EN_PAL_3_{index}.json'

    with open(in_path, 'r', encoding='utf-8') as json_file:
        result_code = json.load(json_file)

    print(len(result_code))
    print("input_path: ", in_path, "output_path: ", out_path)

    result_data = {}
    # Check if file exists
    if os.path.exists(out_path):
        try:
            with open(out_path, 'r', encoding='utf-8') as json_file:
                result_data = json.load(json_file)
        except json.JSONDecodeError:
            print(f"Error reading from {out_path}. File might be empty or corrupted.")
    else:
        print(f"{out_path} does not exist. Starting with an empty list.")

    # Process each id in result_code
    for id in tqdm.tqdm(result_code):
        code_string = result_code[id][0]

        if result_data.get(str(id), None) is not None:
            continue
        print(i, id)
        ans = execute_code(code_string, timeout_duration=5)

        if type(ans) is str:
            ans = simplify_ans(floatify_ans(ans), convert_to_str=True)
        if type(ans) is int:
            ans = min(ans, 12345678901234)
        print(ans)
        result_data[str(id)] = str(ans)
        # Save results
        with open(out_path, 'w', encoding='utf-8') as json_file:
            json.dump(result_data, json_file, ensure_ascii=False)
