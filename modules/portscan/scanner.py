from sentry.settings import PORT_SCAN_CONF_PATH
import json
from scapy.all import *
from scapy.layers.inet import *


#  功能函数1
#  原理：DNS 解析查询
#  功能：域名解析IP
def get_ip_from_hostname(hostname):
    """
    :param hostname: 目标主机域名
    :return: 解析成功：ip/解析失败：None
    """
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.gaierror:
        print("无法解析域名 {}".format(hostname))
        return None


#  功能函数2
#  原理：icmp(ping)探针
#  功能：ip存活判断
def icmp_ping_ip(ip, icmp_logic):
    """

    :param ip: 目标主机ip
    :param icmp_logic: 端口扫描逻辑链开关，默认ip扫描不进入逻辑链
    :return: 存活状态：flag(True/False)
    """

    flag = False
    p = IP(dst=ip) / ICMP()
    # 发包
    reply = sr1(p, timeout=2, verbose=0)
    # 判断回复
    if icmp_logic == 'on':
        if reply and reply.haslayer(ICMP) and reply[ICMP].type == 0:
            print("IP地址 {} 存活".format(ip))
            flag = True
            return flag
        else:
            print("IP地址 {} 无回应".format(ip))
            flag = True
            return flag
    elif icmp_logic == 'off':
        if reply and reply.haslayer(ICMP) and reply[ICMP].type == 0:
            print("IP地址 {} 存活".format(ip))
            flag = True
            return flag
        else:
            print("IP地址 {} 无回应".format(ip))
            return flag


#  功能函数3
#  原理：tcp(半开放)探针  (判断tcp响应消息的标志位)(SYN-ACK open,RST closed)
#  功能：端口存活扫描
def syn_port_scan(target_ip, ports):
    """

    :param target_ip: 目标ip
    :param ports: 端口列表
    :return: 存活端口列表,端口状态列表
    """

    open_ports = []
    ports_state = []

    for port in ports:

        pkt = IP(dst=target_ip) / TCP(dport=int(port), flags="S")
        # 发包并接收到响应
        reply = sr1(pkt, timeout=1, verbose=0)
        # 判断是否收到TCP ACK消息
        if reply and reply.haslayer(TCP):
            if reply[TCP].flags == 0x12:  # TCP SYN-ACK
                #  SYN-ACK 端口开放
                open_ports.append(port)
                ports_state.append('open')
                # print(f"端口 {port} 开放")
            elif reply[TCP].flags == 0x14:  # TCP RST
                #  RST重置 端口关闭
                pass
            else:
                pass
        else:
            pass

    return open_ports, ports_state


#  功能函数4
#  原理：udp扫描  (基于响应消息的判断)
#  UDP响应包：open  无响应：open|filtered  ICMP错误消息：closed|filtered
#  功能：端口存活扫描
def udp_port_scan(target_ip, ports):
    """

    :param target_ip: 目标ip
    :param ports: 端口列表
    :return: 端口列表  端口状态列表
    """
    ports_state = []
    open_filter_ports = []
    # 循环目标端口列表扫描
    for port in ports:

        udp_packet = IP(dst=target_ip) / UDP(dport=int(port))
        res = sr1(udp_packet, timeout=1, verbose=0)
        if res is not None:
            if res.haslayer(ICMP):
                icmp_f = res.getlayer(ICMP).fields

                # ICMP 端口无法访问错误（类型 3，代码 3）
                if icmp_f["type"] == 3 and icmp_f["code"] == 3:
                    pass
                    # state = 'closed'

                # 其他 ICMP 无法访问错误
                else:
                    open_filter_ports.append(port)
                    ports_state.append('filtered')
                    # state = 'filtered'

            # 来自目标端口的UDP响应
            elif res.haslayer(UDP):
                open_filter_ports.append(port)
                ports_state.append('open')
                # state = 'open'

        # 未收到响应
        elif res is None:
            open_filter_ports.append(port)
            ports_state.append('open|filtered')

        #     pass
        #     后续优化，设置重传
        #     state = 'open|filtered'

    return open_filter_ports, ports_state


