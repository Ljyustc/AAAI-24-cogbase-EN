import argparse
import os
import subprocess
import sys
import time

# 设置命令行参数
parser = argparse.ArgumentParser(description='Control script to run the inner script.')
parser.add_argument('--num', type=int, default=30, help='Sequential number to select specific data and credentials.')
parser.add_argument('--max_attempts', type=int, default=5, help='Maximum number of attempts to run the script.')
parser.add_argument('--prompt', type=int, required=True, default=0, help='Get python code for answer(0) or verify(1).')
args = parser.parse_args()

# 脚本路径
inner_script_name = r"\gpt_4_runner.py"
# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)
# 获取脚本所在目录
script_directory = os.path.dirname(script_path)
# 获取脚本的绝对路径
inner_script_path = script_directory + inner_script_name


# 运行内部脚本的函数
def run_inner_script(num, max_attempts, prompt):
    attempts = 0

    if prompt == 0:  # 获取求解函数
        for i in range(num):
            print(f"Loop: {i} ...")
            while attempts < max_attempts:
                print(f"Running the inner script: Attempt {attempts + 1}/{max_attempts}")
                try:
                    file_index = f"{i:02}"
                    in_file = r"\data\input\GPT4_EN_PAL_3.json"
                    out_file = rf"\data\output\GPT4_EN_PAL_3_{file_index}.json"
                    # 运行内部脚本并等待其完成，默认执行英文数据集对应的脚本
                    subprocess.run(
                        ['python', inner_script_path, '--in_file', in_file, '--out_file', out_file],
                        check=True)
                    print("Inner script completed successfully.")
                    break  # 如果成功完成，退出循环

                except subprocess.CalledProcessError as e:
                    print(f"Inner script terminated unexpectedly: {e}")
                    attempts += 1  # 如果内部脚本终止，增加尝试次数
                    time.sleep(60)

                except KeyboardInterrupt:
                    print("Control script interrupted by user.")
                    sys.exit(1)

            if attempts >= max_attempts:
                print(
                    f"Reached the maximum number of attempts. Inner script did not complete successfully for Loop {i} ...")
            print(f"Loop {i} complete.")
            print("---------------------------------------------------")
        print("All Loop complete.")
    else:  # 获取验算函数
        while attempts < max_attempts:
            print(f"Running the inner script: Attempt {attempts + 1}/{max_attempts}")
            try:
                in_file = r"\data\input\GPT4_EN_Verify.json"
                out_file = r"\data\output\GPT4_EN_Verify.json"
                # 运行内部脚本并等待其完成，默认执行英文数据集对应的脚本
                subprocess.run(
                    ['python', inner_script_path, '--in_file', in_file, '--out_file', out_file],
                    check=True)
                print("Inner script completed successfully.")
                break  # 如果成功完成，退出循环

            except subprocess.CalledProcessError as e:
                print(f"Inner script terminated unexpectedly: {e}")
                attempts += 1  # 如果内部脚本终止，增加尝试次数
                time.sleep(60)

            except KeyboardInterrupt:
                print("Control script interrupted by user.")
                sys.exit(1)

        if attempts >= max_attempts:
            print(
                f"Reached the maximum number of attempts. Inner script did not complete.")


# 运行内部脚本
run_inner_script(num=args.num, max_attempts=args.max_attempts, prompt=args.prompt)
