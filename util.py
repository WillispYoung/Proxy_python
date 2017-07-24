import re


def is_video_request(header):
    pattern = "GET .+\.(flv|f4v|mp4|m3u8|ts)\?.*"
    return re.match(pattern, header)