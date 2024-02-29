import sys
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime

def convert_date_format(input_date):
    date_obj = datetime.datetime.strptime(input_date, "%Y%m%d")
    # 将日期对象转换为页面需要的格式：YYYY-MM-DD
    formatted_date = date_obj.strftime("%Y-%m-%d")

    return formatted_date

# 从https://www.11meigui.com/tools/currency 爬取货币代码与名称的映射关系
def get_currency_mapping():
    url = "https://www.11meigui.com/tools/currency"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        # print("HTML Content:", soup)  # 调试语句，输出网页内容
        currency_mapping = {}
        tables = soup.find_all("table")
        # print(tables)
        for table in tables:
            rows = table.find_all("tr")
            # print(rows)
            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 5:
                    currency_code = cells[4].text.strip()
                    currency_name = cells[1].text.strip()
                    currency_mapping[currency_code] = currency_name
        return currency_mapping
    else:
        print("Failed to fetch currency mapping from website.")
        return None

# 货币代码和名称的映射字典
currency_mapping = get_currency_mapping()
# print("Currency Mapping:", currency_mapping)  # 调试语句，输出货币映射字典
def fetch_exchange_rate(date, currency_code):
    if not currency_mapping or currency_code not in currency_mapping:
        print("Unsupported currency code.")
        return
    
    # 将货币代码转换为货币名称
    currency_name = currency_mapping[currency_code]
    
    # 设置 ChromeDriver 路径（已添加进PATH）
    
    # 创建 Chrome WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 设置无头模式
    # 初始化Chrome浏览器
    driver = webdriver.Chrome(options=chrome_options)    

    try:
        # 打开中国银行外汇牌价网站
        driver.get("https://www.boc.cn/sourcedb/whpj/")

        # 等待日期输入框可见 输入日期
        date_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "erectDate"))) 
        date_input.clear()
        date_input.send_keys(date)

        # 等待日期输入框可见
        date_input2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "nothing")))
        date_input2.clear()
        date_input2.send_keys(date)
        
        # 选择货币名称
        currency_select = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "pjname")))
        currency_select.send_keys(currency_name)
        
        # 等待查询按钮可点击
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "search_btn")))
        
        # 点击查询按钮
        search_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "search_btn")))
        # driver.execute_script("arguments[0].click();", search_button)
        driver.execute_script("executeSearch();")
        time.sleep(1)
        driver.switch_to.window(driver.window_handles[0])
        
        # 获取现汇卖出价
        exchange_rate_element = driver.find_element(By.XPATH, "//div[@class='BOC_main publish']/table//tr[2]/td[4]")
        exchange_rate = exchange_rate_element.text

        # 将结果写入文件
        with open("result.txt", "a") as f:
            f.write(f"Date: {date}\n")
            f.write(f"Currency Code: {currency_code}\n")
            f.write(f"Exchange Rate: {exchange_rate}\n")

        return exchange_rate
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    # finally:
    #     # 关闭 WebDriver
    #     driver.quit()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 R1.py <date> <currency_code>")
        sys.exit(1)
    
    date = sys.argv[1]
    formatted_date = convert_date_format(date)
    currency_code = sys.argv[2]
    
    exchange_rate = fetch_exchange_rate(formatted_date, currency_code)
    if exchange_rate:
        print(exchange_rate)
