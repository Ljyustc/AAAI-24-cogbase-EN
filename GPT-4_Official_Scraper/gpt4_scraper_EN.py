import argparse
import json
import os
import random
import re
import sys
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# 解析命令行参数
parser = argparse.ArgumentParser(description='Run Selenium-based scraper with different configurations.')
parser.add_argument('--num', type=int, default=0, help='Sequential number to select specific data and credentials.')
args = parser.parse_args()

num = args.num  # 获取命令行传入的num参数

# 账号和密码字典
# 账号和密码字典
credentials = [
    # 账号和密码字典
]

# 选择账号和密码
email_address, password = credentials[num] 


with open(r'TAL-SAQ6K-EN-difficult.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

begin = max(0,22 * num)

end = min(22 * (num + 1),len(data))
data = data[begin:end]

output_file = rf'output\gpt4-answer-EN-{num}.json'
driver_path = r"chromedriver.exe"

# 初始化空列表
data_finished = []
ids_finished = []

# 检查文件是否存在
if os.path.exists(output_file):
    try:
        with open(output_file, 'r', encoding='utf-8') as json_file:
            data_finished = json.load(json_file)
            ids_finished = [item['ids'] for item in data_finished]
    except json.JSONDecodeError:
        print(f"Error reading from {output_file}. File might be empty or corrupted.")
else:
    print(f"{output_file} does not exist. Starting with an empty list.")

result = data_finished


print("len_data:",len(data),"len_result:",len(result))



driver = None

def login_openai(driver, email_address: str, password: str) -> None:
    """Login with your OpenAI account.

    Args:
        driver (uc.Chrome): Selenium Chrome driver
        email_address (str): Your OpenAI email address
        password (str): Your OpenAI password
    """
    # type email_address
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="username"]'))).send_keys(email_address)

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[name="action"]'))).click()

    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))).send_keys(password)

    continue_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-action-button-primary="true"]')))
    continue_button.click()

def send_prompt(driver, prompt: str, max_attempts: int = 5) -> None:
    """Send prompt to ChatGPT."""
    attempts = 0  # 初始化尝试次数

    while attempts < max_attempts:
        try:
            textarea = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#prompt-textarea")))
            textarea.clear()
            time.sleep(random.uniform(0.5, 1))  # Slight delay for UI to register clear
            textarea.send_keys(prompt)
            time.sleep(random.uniform(0.5, 1))  # Wait for text to be fully entered

            # Wait until the button is clickable
            submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.absolute")))
            submit_button.click()  # Click the submit button
            break  # 如果点击成功，退出循环

        except Exception as e:
            print(f"Attempt {attempts + 1}/{max_attempts}: Unexpected error: {e}. Retrying...")
            fresh_page(driver)  # 出现其他异常，刷新页面并重试

        attempts += 1  # 增加尝试次数

    if attempts >= max_attempts:
        print("Reached the maximum number of attempts. Unable to submit the prompt.")
        sys.exit(1)


def fresh_page(driver):
    max_refresh_hours = 3  # 最大刷新时间为3小时
    refresh_interval = 15*60  # 每15分钟刷新一次
    start_time = time.time()

    while True:
        try:
            
            driver.refresh()
            time.sleep(1)
            # 等待直到#prompt-textarea元素可见并且可被交互
            textarea = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#prompt-textarea")))
            textarea.send_keys("test message")
            time.sleep(random.uniform(3, 5))
            submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.absolute")))
            submit_button.click()
            time.sleep(random.uniform(3, 5))  # Wait for text to be fully entered
            if "usage cap for GPT-4" not in driver.page_source:
                print("已经找到#prompt-textarea并可以输入，完成刷新")
                break  # 成功找到元素并且可交互，退出循环
            else:
                print("You've reached the current usage cap for GPT-4,等待刷新")

        except Exception as e:
            print(f"Error: {e}, 在指定时间内未找到#prompt-textarea或者不可交互，尝试刷新。")
        
        # 计算已经刷新的时间
        current_time = time.time()
        elapsed_time = current_time - start_time

        # 如果超过最大刷新时间，则退出循环
        if elapsed_time > max_refresh_hours * 3600:
            print("已经刷新了最大允许时间，仍然未找到#prompt-textarea或者不可交互，退出刷新。")
            sys.exit(1)
            break

        print(f"页面刷新中，已经刷新了 {int(elapsed_time / 60)} 分钟...")
        time.sleep(refresh_interval)  # 等待一定时间后再次尝试


