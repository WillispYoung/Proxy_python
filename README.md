清云WiFi VPN安全通道
语言：Python 3.*
文件说明：
    server.py：服务器上的程序，对加密数据流进行处理
    shunt.py：分流程序
    modifier.py：用于数据流的加密解密

Todo:
    添加优酷、酷6的加密视频的弹出处理

说明：
    socket.bind/connect 时使用("localhost", port)而不是("", port)

完成情况：
    普通视频弹出的延迟和跳播的延迟不明显
    爱奇艺、搜狐（与56）的加密视频的不弹出基本实现