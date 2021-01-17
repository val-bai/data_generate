import requests
import xlrd
import re
from bs4 import BeautifulSoup
import json
import math
from geopy.distance import geodesic
import numpy as np
from random import shuffle
import random
import pandas as pd

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率
URL_GAODE_API= 'https://restapi.amap.com/v3/geocode/geo?'

def main():
    # TODO 1. 读取文件lianjia_hz.xls 中的小区名 并存与 neighbour_name_list中
    file_name = "lianjia_hz.xls"
    readbook = xlrd.open_workbook(file_name)
    sheet = readbook.sheet_by_index(0)
    nrows = sheet.nrows
    neighbour_dict = {}
    for i in range(nrows - 1):
        name = str(sheet.cell(i, 2))
        neighbour_dict[name[6:-1]] = 1
    neighbour_name_list = list(neighbour_dict.keys())

    # TODO 2. 读取经纬度，在第一次读完以后存储到 "校区经纬坐标.json"文件中，下次可以直接读取使用
    # get_jinweidu(neighbour_name_list)

    # with open('小区经纬坐标.json', 'r', encoding='utf8')as fp:
    #     location_Dictionary = json.load(fp)

    # TODO 3. 将高德地图的火星坐标转化为正常坐标
    # location_Dictionary_new = {}
    # for i in range(len(neighbour_name_list)):
    #     try:
    #         location_Dictionary_new[neighbour_name_list[i]] = gcj02towgs84(location_Dictionary[neighbour_name_list[i]][0], location_Dictionary[neighbour_name_list[i]][1])
    #     except KeyError:
    #         pass
    #
    # with open("纠偏小区经纬坐标.json", "w", encoding='utf-8') as f:
    #     f.write(json.dumps(location_Dictionary, ensure_ascii=False, indent=4, separators=(',', ':')))

    # TODO 4. 生成距离矩阵
    # 4.1 经纬度获得
    with open('纠偏小区经纬坐标.json', 'r', encoding='utf-8') as f:
        location_Dictionary = json.load(f)
    num = len(location_Dictionary)
    lon_lat_list = list(location_Dictionary.values())
    # for i in range(len(lon_lat_list)):
    #     lon_lat_list[i][0], lon_lat_list[i][1] = lon_lat_list[i][1], lon_lat_list[i][0]
    # distance_list = get_distance(len(lon_lat_list), list(lon_lat_list))
    # print(distance_list)

    # TODO 5. 干垃圾、湿垃圾 demand
    dry_demand_list = demand_generate(num, 2, 1)
    wet_demand_list = demand_generate(num, 1, 0.5)

    # TODO 6. time windows
    time_window_list = time_window_generate(num)
    # TODO 7. service time
    service_time_list = np.random.randint(15, 30, num)

    # TODO 8. VEHICLE DATA
    car_depot = np.random.uniform(0, num, 4)



    # TODO 9. 存储数据
    store_data('C101.txt', num, 4,
               lon_lat_list, dry_demand_list, wet_demand_list, time_window_list, service_time_list)


def get_jinweidu(neighbour_name_list):
    par = {
        'address': '',
        'city': '杭州',
        'key': 'ecc04f257bdcd5068e54103e598a99a5'
    }
    # 获得经纬度
    location_Dictionary = {}
    for i in range(len(neighbour_name_list)):
        par['address'] = neighbour_name_list[i]
        location_lon_lat = getLocation(URL_GAODE_API, par)  # 获得经纬坐标
        try:
            a = list(map(lambda x: float(x), location_lon_lat[0].split(',')))
        except IndexError:
            continue
        location_Dictionary[par['address']] = a

    with open("小区经纬坐标.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(location_Dictionary, ensure_ascii=False, indent=4, separators=(',', ':')))

def getLocation(url, par):
    response = requests.get(url, params=par)
    res = BeautifulSoup(str(response.text),"lxml")
    res = str(res)
    location = re.findall(re.compile(r'"location":"(.*?)"'),res)
    return location

def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False

def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

def gcj02towgs84(lng, lat):
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]

