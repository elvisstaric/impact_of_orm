import os
import time
from random import randint

from models import *
from sqlalchemy.orm import sessionmaker
from transactions import *
from multiprocessing import Process, Value, Lock
from settings import AMOUNT_OF_PROCESSES, TEST_DURATION, PRINT_INTERVAL


def test_controler(lat,cnt,cnt_no,cnt_pay, cnt_ord_st, cnt_del, cnt_stock, run, start, gl_start):
    while run.value:
        now = time.time()
        if now - gl_start >= TEST_DURATION:
            run.value = False
        if now - start.value >= PRINT_INTERVAL:
            print("All:",cnt.value, "lat:", lat, "NO:", cnt_no, "Payment:", cnt_pay, "OrdSt:", cnt_ord_st, "Delete:", cnt_del, "Stock:", cnt_stock)
            with cnt.get_lock():
                cnt.value = 0
            with cnt_no.get_lock():
                cnt_no.value = 0
            with cnt_pay.get_lock():
                cnt_pay.value = 0
            with cnt_ord_st.get_lock():
                cnt_ord_st.value = 0
            with cnt_del.get_lock():
                cnt_del.value = 0
            with cnt_stock.get_lock():
                cnt_stock.value = 0
            with lat.get_lock():
                lat.value=0
            with start.get_lock():
                start.value = now


def test(lat, cnt, cnt_no,cnt_pay, cnt_ord_st, cnt_del, cnt_stock,  run):
    max_lat=0
    now = time.time()
    while run.value:
        choice = randint(1, 100)
        if choice <= 45:
           start = time.perf_counter()
           tran = [new_order_tran,
                   {'w_id': randint(1, AMOUNT_OF_WAREHOUSES), 'c_id': randint(1, AMOUNT_OF_WAREHOUSES * 150)}]
           end = time.perf_counter() - start
           if max_lat<end:
               max_lat=end;
        elif choice > 45 and choice <= 88:
             start=time.perf_counter()
             tran = [payment_tran,
                    {'w_id': randint(1, AMOUNT_OF_WAREHOUSES), 'c_id': randint(1, AMOUNT_OF_WAREHOUSES * 150)}]
             end = time.perf_counter() - start
             if max_lat<end:
                 max_lat=end;
        elif choice > 88 and choice <= 92:
           start = time.perf_counter() 
           tran = [order_status_tran, {'c_id': randint(1, AMOUNT_OF_WAREHOUSES * 150)}]
           end = time.perf_counter() - start
           if max_lat<end:
               max_lat=end;
        elif choice > 92 and choice <= 96:
           start = time.perf_counter() 
           tran = [delivery_tran, {'w_id': randint(1, AMOUNT_OF_WAREHOUSES)}]
           end = time.perf_counter() - start
           if max_lat<end:
               max_lat=end;
        elif choice > 96 and choice<=100:
            start = time.perf_counter()
            tran = [stock_level_tran, {'w_id': randint(1, AMOUNT_OF_WAREHOUSES)}]
            end = time.perf_counter() - start
            if max_lat<end:
                max_lat=end;
        
        if tran[0](**tran[1]):
            with cnt.get_lock():
                cnt.value += 1
            with lat.get_lock():
                lat.value = max_lat
            if choice <= 45:
               with cnt_no.get_lock():
                 cnt_no.value += 1
            elif choice > 45 and choice <= 88:
                with cnt_pay.get_lock():
                     cnt_pay.value += 1
            elif choice > 88 and choice <= 92:
                with cnt_ord_st.get_lock():
                    cnt_ord_st.value += 1
            elif choice > 92 and choice <= 96:
                with cnt_del.get_lock():
                    cnt_del.value += 1
            elif choice > 96 and choice<=100:
                with cnt_stock.get_lock():
                    cnt_stock.value += 1
            

if __name__ == '__main__':
    cnt = Value('i', 0)
    cnt_no = Value('i', 0)
    cnt_pay = Value('i', 0)
    cnt_ord_st = Value('i', 0)
    cnt_del = Value('i', 0)
    cnt_stock = Value('i', 0)
    start = Value('d', 0.0)
    lat = Value("d", 0.0)
    processes = []
    start.value = gl_start = time.time()
    run = Value('b', True)

    for i in range(AMOUNT_OF_PROCESSES):
        process = Process(target=test, args=(lat,cnt,cnt_no,cnt_pay, cnt_ord_st, cnt_del, cnt_stock, run))
        process.start()
        processes.append(process)
    process = Process(target=test_controler, args=(lat,cnt,cnt_no,cnt_pay, cnt_ord_st, cnt_del, cnt_stock, run, start, gl_start))
    process.start()
    processes.append(process)

    for process in processes:
        process.join()
