import numpy as np
from geopy.distance import geodesic
from random import shuffle

LAT_LOW = 29.183
LAT_HIGH = 30.55
LAT_MEANS = 30.267
LON_LOW = 118.35
LON_HIGH = 120.5
LON_MEANS = 120.2

def main(num=100):
    # TODO 1.生成经纬度
    # “杭州地理坐标为坐标为东经118°21′-120°30′,北纬29°11′-30°33′。市中心地理坐标为东经120°12′,北纬30°16′。
    # 118.35 - 120.5, mean = 120.2,   29.183 - 30.55, mean = 30.267
    # TODO 1.1 正态分布生成
    lat_lon_gauss_list = gauss_gen(num)
    # TODO 1.2 均匀分布
    lat_lon_uniform_list = uniform_gen(num)
    # TODO 1.3 得到距离矩阵
    distance_list = get_distance(num, lat_lon_gauss_list)  # 单位为km
    print(distance_list)

    # TODO 2. 干垃圾、湿垃圾 demand
    dry_demand_list = demand_generate2(num, 1, 3)
    wet_demand_list = demand_generate(100, 50, num)

    # TODO 3. time windows
    time_window_list = time_window_generate(num)
    # TODO 4. service time
    service_time_list = np.random.randint(10, 30, num)

    # TODO 5. store data
    store_data('C101.txt', num, 4,
               lat_lon_uniform_list, dry_demand_list, time_window_list, service_time_list)



def gauss_gen(num: int):
    '''
    :param num: 生成经纬度个数
    :return: 经纬度二维数组
    '''
    # 经度生成，并锁定范围
    lon_list = []
    i = 0
    while(i < num):
        lon_num = np.random.normal(LON_MEANS, 0.05)
        if(lon_num > LON_HIGH or lon_num < LON_LOW):
            i = i - 1
            continue
        lon_list.append(lon_num)
        i += 1
    # 纬度生成，并锁定范围
    lat_list = []
    i = 0
    while(i < num):
        lat_num = np.random.normal(LAT_MEANS, 0.05)
        if(lat_num > LAT_HIGH or lat_num < LAT_LOW):
            i = i - 1
            continue
        lat_list.append(lat_num)
        i += 1
    # 合并经纬度
    lat_lon_list = []
    for i in range(num):
        lat_lon_list.append([lat_list[i], lon_list[i]])
    return lat_lon_list

def uniform_gen(num: int):
    '''
    :param num: 生成经纬度个数
    :return: 经纬度二维数组
    '''
    # 经度生成，并锁定范围
    lon_list = np.random.uniform(LON_LOW, LON_HIGH, num)
    # 纬度生成，并锁定范围
    lat_list = np.random.uniform(LAT_LOW, LAT_HIGH, num)
    # 合并经纬度
    lon_lat_list = []
    for i in range(num):
        lon_lat_list.append([lon_list[i], lat_list[i]])
    return lon_lat_list

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

def demand_generate2(num: int, low: int, high: int):

    dry_demand_list = np.random.randint(low, high, num)
    return dry_demand_list

def time_window_generate(num: int, end_time=1020, percentage=1.0):
    '''

    :param num:
    :param end_time: 时间窗结束时间
    :param percentage:
    :return:
    '''
    temp_list = [i for i in range(num)]
    shuffle(temp_list)
    temp_n = int(num * percentage)
    time_window_list = []
    start_time = 480  # 早上8点 即480分钟
    for i in range(temp_n):
        time_window_list.append([temp_list[i], start_time, end_time])
    time_window_list.sort(key=lambda x: x[0])
    return time_window_list

def store_data(file_name, num: int, capacity: int, lat_lon_gauss_list, dry_demand_list, time_window_list, service_time_list):
    f = open(file_name, mode='w')
    f.write('solomon')
    f.write('\n')
    f.write('\nVEHICLE\n')
    f.write('NUMBER CAPACITY\n')
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
    f.write('ID\tLAT\tLON\tDEMAND\tSTART_TIME\tEND_TIME\tSETVICE_TIME\n\n')
    f.write('0 0 0 0 0 1920 0\n')
    for i in range(num):
        f.write('%d\t%f\t%f\t%d\t%d\t%d\t%d\n' % (i+1, lat_lon_gauss_list[i][0], lat_lon_gauss_list[i][1], dry_demand_list[i], time_window_list[i][1], time_window_list[i][2], service_time_list[i]))

    f.close()





if __name__ == '__main__':
    main()

