import requests
import json
import argparse
import sys
import tqdm

RED = '\x1b[91m'
BLUE = '\033[94m'
GREEN = '\033[32m'
ENDC = '\033[0m'
#alive_ips=[]
def read_ip_from_file(file_path):

    #为了去重，使用set数据结构
    item_set=set()
    with open(file_path, "r") as file:   #打开列表文件
        ips=file.read()
        ip_ports=ips.split("\n")
        for ip_port in ip_ports:
            print(ip_port)
            item_set.add(ip_port)
    print(GREEN+"[+]txt文件读取完毕....\n"+ENDC)
    return item_set


#从json数据剥离ip:port
def read_ip_from_json(file_path):
    #为了去重，使用set数据结构
    item_set=set()
    #打开列表文件
    with open(file_path, "r") as file:
        file_data=file.read()
        json_datas=file_data.split("\n")
        for json_data in json_datas:
            json_data=json.loads(json_data)
            ip_port=(json_data["ip"]+":"+str(json_data["port"]))
            print(ip_port)
            item_set.add(ip_port)
    print(GREEN+"[+]json文件读取完毕....\n"+ENDC)
    return item_set
            

#发送https请求
def send_https_request(ip_port,proxy,user_agent):
        url="https://"+ip_port
        response=requests.get(url,allow_redirects=True,headers={"User-Agent":user_agent},proxies=proxy,timeout=5)     #存活探测
        if response.status_code==200:
            print(GREEN+"[+]"+url+" is alive"+ENDC)
            return True
        else:
            print(RED+"[-]"+url+" is dead","code:"+str(response.status_code)+ENDC)
            return False


#发送http请求
def send_http_request(ip_port,proxy,user_agent):
        url="http://"+ip_port
        response=requests.get(url,allow_redirects=True,headers={"User-Agent":user_agent},proxies=proxy,timeout=5)     #存活探测
        if response.status_code==200:
            print(GREEN+"[+]"+url+" is alive"+ENDC)
            return True
        else:
            print(RED+"[-]"+url+" is dead","code:"+str(response.status_code)+ENDC)
            return False


#save to file
#将通过测试的ip:port保存到文件中
def save_to_file(save_path,set_data,proxy,user_agent):
    print(BLUE+"[+]正在探测存活状态并保存至文件...[{}]".format(save_path)+ENDC)
    with open(save_path, "w") as file:   
        #使用tqdm显示进度
        for item in set_data:
            try:
                if send_http_request(item,proxy,user_agent):  #send request
                    file.write("http://"+item+"\n")
                if send_https_request(item,proxy,user_agent):  #send request
                    file.write("https://"+item+"\n")
            except:
                print(RED+"[-]"+item+" is timeout"+ENDC)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=GREEN+'Parse TXT,JSON format file, get the target IP: PORT infomation(automatic deduplication主动去重)'+ENDC)
    parser.add_argument('--proxy', type=str, required=False, dest='proxy', default="http://127.0.0.1:7890", help = "proxy(default:NULL)")
    parser.add_argument('--txt', type=str, required=False, dest='txt_file_path', default = "", help = "txt_file_path ")
    parser.add_argument('--json', type=str, required=False, dest='json_file_path', default = "./json/目录穿越.json", help = "json_file_path")
    parser.add_argument('--save', type=str, required=False, dest='save_path', default="./result.txt" , help = "where the result will be saved")
    parser.add_argument('--user-agent', type=str, required=False, default="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36", dest='user_agent', help = "Custom User-Agent")
    args = parser.parse_args()
    file_path=args.txt_file_path
    save_path=args.save_path
    json_file_path=args.json_file_path
    user_agent=args.user_agent
    if args.proxy!="":
        proxy={}#"http":"http://127.0.0.7890"}
    else:
        proxy={}

    if file_path=="" and json_file_path=="":
        print(RED+"[-]please input the file path"+ENDC)
        sys.exit(1)
    elif file_path!="":
        save_to_file(save_path,read_ip_from_file(file_path),proxy,user_agent)
    elif json_file_path!="":
        save_to_file(save_path,read_ip_from_json(json_file_path),proxy,user_agent)
    else:
        print(RED+"[-]please check the file path Parameter setting: Only one file can be parsed at a time "+ENDC)
        sys.exit(1)