def get_gpt_response(driver, ids ,timeout: int = 600) -> str:
    """Get GPT response with a timeout.

    Args:
        driver: Selenium WebDriver instance.
        timeout (int, optional): Timeout in seconds. Defaults to 600.

    Returns:
        str: GPT response text.
    """
    # Temporarily disable implicit wait
    driver.implicitly_wait(5)
    time.sleep(random.uniform(5, 5))

    if "usage cap for GPT-4" in driver.page_source:
        print("You've reached the current usage cap for GPT-4, please try again after")
        fresh_page(driver)
        return "None"
    
    max_attempts = 10
    attempts = 0
    while attempts < max_attempts:
        try:
            # Wait until the "Stop generating" button disappears or timeout is reached
            stop_button_xpath = '//button[@aria-label="Stop generating"]'
            WebDriverWait(driver, timeout).until_not(EC.presence_of_element_located((By.XPATH, stop_button_xpath)))
        except Exception as e:
            print(f"Timeout reached after {timeout} seconds.")
            fresh_page(driver)
            return "None"

        if "an error generating a response" not in driver.page_source:
            # If no error, break the loop and proceed to gather the response
            break

        print("There was an error generating a response, trying to regenerate.")
        regenerate_button_xpath  = "//div[text()='Regenerate']"  # Update this XPath as needed
        try:
            # Attempt to click the regenerate button
            regenerate_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, regenerate_button_xpath))
            )
            regenerate_button.click()
            time.sleep(random.uniform(0.5, 5))  # 随机等待时间
        except Exception as e:
            print("Error {e}, Unable to find or click the regenerate button.Refreshing the page.")
            fresh_page(driver)
            return "None"

        # print("There was an error generating a response, trying to refresh.")
        # fresh_page(driver)
        # return "None"
        
        attempts += 1

    if attempts == max_attempts:
        print("Max attempts reached. Unable to generate a valid response.")
        fresh_page(driver)
        return "None"
    driver.refresh()
    time.sleep(random.uniform(5, 5))
    def auto_sleep ():
        id_string = f'''"{ids}"'''
        timeout = 60
        start_time = time.time()
        while True:
            # Check if the ID is in the page source
            if id_string in driver.page_source:
                print("the id is in the page_source")
                time.sleep(5)  # Adjust the sleep time as needed
                break  # Exit the loop if the ID is found

            # Check if the timeout has been reached
            if time.time() - start_time > timeout:
                print("there is no id  in the page_source")
                break  # Exit the loop if the timeout is reached
            # Wait a short period before checking again to avoid overwhelming the CPU
            time.sleep(5)  # Adjust the sleep time as needed
    auto_sleep()
    try:
        # Wait for the elements to be present
        all_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".w-full.text-token-text-primary"))
        )

        last_element = all_elements[-1] if all_elements else None
        time.sleep(random.uniform(1, 5))  # 随机等待时间
        # if last_element:
        #     # Wait for the assistant elements within the last element to be present
        #     assistant_elements = WebDriverWait(last_element, 10).until(
        #         EC.presence_of_all_elements_located((By.XPATH, ".//div[@data-message-author-role='assistant']"))
        #     )
        #     for element in assistant_elements:
        #         results.append(element.text)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


    return last_element.text


def click_to_gpt4(driver, max_retries=5):
    """尝试点击元素，如果超时则刷新页面并重试。

    Args:
        driver: WebDriver实例。
        xpath: 元素的XPATH。
        max_retries: 最大重试次数。
    """
    attempts = 0
    while attempts < max_retries:
        try:
            # 等待第一个元素可点击并点击
            first_element = WebDriverWait(driver, 150).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'group') and contains(@class, 'cursor-pointer')]"))
            )
            first_element.click()
            time.sleep(random.uniform(1, 5))  # 随机等待时间

            # 等待第二个元素可点击并点击
            second_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.flex.items-center.gap-3"))
            )
            second_element.click()
            time.sleep(random.uniform(3, 5))  # 随机等待时间
            return  # 如果成功点击，退出函数
        except Exception as e:
            print(f"点击元素超时，正在尝试第{attempts + 1}/{max_retries}次重试。")
            fresh_page(driver)  # 调用刷新函数
            attempts += 1

    print("超过最大重试次数，未能点击元素。")
    sys.exit(1)


options = uc.ChromeOptions()


# 以下为selenium模拟操作
driver = uc.Chrome(driver_executable_path=driver_path,options=options)
driver.implicitly_wait(10)
driver.get('https://chat.openai.com/')

#！ 登录
WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="login-button"]'))).click()

login_openai(driver=driver,email_address=email_address,password=password)
time.sleep(random.uniform(5, 5))

click_to_gpt4(driver=driver)
# driver.get('https://chat.openai.com/g/g-skneMyAeF-math-solver')



# fresh_page(driver=driver)

count = 0
index = begin
for item in data:
    index += 1
    ids = item['queId']
    if ids in ids_finished:
        continue
    problem = item["problem"]
    prompt = f"""As a Python programming and math teacher, I would like you to solve the following math question. Let's think things through one step at a time. To `solve` the problem using code interpreter step by step, and should `verify` your answer using code interpreter. Please alternately perform the `solve` and `verify` process in the iteration until the answer is proved to be correct. Finally, kindly output the result number without any units with the key `id` and `question_answer` in json format. Please follow the guidelines: - Use English language for communication. - Take a moment to relax and compose yourself. -  Try to use `sympy` and `math` or other libraries to make the solution easier. - must output the `id` and `question_answer` in json. Here is the math problem you need to solve: `id`: '{ids}' ; `problem`: {problem}"""
    print("count: ",count," ids: ",ids,"remain_ques:",len(data)-len(result))
    print("begin:",begin,"end:",end,"index:",index)
    send_prompt(driver=driver,prompt=prompt)
    answer = get_gpt_response(driver=driver,ids = ids)

    pattern = r'"question_answer":\s*(-?\d+(\.\d+)?)(?=\s*})'
    matches = re.findall(pattern, answer)
    if matches:
        result.append({"ids": ids, "answer": matches[-1][0]})
        count += 1
        print(ids,matches[-1][0])
        with open(output_file, 'w',encoding='utf-8') as json_file:
            json.dump(result,json_file,ensure_ascii=False)
    else:
        print(ids,"gpt responese has no question_answer, pass~")
    time.sleep(random.uniform(5, 5))

driver.close()



for d in data:
    id = d['queId']
    if id not in result:
        print(f"id {id} 没有产生结果，重来！")
        sys.exit(1)

print("大成功！！！")