import json
import mimetypes
import random
import re
from urllib.parse import urlparse, urljoin, urlsplit
from sentry.settings import FINGERPRINT_LIST_PATH, USER_AGENT_DICT_PATH
# from app.task import celery_app
import requests
from bs4 import BeautifulSoup


# @celery_app.task
def web_crawler_action(start_url):
    if (not start_url.startswith("http://")) and (not start_url.startswith("https://")):
        start_url = "http://" + start_url
    resp = requests.get(start_url)
    parsed_url = urlparse(start_url)
    base_domain = parsed_url.netloc

    link_tree = {
        # 'url': urlparse(start_url).path,
        'url': base_domain,
        'out_domain': [],
        'fingerprint': [],
        'children': []
    }
    # link_tree = json.dumps(link_tree_none)

    with open(FINGERPRINT_LIST_PATH, 'r', encoding='utf-8') as f:
        data = f.read()
        parsed_data = json.loads(data)

    def read_user_agents_from_file(file_path=USER_AGENT_DICT_PATH):
        with open(file_path, 'r') as file:
            user_agents = [line.strip() for line in file.readlines()]
        return user_agents

    UserAgent = read_user_agents_from_file(file_path=USER_AGENT_DICT_PATH)

    def generate_random_headers(user_agents):
        referers = [
            'https://www.google.com/',
            'https://www.bing.com/',
        ]

        languages = [
            'en-US,en;q=0.9',
            'zh-CN,zh;q=0.8',
        ]

        headers = {
            'User-Agent': random.choice(user_agents),
            'Referer': random.choice(referers),
            'Accept-Language': random.choice(languages),
        }

        return headers

    # 正则匹配敏感信息
    def extract_contact_info(soup):
        phone_numbers = re.findall(r'\b\d{10,12}\b', soup.get_text())
        email_addresses = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())
        return phone_numbers, email_addresses

    def draw_link_tree(url, path, data, link_tree):
        data_set = {
            'path': data['path'],
            'phone_numbers': data['phone_numbers'],
            'email_addresses': data['email_addresses'],
            'code': data['code'],
            'title': data['title'],
            # 'out_domain': data['out_domain'],
            'children': [],
        }

        path_components = path.rstrip('/').split('/')
        print("path: " + str(path_components))
        current_node = link_tree

        for component in path_components[:-1]:
            # Check if the component already exists in children
            existing_node = next((child for child in current_node['children'] if child['path'] == component), None)
            if existing_node:
                current_node = existing_node
            else:
                if component == 'http:' or component == 'https:' or component == '' or component == base_domain:
                    continue

                resp = requests.get(url)
                code = resp.status_code
                new_node = {
                    'path': component,
                    'phone_numbers': [],
                    'email_addresses': [],
                    'code': code,
                    'title': '',
                    # 'out_domain': [],
                    'children': []
                }
                current_node['children'].append(new_node)
                current_node = new_node

        current_node['children'].append(data_set)

        return link_tree

    # 指纹识别
    def fingerprint_detector(resp):
        for dict in parsed_data:
            if 'keyword' not in dict or not dict['keyword']:
                continue  # 如果关键字不存在或为空，跳过当前迭代
            for keyword in dict['keyword']:
                escaped_input = re.escape(keyword)
                pattern = re.compile(escaped_input)
                # print(keyword)
                # print(resp)
                match = pattern.search(resp)
                if not match:
                    break
            if match:
                hint = dict['name']
                # print(pattern)
                return hint
        return ''

    # cralwer:
    def cralwer(current_url, base_domain, visited, link_tree, ua=UserAgent):
        # 判断是否爬行与下一步处理
        if current_url in visited:
            return
        # 添加已爬名录
        visited.add(current_url)

        # 处理 url 链接, 待用作比对
        parser_current_url = urlparse(current_url)
        domain = parser_current_url.netloc

        # 纯净url链接. 构建一个新的ParseResult对象，去掉query和fragment部分 #***
        # new_parsed_url = parsed_url._replace(query='', fragment='', params='')
        # print("new: " + str(new_parsed_url))

        # 比对是否本域名链接
        if not domain == base_domain:
            print(f"External link found: {current_url}")
            link_tree['out_domain'].append(current_url)
            return  # **********

        try:
            # 发包请求
            headers = generate_random_headers(ua)
            response = requests.get(current_url, headers=headers)

            code = resp.status_code

            # 排除非网页文件
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                print(f"Skipping non-HTML content at {current_url}")
                return

            soup = BeautifulSoup(response.text, 'html.parser')
            # 正则匹配敏感信息
            phone_numbers, email_addresses = extract_contact_info(soup)

            # 提取当前页面链接, 进入递归
            for link in soup.find_all('a', href=True):
                # 取消对于锚点的跟进
                if '#' in link['href']:
                    continue
                # 取消对于 java 锚点的跟进
                if link.get('href').startswith('java'):
                    continue
                path = link['href']
                # 新获取的绝对 url
                absolute_url = urljoin(start_url, path)
                # print("absolute url: " + absolute_url)
                # 排除已访问
                if absolute_url in visited:
                    continue
                # print("now visit " + absolute_url)
                # 排除非网页文件
                linked_content_type, _ = mimetypes.guess_type(absolute_url)
                if linked_content_type and 'text' not in linked_content_type:
                    # print(f"Skipping non-HTML content at {absolute_url}")
                    continue

                # 判断是否站内, 站内递归
                if urlsplit(absolute_url).netloc == base_domain:
                    # fingerprint = fingerprint_detector(response.text)
                    data = {
                        'path': path,
                        # 'path': path,
                        'phone_numbers': phone_numbers,
                        'email_addresses': email_addresses,
                        'code': code,
                        'title': soup.title.text.strip() if soup.title else 'Untitled',
                        # 'out_domain': [],
                        'children': [],
                    }

                    # print("new data is: " + str(data))
                    print("new from: " + absolute_url)
                    print("new data: " + str(data))
                    link_tree = draw_link_tree(absolute_url, path, data, link_tree)
                    # print("link_tree is: " + str(link_tree))
                    cralwer(absolute_url, base_domain, visited, link_tree)
                # 外站跳过
                else:
                    print(f"External link found: {absolute_url}")
                    # link_tree['out_domain'].append(absolute_url)
                    if absolute_url not in link_tree['out_domain']:
                        link_tree['out_domain'].append(absolute_url)
                    continue

        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")

        return link_tree

    # 开始调用
    UserAgent = read_user_agents_from_file(file_path=USER_AGENT_DICT_PATH)
    response = requests.get(start_url)
    fingerprint = fingerprint_detector(response.text)
    link_tree['fingerprint'] = fingerprint

    final_result = cralwer(current_url=start_url, base_domain=base_domain, visited=set(), link_tree=link_tree,
                           ua=UserAgent)

    link_tree_json = json.dumps(final_result, ensure_ascii=False)


    print(link_tree_json)
    return link_tree_json
    # return final_result

if __name__=='__main__':
    link_tree_json = web_crawler_action('https://www.igetq.com/')
    print("--------------------------------" + '\n' + link_tree_json)