# 功能函数5
# 原理：tcp(全连接)探针  (发送ACK（确认）数据包，完成三次握手过程 open)
# 功能：端口存活扫描
def connect_port_scan(ip, ports):
    """

    :param ip: 目标ip
    :param ports: 端口列表
    :return: 存活端口列表 端口状态列表
    """
    open_ports = []
    ports_state = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        connect_response = sock.connect_ex((ip, port))
        # connect_ex 返回值为零表示端口开放
        if connect_response == 0:
            open_ports.append(port)
            ports_state.append('open')

        # 其他非零值则表示端口关闭
        else:
            pass
            # open_filter_ports.append('closed')

        sock.close()

    return open_ports, ports_state


#  功能函数6
# 功能：端口服务识别，探针指定ip 指定开放端口 (服务和版本)
# 原理：通过http数据包刺探端口，根据响应消息进行正则匹配
# 用法：接收参数 (目标ip , 存活端口) 返回最终整个扫描结果(json)

def port_server_identify(ip, ports, ports_state):
    """

    :param ip: 目标ip
    :param ports: 识别端口列表
    :param ports_state: 端口状态
    :return: 服务/版本 探测结果 (dict)
    """

    # 读取JSON指纹库文件
    # 指纹库：92个模块，每个模块下有对应的匹配正则

    global result
    with open(PORT_SCAN_CONF_PATH, 'r') as file:
        fingerprint = json.load(file)

    # 发包内容(端口服务识别函数)
    protocol = {
        'GET / HTTP/1.0\r\n\r\n'
    }
    ports_info = []

    # 如果传入的端口列表为空，输出无开放端口，return None
    if len(ports) == 0:
        # print("无开放端口")
        return {"error": 'No open ports'}

    # 端口状态索引
    state_index = 0

    # 循环探针所有开放端口
    for port in ports:

        port_state = ports_state[state_index]

        # 设置默认值为None
        service = None
        version_info = None

        result = {"ip": ip,
                  "ports_info": ports_info
                  }

        print("当前探测端口：{}".format(port))

        # 设置超时时间
        socket.setdefaulttimeout(1)
        try:
            # 创建 TCP 套接字
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # 尝试连接目标主机和端口
            res = sock.connect_ex((ip, port))

            flag = True  # 设置匹配flag状态，默认匹配失败

            for i in protocol:  # 遍历数据包字典
                sock.sendall(i.encode())  # 发送TCP数据包
                response = sock.recv(1024)  # 接受最大1024byte(字节数)
                sock.close()
            if response:

                # 取正则
                for md in fingerprint:  # 遍历指纹库的模块(module)
                    for mtc in md['matches']:  # 遍历每个模块下的matches模块

                        # 取单个service的正则，并且转换为字节对象
                        service_p = mtc['pattern']
                        service_p = service_p.encode('utf-8')

                        # 设置匹配成功的返回结果，服务,版本(默认为空)
                        service_r = mtc['service']
                        # version_r = ''

                        if re.search(service_p, response, re.IGNORECASE):  # 服务探测

                            # version_r = mtc['version_info']
                            # 获取指纹库中的版本信息
                            version_info = mtc['version_info']

                            # 定义标识符映射字典                         
                            identifier_mapping = {'p': 'vendor', 'v': 'version', 'i': 'info', 'h': 'hostname',
                                                  'o': 'operatingsystem', 'd': 'devicetype', 'cpe': 'cpename'}

                            # 替换标识符为相应的字段
                            for identifier, field in identifier_mapping.items():
                                # 匹配标识符和字段值的正则表达式
                                pattern = re.compile(f"{re.escape(identifier)}/([^/]+)/")
                                match = pattern.search(version_info)

                                if match:
                                    # 提取字段值
                                    value = match.group(1).replace(' ', '_')
                                    version_info = re.sub(f"{re.escape(identifier)}/([^/]+)/", f"{field}:{value}",
                                                          version_info)

                            # 匹配占位符
                            # 匹配正则表达式中的括号内容
                            pattern = re.compile(mtc['pattern'])
                            match = pattern.search(response.decode('utf-8', errors='replace'))

                            if match:
                                # 替换占位符
                                # 查找所有占位符
                                for i, group_value in enumerate(match.groups(), start=1):
                                    placeholder = "${}".format(i)
                                    version_info = version_info.replace(placeholder, group_value.replace(' ', '_'))

                            # 转换成字典                         
                            pattern = re.compile(r'(\w+):([^ ]+)')
                            version_info_dict = {match.group(1): match.group(2) for match in
                                                 pattern.finditer(version_info)}

                            vendor_info = version_info_dict.get('vendor', None)
                            version_info = version_info_dict.get('version', None)
                            info_info = version_info_dict.get('info', None)
                            hostname_info = version_info_dict.get('hostname', None)
                            operatingsystem_info = version_info_dict.get('operatingsystem', None)
                            devicetype_info = version_info_dict.get('devicetype', None)

                            # 移除 "cpe" 字段
                            version_info_dict.pop("cpe", None)

                            res_pattern = {
                                "{}".format(port): {
                                    "state": port_state,
                                    "finger": {
                                        "service": service_r,
                                        "vendor": vendor_info,
                                        "info": info_info,
                                        "hostname": hostname_info,
                                        "operatingsystem": operatingsystem_info,
                                        "devicetype": devicetype_info,
                                    },
                                    "raw": response.decode('utf-8', errors='replace')}
                            }

                            result["ports_info"].append(res_pattern)

                            # 匹配成功，修改flag
                            flag = False

                            break

                if re.search(rb'^HTTP/\d\.\d (\d{3})', response):
                    # rb'^HTTP/\d\.\d (\d{3})

                    service_r = 'http'

                    #  正则匹配http响应头的server头值
                    server_pattern = re.compile(rb'Server: (.+?)\r\n')
                    server_value = server_pattern.search(response)
                    if server_value:
                        version_r = server_value.group(1).decode('utf-8')
                    else:
                        version_r = 'unknown'

                    #  正则匹配http响应头的状态码
                    status_code_pattern = re.compile(rb'^HTTP/\d\.\d (\d{3}) ')
                    http_state = status_code_pattern.match(response)
                    state_code = http_state.group(1).decode('utf-8')
                    # print(state_code)

                    res_pattern = \
                        {"{}".format(port):
                             {"state": port_state,
                              "http": version_r,
                              "state_code": state_code,
                              "raw": response.decode('utf-8', errors='replace')}
                         }
                    result["ports_info"].append(res_pattern)
                    flag = False

                # 指纹库,http服务 匹配失败执行
                while flag:
                    service_r = 'unknown'
                    res_pattern = {
                        "{}".format(port): {
                            "state": port_state,
                            "finger": {
                                "service": service_r,
                                "vendor": None,
                                "info": None,
                                "hostname": None,
                                "operatingsystem": None,
                                "devicetype": None,
                            },
                            "raw": response.decode('utf-8', errors='replace')}
                    }

                    result["ports_info"].append(res_pattern)
                    flag = False

            # 无响应包的情况
            else:
                service_r = 'unknown'
                res_pattern = {
                    f"{port}": {
                        "state": port_state,
                        "finger": {
                            "service": service_r,
                            "vendor": None,
                            "info": None,
                            "hostname": None,
                            "operatingsystem": None,
                            "devicetype": None,
                        },
                        "raw": None}
                }

                result["ports_info"].append(res_pattern)

            sock.close()

        # 端口连接异常：连接超时
        # 记录当前端口连接异常信息，pass , 进行下一个端口的服务探测

        except (socket.timeout, ConnectionResetError):
            str_error = str(ConnectionResetError)
            match = re.search(r"<class '(.*?)'>", str_error)
            error = match.group(1)

            res_pattern = \
                {port:
                     {"state": "closed",
                      "error": error
                      }
                 }

            result["ports_info"].append(res_pattern)
            pass
            # print("连接超时，未连接上")
            # print(ConnectionReseterror)

        # 出现其他异常，并输出异常
        # name未定义异常：由于传入的开放ports为空列表导致，已修正
        # an integer is required (got type str)    str类型未转换 , 已修正
        # 'utf-8' codec can't decode byte 0xff in position 25: invalid start byte 编码问题,已修正
        # 添加pass
        except Exception as e:
            res_pattern = \
                {port:
                     {"state": "unknown",
                      "error": str(e)
                      }
                 }

            result["ports_info"].append(res_pattern)
            pass
            # print("其他异常")
            # print(e)

    return result


