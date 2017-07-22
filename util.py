import re


def is_video_request(header):
    pattern = "GET .+\.(flv|f4v|mp4|m3u8|ts)\?.*"
    return re.match(pattern, header)


def sohu_check_feature_header(header):
    pattern = ("GET .+&passwd=.+")
    return re.match(pattern, header)


def sohu_get_vid_from_feature_header(header):
    return header.split("vid=")[1].split("&")[0]


def sohu_check_vid_from_video_request(header, flag):
    return ("vid=" + flag) in header