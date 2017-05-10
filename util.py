import requests


def get_flow_result(port):
    file = open("/proxy/flow/"+str(port)+".flow")
    lines = file.readlines()
    file.close()
    if ":" in lines[-1]:
        print("error: flow result", port)
        return 0
    else:
        result = eval(lines[-1])
        if ":" not in lines[-2]:
            print("error: flow result", port)
            return 0
        return result/(1024*1024)


def get_pre_flow(port):
    file = open("/proxy/flow/"+str(port)+".flow")
    lines = file.readlines()
    file.close()
    if ":" in lines[-3]:
        print("error: pre flow result", port)
        return 0
    else:
        result = eval(lines[-3])
        if ":" not in lines[-4]:
            print("error: pre flow result", port)
            return 0
        return result/(1024*1024)


def get_ip_address(port):
    file = open("/proxy/ip/"+str(port)+".ip")
    lines = file.readlines()
    file.close()
    if ":" in lines[-1]:
        print("error: ip address result", port)
        return ""
    else:
        ipaddr = lines[-1]
        try:
            location = get_location(ipaddr)
            ipaddr += "@" + location
        except IOError as e:
            print(e)
        return ipaddr


def get_ip_address_list(port):
    file = open("/proxy/ip/" + str(port) + ".ip")
    lines = file.readlines()
    file.close()
    count = 0
    ip_list = []
    while count < 6:
        ip = lines[-1 - 2*count]
        time = lines[-2 - 2*count]
        if ":" in ip:
            print("error: IP address", port)
            return []
        if ":" not in time:
            print("error: time", port)
            return []
        time = time.replace(",", " ")
        location = get_location(ip)
        ip_list.append(ip+"@"+time+"@"+location)
        count += 1
    return ip_list


def get_location(ip):
    query_html = requests.get('http://www.ip138.com/ips138.asp?ip=' + ip).content.decode(encoding="gbk")
    index = query_html.find("本站数据：") + len("本站数据：")
    result = ""
    while query_html[index] not in " <":
        result += query_html[index]
        index += 1
    return result