def get_distance(num: int, lat_lon_list: list):
    distance_list = []
    for i in range(num):
        temp = []
        for j in range(num):
            temp.append(geodesic(lat_lon_list[i], lat_lon_list[j]).km)
        distance_list.append(temp)
    return distance_list

def demand_generate(num: int, mean: float, var: float):
    '''
    :param num: 生成个数
    :param mean: 服从的均值
    :param var: 服从的方差
    :return: 对应个数的数据list
    '''
    dry_demand_list = []
    i = 0
    while(i < num):
        temp = np.random.normal(mean, var)
        if(temp < 0):
            i = i - 1
            continue
        dry_demand_list.append(temp)
        i += 1
    return dry_demand_list

def time_window_generate(num: int, end_time=1020, station_percentage = 0.6,tw_percentage=0.2):
    '''

    :param num:
    :param station_percentage: 清运点与中转站比例
    :param tw_percentage: 清运点拥有时间窗的站点比例
    :param end_time: 时间窗结束时间
    :param percentage:
    :return:
    '''
    random.seed(1)
    temp_list = [i for i in range(num)]
    shuffle(temp_list)
    tw_station_num = int(num * station_percentage * tw_percentage)  # 清运点拥有时间窗的站点
    qinyun_stataion_num = int(num * station_percentage)  # 清运点数量
    time_window_list = []
    start_time = 480  # 早上8点 即480分钟
    car_num = 0  # 自有车辆个数
    station_type = 0  # 站点种类，0为清运站， 1为中转站
    for i in range(tw_station_num):
        time_window_list.append([temp_list[i], start_time, end_time, car_num, station_type])
    for i in range(tw_station_num, qinyun_stataion_num):
        time_window_list.append([temp_list[i], 0, 1440, 0, 0])
    for i in range(qinyun_stataion_num, num):
        time_window_list.append([temp_list[i], 0, 1440, random.randint(1, 2), 1])
    time_window_list.sort(key=lambda x: x[0])
    return time_window_list

def store_data(file_name, num: int, capacity: int, lat_lon_gauss_list, dry_demand_list, wet_demand_list, time_window_list, service_time_list):
    f = open(file_name, mode='w')
    f.write('DATA')
    f.write('\n')
    f.write('\nVEHICLE\n')
    f.write('ID\tLON\tLAT\tNUMBER\tCAPACITY\tCOST\n')
    f.write(' ')
    f.write(str(num))
    f.write(' ')
    f.write(str(capacity))
    f.write('\n')
    f.write('\nCUSTOMER\n')
    # f.write('CUST LAT\tLON\tDEMAND\tSTART_TIME\tEND_TIME\tSETVICE_TIME\n')
    # f.write('0 0 0 0\t0\t1020\t0\n')
    # for i in range(num):
    #     f.write('%d\t%d\t%d\t%d\t%d\t%d\t%d\n' % (i+1, lat_lon_gauss_list[i][0], lat_lon_gauss_list[i][1], dry_demand_list[i], time_window_list[i][1],
    #                                           time_window_list[i][2], service_time_list[i]))
    f.write('ID\tLON\tLAT\tDRY_DEMAND\tWET_DEMAND\tSTART_TIME\tEND_TIME\tSETVICE_TIME\tCAR_NUM\tSTATION_TYPE\n\n')
    # f.write('0 0 0 0 0 1920 0\n')
    for i in range(num):
        f.write('%d\t%f\t%f\t%f\t%f\t%d\t%d\t%d\t%d\t%d\n' % (i+1, lat_lon_gauss_list[i][0], lat_lon_gauss_list[i][1], dry_demand_list[i], wet_demand_list[i], time_window_list[i][1], time_window_list[i][2], service_time_list[i], time_window_list[i][3], time_window_list[i][3]))

    f.close()

if __name__ == "__main__":
    main()