# 逻辑函数(调用功能函数，实现功能)
# 输入目标（域名或IP，输入port，80 或 1-100 或 21,22,23,80,443,3389,3306）
# 不传入端口 ，扫描默认端口列表DEFAULT_PORTS
def port_scan_action(target, ports=None, method='tcp_syn', icmp_logic='on'):
    """
    :param target: 目标域名或ip
    :param ports: 扫描端口范围(默认扫描DEFAULT_PORTS),eg:1-65535 ; 21,22,80,3306,3389,6379
    :param method: 指定扫描方式(默认半开放syn扫描)，tcp_syn ; tcp_connect ; udp
    :param icmp_logic: ip存活是否退出扫描逻辑链开关 默认退出
    :return: json的端口扫描以及服务识别结果
    """
    # 进行dns域名解析，调用功能函数1
    target_ip = get_ip_from_hostname(target)

    # 对解析成功的ip进行进一步探针
    if target_ip:

        # 设置默认端口
        default_ports = [20, 21, 22, 23, 53, 80, 111, 139, 161, 389, 443, 445, 512, 513, 514,
                         873, 888, 1025, 1433, 1521, 3128, 3306, 3311, 3312, 3389, 5432, 5900,
                         5984, 6082, 6379, 7001, 7002, 8000, 8080, 8081, 8090, 9000, 9090,
                         8888, 9200, 9300, 9999, 10000, 11211, 27017, 27018, 50000, 50030, 50070]

        # icmp进行ip存活探针(返回bool值结果) ，调用功能函数2
        flag = icmp_ping_ip(target_ip, icmp_logic)

        # ip存活，flag = True ,进行端口探针
        if flag:
            # 扫描端口(列表形式)
            scan_ports = []
            #  用户有指定端口，对用户指定端口进行探针
            if ports:

                # 指定形式 1-65535
                if '-' in str(ports):
                    s_port, e_port = map(int, ports.split('-'))
                    scan_ports = list(range(s_port, e_port + 1))
                    print("探测端口：{}".format(scan_ports))

                # 指定形式 21,22,80,443,3306,3389
                elif ',' in str(ports):
                    scan_ports = list(map(int, ports.split(',')))
                    print("探测端口：{}".format(scan_ports))

                # 指定端口 80
                else:
                    ports = int(ports)
                    scan_ports = [ports]
                    print("探测端口：{}".format(scan_ports))


            #  用户未指定端口，对默认端口进行探针
            elif ports is None:
                scan_ports = default_ports
                print("探测端口：{}".format(scan_ports))
            elif ports == '':
                scan_ports = default_ports
                print("探测端口：{}".format(scan_ports))


            if method == 'tcp_syn':
                # 对端口扫描结果进行接收
                # 端口列表，状态列表
                open_port, ports_state = syn_port_scan(target_ip, scan_ports)

            elif method == 'tcp_connect':
                open_port, ports_state = connect_port_scan(target_ip, scan_ports)

            elif method == 'udp':
                open_port, ports_state = udp_port_scan(target_ip, scan_ports)
            else:
                print("请指定扫描方式：tcp_syn tcp_connect udp")

            # 调用功能函数6：进行端口服务指纹识别
            identify_result = port_server_identify(target_ip, open_port, ports_state)

            # 返回探针结果res(json)
            ports_scan_identify_res = json.dumps(identify_result)

            # 返回结果显示(测试)
            return ports_scan_identify_res

        # flag状态为False
        # 返回主机ip存活状态(False)
        else:
            return json.dumps({"error": "{}状态：{}".format(target_ip, flag)})

    # 域名解析ip失败
    else:
        return json.dumps({"error": "无法获取{}的IP地址".format(target)})


if __name__ == '__main__':

    target_ip = '127.0.0.1'
    target_port = '21, 80, 443, 444, 445,9999'
    res = port_scan_action(target_ip, target_port)
    print(res)
