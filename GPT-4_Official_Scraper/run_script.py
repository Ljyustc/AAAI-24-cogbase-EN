import argparse
import subprocess
import sys
import time

# 设置命令行参数
parser = argparse.ArgumentParser(description='Control script to run the inner script.')
parser.add_argument('--num', type=int, default=0, help='Sequential number to select specific data and credentials.')
parser.add_argument('--max_attempts', type=int, default=5, help='Maximum number of attempts to run the script.')
parser.add_argument('--EN_or_CN', type=str, default="EN", help='Select the script path.')
args = parser.parse_args()

# 脚本路径
if args.EN_or_CN == "EN":
    inner_script_path = r"gpt4_scraper_EN.py"
else:
    inner_script_path = r"gpt4_scraper_CN.py"

# 运行内部脚本的函数
def run_inner_script(num, max_attempts):
    attempts = 0

    while attempts < max_attempts:
        print(f"Running the inner script: Attempt {attempts + 1}/{max_attempts}")
        try:
            # 运行内部脚本并等待其完成
            subprocess.run(['python', inner_script_path, '--num', str(num)], check=True)
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
        print("Reached the maximum number of attempts. Inner script did not complete successfully.")

# 运行内部脚本
run_inner_script(num=args.num, max_attempts=args.max_attempts)
