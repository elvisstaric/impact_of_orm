import os
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, Integer, SmallInteger, String, create_engine, ForeignKey, BigInteger, Float, Boolean, Text 
from sqlalchemy.orm import relationship, declarative_base
from settings import PROVIDER


engine = create_engine(PROVIDER['mysql'])

Base = declarative_base()


class Warehouse(Base):
    __tablename__ = 'warehouse'
    
    w_id = Column(SmallInteger, primary_key=True)
    w_name = Column(String(255), nullable=True)
    w_street_1 = Column(String(255), nullable=True)
    w_street_2 = Column(String(255), nullable=True)
    w_city = Column(String(255), nullable=True)
    w_state = Column(String(255), nullable=True)
    w_zip = Column(String(255), nullable=True)
    w_tax = Column(Float, nullable=True)
    w_ytd = Column(Float, nullable=True)
    orders = relationship("Orders", backref='warehouse', lazy='dynamic') 	
    districts = relationship("District", backref='warehouse', lazy='dynamic')	 
    stocks = relationship("Stock", backref='warehouse', lazy='dynamic')



class District(Base):
    __tablename__ = 'district'
    
    d_id = Column(Integer, primary_key=True)
    d_w_id = Column(Integer, ForeignKey('warehouse.w_id'), primary_key=True,  index=True, nullable=False)
    d_name = Column(String, nullable=True)
    d_street_1 = Column(String, nullable=True)
    d_street_2 = Column(String, nullable=True)
    d_city = Column(String, nullable=True)
    d_state = Column(String, nullable=True)
    d_zip = Column(String, nullable=True)
    d_tax = Column(Float, nullable=True)
    d_ytd = Column(Float, nullable=True)
    d_next_o_id = Column(Integer, nullable=True)
    orders = relationship("Orders", backref='district', lazy='dynamic')
    customers = relationship("Customer", backref='district', lazy='dynamic')

    

class Customer(Base):
    __tablename__ = 'customer'
    
    c_id = Column(Integer, primary_key=True, autoincrement=True)
    c_first = Column(String, nullable=True)
    c_middle = Column(String, nullable=True)
    c_last = Column(String, nullable=True)
    c_street_1 = Column(String, nullable=True)
    c_street_2 = Column(String, nullable=True)
    c_city = Column(String, nullable=True)
    c_state = Column(String, nullable=True)
    c_zip = Column(String, nullable=True)
    c_phone = Column(String, nullable=True)
    c_since = Column(DateTime, nullable=True)
    c_credit = Column(String, nullable=True)
    c_credit_lim = Column(BigInteger, nullable=True)
    c_discount = Column(Float, nullable=True)
    c_delivery_cnt = Column(Integer, nullable=True)
    c_payment_cnt = Column(Integer, nullable=True)
    c_balance = Column(Float, nullable=True)
    c_ytd_payment = Column(Float, nullable=True)
    c_data = Column(Text, nullable=True)
    c_d_id = Column(Integer, ForeignKey('district.d_id'), primary_key=True, index=True, nullable=False)
    c_w_id = Column(Integer, ForeignKey('warehouse.w_id'), primary_key=True, index=True, nullable=False)
    orders = relationship("Orders", backref='customer', lazy='dynamic')
    history = relationship("History", backref='customer', lazy='dynamic')


class Stock(Base):
    __tablename__ = 'stock'
    
    s_i_id = Column(Integer, ForeignKey('item.i_id'), primary_key=True, index=True, nullable=False)
    s_w_id = Column(Integer, ForeignKey('warehouse.w_id'), primary_key=True,  index=True, nullable=False)
    s_quantity = Column(Integer, nullable=True)
    s_dist_01 = Column(String, nullable=True)
    s_dist_02 = Column(String, nullable=True)
    s_dist_03 = Column(String, nullable=True)
    s_dist_04 = Column(String, nullable=True)
    s_dist_05 = Column(String, nullable=True)
    s_dist_06 = Column(String, nullable=True)
    s_dist_07 = Column(String, nullable=True)
    s_dist_08 = Column(String, nullable=True)
    s_dist_09 = Column(String, nullable=True)
    s_dist_10 = Column(String, nullable=True)
    s_ytd = Column(Float, nullable=True)
    s_order_cnt = Column(SmallInteger, nullable=True)
    s_remote_cnt = Column(SmallInteger, nullable=True)
    s_data = Column(String, nullable=True)
    


class Item(Base):
    __tablename__ = 'item'
    
    i_id = Column(Integer, primary_key=True)
    i_im_id = Column(Integer, primary_key=True)
    i_name = Column(String, nullable=True)
    i_price = Column(Float, nullable=True)
    i_data = Column(String, nullable=True)
    stocks = relationship('Stock', backref='item', lazy='dynamic')
    o_lns = relationship("OrderLine", backref='item', lazy='dynamic')


class Orders(Base):
    __tablename__ = 'orders'
    
    o_id = Column(Integer, primary_key=True)
    o_w_id = Column(Integer, ForeignKey('warehouse.w_id'), primary_key=True, index=True, nullable=False)
    o_d_id = Column(Integer, ForeignKey('district.d_id'), primary_key=True, index=True, nullable=False)
    o_c_id = Column(Integer, ForeignKey('customer.c_id'), index=True)
    o_entry_d = Column(DateTime, nullable=False)
    o_ol_cnt = Column(Integer, nullable=True)
    o_all_local = Column(Integer, nullable=True)
    o_lns = relationship("OrderLine", backref = "orders", lazy = "dynamic")


class NewOrder(Base):
    __tablename__ = "new_orders"

    no_o_id = Column(Integer,ForeignKey("orders.o_id"), primary_key=True, index=True, nullable=False)
    no_d_id = Column(Integer,ForeignKey("district.d_id"), primary_key=True, index=True, nullable=False)
    no_w_id = Column(Integer,ForeignKey("warehouse.w_id"), primary_key=True, index=True, nullable=False)

class OrderLine(Base):
    __tablename__ = 'order_line'
    
    ol_w_id = Column(Integer, ForeignKey('warehouse.w_id'), primary_key=True, index=True, nullable=False)
    ol_d_id = Column(Integer, ForeignKey('district.d_id'), primary_key=True, index=True, nullable=False)
    ol_number = Column(Integer, primary_key=True, nullable=False)
    ol_i_id = Column(Integer, ForeignKey('item.i_id'), index=True)
    ol_supply_w_id = Column(Integer, ForeignKey("warehouse.w_id"), index=True)
    ol_delivery_d = Column(DateTime, nullable=True)
    ol_quantity = Column(Integer, nullable=True)
    ol_amount = Column(Float, nullable=True)
    ol_o_id = Column(Integer, ForeignKey('orders.o_id'), primary_key=True, index=True, nullable=False)
    ol_dist_info = Column(String, nullable=True)

    
class History(Base):
    __tablename__ = 'history'
    
    h_c_id = Column(Integer, ForeignKey("customer.c_id"), primary_key=True, index=True)
    h_c_d_id = Column(Integer, ForeignKey("district.d_id"), primary_key=True, index=True)
    h_c_w_id = Column(Integer, ForeignKey("warehouse.w_id"), primary_key=True, index=True)
    h_d_id = Column(Integer, ForeignKey("district.d_id"), primary_key=True, index=True)
    h_w_id = Column(Integer, ForeignKey("warehouse.w_id"), primary_key=True, index=True)
    h_date = Column(DateTime, nullable=False)
    h_amount = Column(Float, nullable=False)
    h_data = Column(String, nullable=False)
   


def create_tables():
    Base.metadata.create_all(engine)


