from models import *
from random import randint, choice
from datetime import datetime
import time

from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, func, update
from settings import AMOUNT_OF_WAREHOUSES


def new_order_tran(w_id, c_id):
    ST=time.time()
    Session = sessionmaker(bind=engine)
    session = Session()
    set_iso(session)
    
    whouse = session.query(Warehouse).filter(Warehouse.w_id == w_id).first()
    district = choice(whouse.districts.all())
    customer = session.query(Customer).filter(Customer.c_id == c_id).first()
    ol_cnt = randint(1, 10)
    amount = randint(1, 10)
    last_order = session.query(func.max(Orders.o_id)).scalar()
    order = Orders(
        o_id=last_order+1,
        o_ol_cnt=ol_cnt,
        o_c_id=customer.c_id,	
        o_entry_d=datetime.now(),
        o_w_id=whouse.w_id,
        o_d_id=district.d_id
    )
    session.commit()
    items_id = []

    for i in range(ol_cnt):
        item = session.query(Item).filter(Item.i_id == randint(1, AMOUNT_OF_WAREHOUSES * 10)).first()
        items_id.append(item.i_id)
        ord_line = OrderLine(
            ol_w_id = whouse.w_id,
            ol_d_id = district.d_id,
            ol_number = i,
            ol_i_id = item.i_id,
            ol_supply_w_id = 1,
            ol_delivery_d = order.o_entry_d,
            ol_quantity = ol_cnt,
            ol_amount = amount,
            ol_o_id = order.o_id,
            ol_dist_info = "pz8k31cIa9yaYNhc3FESgn32"
        )
        session.commit

    stocks = session.query(Stock).filter(Stock.s_w_id == whouse.w_id, Stock.s_i_id.in_(items_id)).order_by(text("s_i_id")).with_for_update().all()
    for stock in stocks:
        i_in_o = items_id.count(stock.s_i_id)
        stock.s_order_cnt += 1
        stock.s_quantity -= amount * i_in_o
    session.commit()
    EN=time.time()-ST
    return True, EN


def payment_tran(w_id, c_id):
    ST=time.time()
    Session = sessionmaker(bind=engine)
    session = Session()
    set_iso(session)

    whouse = session.query(Warehouse).filter(Warehouse.w_id == w_id).first()
    district = choice(whouse.districts.all())
    customer = session.query(Customer).filter(Customer.c_id == c_id).first()
    h_amount = randint(10, 5000)

    whouse.w_ytd += h_amount
    district.d_ytd += h_amount
    customer.c_balance -= h_amount
    customer.c_ytd_payment += h_amount
    customer.c_payment_cnt += 1
    
    session.add(History(
        h_c_id=customer.c_id,
        h_c_d_id=district.d_id,
        h_c_w_id=whouse.w_id,
        h_d_id=district.d_id,
        h_w_id=whouse.w_id,
        h_amount=h_amount,
        h_data='new_paynment',
        h_date=datetime.now()
    ))	
    session.commit()
    EN=time.time()-ST
    return True, EN


def order_status_tran(c_id):
    ST=time.time()
    Session = sessionmaker(bind=engine)
    session = Session()
    set_iso(session)

    customer = session.query(Customer).filter(Customer.c_id == c_id).first()
    last_order = session.query(Orders).filter(Orders.customer == customer).order_by(text("o_id desc")).first()
    o_ls = []
    
    if not last_order:
        session.commit()
        return False
    for ol in session.query(OrderLine).filter(OrderLine.ol_o_id == last_order.o_id, OrderLine.ol_w_id == last_order.o_w_id):
        o_ls.append({
            'ol_delivery_d' : ol.ol_delivery_d,
            'ol_item' : ol.ol_i_id,
            'ol_amount' : ol.ol_amount,
            'ol_order' : ol.ol_o_id
        })
    session.commit()
    EN=time.time()-ST
    return True, EN
def set_iso(session):
    session.execute(text("SET AUTOCOMMIT = 1"))

def delivery_tran(w_id):
    ST=time.time()
    Session = sessionmaker(bind=engine)
    session = Session()
    set_iso(session)

    whouse = session.query(Warehouse).filter(Warehouse.w_id == w_id).first()
    districts = session.query(District).filter(District.warehouse == whouse).order_by(text("d_w_id")).with_for_update()
    customers_id = []
    oln=1
    for district in districts:
        new_order=session.query(NewOrder).filter(NewOrder.no_d_id == district.d_id).order_by(text("no_d_id"))
        order = session.query(Orders).filter(Orders.district == district).order_by(text("o_d_id")).first()
        if not new_order:
            session.commit()
            return False
        delete=session.query(NewOrder).where(NewOrder.no_o_id == order.o_id, NewOrder.no_d_id == district.d_id,NewOrder.no_w_id == district.d_w_id).delete()
        for ol in session.query(OrderLine).filter(OrderLine.ol_o_id == order.o_id, OrderLine.ol_w_id == order.o_w_id, OrderLine.ol_number == oln):
    
            oln=oln+1
            ol.ol_delivery_d = datetime.now()
        customers_id.append(order.o_c_id)
    customers = session.query(Customer).filter(Customer.c_id.in_(customers_id)).order_by(text("c_id")).with_for_update()
    for customer in customers:
        amount = customer.c_delivery_cnt+customers_id.count(customer.c_id)
        update_cnt = update(Customer).where(Customer.c_id==customer.c_id).values(c_delivery_cnt=amount)
        

    session.commit()
    EN=time.time()-ST
    return True, EN
    



def stock_level_tran(w_id):
    ST=time.time()
    Session = sessionmaker(bind=engine)
    session = Session()
    set_iso(session)
    

    whouse = session.query(Warehouse).filter(Warehouse.w_id == w_id).first()
    oln=1
    items_stock = {}
    for order in session.query(Orders).filter(Orders.warehouse == whouse).order_by(text("o_w_id desc"))[:20]:
        for ol in session.query(OrderLine).filter(OrderLine.ol_o_id == order.o_id, OrderLine.ol_w_id == order.o_w_id, OrderLine.ol_number == oln):

               oln=oln+1
               item = session.query(Item).filter(Item.i_id == ol.ol_i_id).first()
               if item.i_name in items_stock.keys():
                    continue
               stock = session.query(Stock).filter(Stock.warehouse == whouse, Stock.item == item).first()
               items_stock[item.i_name] = stock.s_quantity
    session.commit()
    EN=time.time()-ST
    return True, EN
