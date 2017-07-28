###清云WiFi VPN安全通道
##WiFiVPNTunnel
#语言：Python 3.*
#文件说明：
    Server.py：服务器上，对加密数据流进行处理
    Shunt.py：分流程序
    Modifier.py：用于数据流的加密解密
    Util.py：提供一些方法，对数据流进行解析和处理
    Main.py：项目的可执行程序的主体
    GUI.py：客户端的GUI，显示分流结果等

#Todo:
    发布可用客户端

#关于客户端执行流程：
1.启动squid
2.启动图形界面
3.启动分流程序
4.分流程序将分流结果等传递给图形界面