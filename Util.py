import re


def is_video_request(header):
    pattern = "GET .+\.(flv|f4v|mp4|m3u8|ts)\?.*"
    return re.match(pattern, header)


def check_youku_html_request(header):
    return "/v_show/id_" in header


def check_youku_video_request(header):
    pattern = "GET .+\.flv?.*ccode=.*&duration=.*&expire=.*psid=.*"
    return re.match(pattern, header)


def check_youku_feature_header(header):
    return "getVideoPlayInfo" in header and "showid=0" in header


def get_youku_vid_from_html_request(content):
    header = content.split("\n")[0]
    char_id = header.split("id_")[1].split(".html")[0].replace("=", "%3D")
    try:
        number_id = content.split("arcms=")[1].split(";")[0].split("-")[-1]
    except IndexError:
        return None, None
    if len(number_id) > 1:
        return number_id, char_id
    else:
        return None, None


def get_youku_vid_from_header(header):
    return header.split("vid=")[1].split("&")[0]
