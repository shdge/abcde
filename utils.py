import numpy as np
import os, time, argparse
import pickle

parse = argparse.ArgumentParser()
parse.add_argument("file")
args = parse.parse_args()

def get_meta(inp_name, out_name, min_max, sets):
    '''

    :param inp_name: path of data file
    :param out_name: path of output file
    :param min_max: a list of indexes which we want to get their max and min value
    :param sets: a list of indexes which we want to get the set of their values
    :return: two dicts
    '''

    d_m, d_s = {}, {}

    with open(inp_name, 'rb') as f:
        head = f.readline().strip().split(' ')
    for i in min_max:
        d_m.update({head[i]: [0, 0]})
    for i in sets:
        d_s.update({head[i]: set()})

    line = f.readline()
    while line:
        line = line.strip().split(' ')
        if line[-1] != '5':
            continue
        for i in min_max:
            if line[i]!='0' and line[i]!='NULL':
                t = float(line[i])
                if t>d_m[head[i]][1]: d_m[head[i]] = t
                if t<d_m[head[i]][0]: d_m[head[i]] = t

        for i in sets:
            if line[i]!=0 and line[i]!='NULL':
                d_s[head[i]].add(line[i])

    with open('data_np/'+out_name+'_mm', 'w') as f:
        pickle.dump(d_m, f)
    with open('data_np/'+out_name+'_set', 'w') as f:
        pickle.dump(d_s, f)


def get_time_space(file, poi):
    '''

    :param file: path of data file
    :param poi: a list of regions
    :return: total_fee, pre_total_fee, orders
    '''
    with open(file, 'rb') as f:
        head = f.readline().strip().split(' ')
    index = [head.index('current_stat_hour'), head.index('starting_poi_id'), head.index('dest_poi_id') 
             head.index('pre_total_fee'), head.index('total_fee'), head.index('dynamic_price')]

    poi.sort()
    n = len(poi)

    pre_total_fee = np.zeros((24, n, n), 'float16')
    total_fee = np.zeros((24, n, n), 'float16')
    orders = np.zeros((24, n, n), 'int32')

    line = f.readline()
    while line:
        line = line.strip().split(' ')
        if line[-1] != '5': continue
        t, start, end = line[index[:3]]
        t, start, end = int(t), poi.index(start), poi.index(end)

        pre_total_fee[t, start, end] += float(line[index[3]])
        total_fee[t, start, end] += float(line[index[4]]) - float(line[index[5]])
        orders[t, start, end] += 1

    pre_total_fee /= (orders.astype('float16') + 1e-6)
    total_fee /= (orders.astype('float16') + 1e-6)

    return total_fee, pre_total_fee, orders

def get_position(file, poi):
    city = file.split('_')[-2]
    with open(file, 'rb') as f:
        head = f.readline().strip().split(' ')
    index = [head.index('starting_poi_id'), head.index('begun_lng'), 
             head.index('begun_lat')]
    
    poi.sort()
    n = len(poi)
    position = np.zeros((n, 2), 'float32')
    num = np.zeros(n, 'int32')
    
    line = f.readline()
    while line:
        line = line.strip().split(' ')
        ids, lng, lat = line[index]
        ids, lng, lat = poi.index(ids), float(lng), float(lat)
        
        position[ids] += np.array([lng, lat])
        num[ids] += 1
    num[num==0] = 1
    position = position / num
    np.save(city+'_pos', position)
    
        
        
if __name__=='__main__':
    if not os.path.isdir("data_np"):
        os.mkdir("data_np")
    get_meta(args.file, '55000199', [4,5,6,7,8,9,10,11], [1,2,3,12])



