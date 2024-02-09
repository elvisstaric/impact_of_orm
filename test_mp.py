import os
import time
from random import randint

from models import *
from sqlalchemy.orm import sessionmaker
from transactions import *
from multiprocessing import Process, Value, Lock
from settings import AMOUNT_OF_PROCESSES, TEST_DURATION, PRINT_INTERVAL


def test_controler(lat,cnt, run, start, gl_start):
    while run.value:
        now = time.time()
        if now - gl_start >= TEST_DURATION:
            run.value = False
        if now - start.value >= PRINT_INTERVAL:
            print("number of transactions:", cnt.value, "lat:", lat)
            with cnt.get_lock():
                cnt.value = 0
            with lat.get_lock():
                lat.value=0
            with start.get_lock():
                start.value = now


def test(lat, cnt, run):
    max_lat=0
    now = time.time()
    
    while run.value:
        choice = randint(1, 100)
        if choice <= 45:
           
           tran = [new_order_tran,
                   {'w_id': randint(1, AMOUNT_OF_WAREHOUSES), 'c_id': randint(1, AMOUNT_OF_WAREHOUSES * 150)}]
           
        
        elif choice > 45 and choice <= 88:
             start=time.time()
             tran = [payment_tran,
                    {'w_id': randint(1, AMOUNT_OF_WAREHOUSES), 'c_id': randint(1, AMOUNT_OF_WAREHOUSES * 150)}]
             
            
        elif choice > 88 and choice <= 92:
            
           tran = [order_status_tran, {'c_id': randint(1, AMOUNT_OF_WAREHOUSES * 150)}]
           
           
        elif choice > 92 and choice <= 96:
            
           tran = [delivery_tran, {'w_id': randint(1, AMOUNT_OF_WAREHOUSES)}]
           
           
        elif choice > 96 and choice<=100:
            
            tran = [stock_level_tran, {'w_id': randint(1, AMOUNT_OF_WAREHOUSES)}]
            
        
        if tran[0](**tran[1]):
            with cnt.get_lock():
                cnt.value += 1
            a, latency=tran[0](**tran[1])
            with lat.get_lock():
                if(lat.value<latency):
                    lat.value = latency
           
                
                
              

if __name__ == '__main__':
    cnt = Value('i', 0)
    start = Value('d', 0.0)
    lat = Value("d", 0.0)
    processes = []
    start.value = gl_start = time.time()
    run = Value('b', True)

    for i in range(AMOUNT_OF_PROCESSES):
        process = Process(target=test, args=(lat,cnt, run))
        process.start()
        processes.append(process)
    process = Process(target=test_controler, args=(lat,cnt, run, start, gl_start))
    process.start()
    processes.append(process)

    for process in processes:
        process.join()
