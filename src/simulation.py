import math
import datetime
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

def to_ln_timestamp(date):
    return math.log(pd.to_datetime(date, dayfirst=True, utc=True).timestamp())

def from_ln_timestamp(ln_timestamp):
    return datetime.datetime.fromtimestamp(math.exp(ln_timestamp)).strftime('%d/%m/%Y')

def read_curve(filename):
    # Ruta relativa desde src/ hacia data/ (un nivel arriba)
    data_path = Path(__file__).parent.parent / 'data' / filename
    curve = pd.read_csv(data_path, sep=';', encoding='utf-8-sig')
    curve.index = curve['Date']
    # Convertimos las fechas a ln(timestamp) para poder interpolar posteriormente
    curve['ln(Date)'] = curve['Date'].apply(to_ln_timestamp)
    return curve

def plot_curve(curve):
    curve[['Discount', 'Zero Rate', 'Market Rate']].plot()

def evaluate_bonds(date, df, curve, spread):
    return df.apply(lambda bond: __evaluate_bond__(date, bond, curve, spread), axis = 1)

def __evaluate_bond__(date, bond, curve, bps):
    dirty_price = 0
    spread = bps / 10000
    coupon = bond['Coupon']
    nominal = bond['Price']
    coupon_value = coupon/100 * nominal
    maturity_date = bond['Maturity']
    # Si es perpetuo, cogemos la fecha del proximo call
    if pd.isnull(maturity_date):
        maturity_date = bond['Next Call Date']

    coupon_freq = bond['Coupon Frequency']
    first_coupon_date = pd.to_datetime(bond['First Coupon Date'])
    next_coupon_date = first_coupon_date

    while (next_coupon_date < date):
        next_coupon_date = next_coupon_date + relativedelta(years=coupon_freq)
    last_coupon_date = next_coupon_date - relativedelta(years=coupon_freq)

    days_from_last_coupon_payment = (date - last_coupon_date).days
    days_until_next_coupon_payment = (next_coupon_date - date).days
    accrued_interest = coupon_value * (days_from_last_coupon_payment/days_until_next_coupon_payment if days_until_next_coupon_payment > 0 else 0)

    t = 0
    while (next_coupon_date < maturity_date):
        t = ((next_coupon_date - date).days) / 365.0
        dirty_price = dirty_price + coupon_value * interpolate(curve, next_coupon_date) * math.exp(-spread * t)
        next_coupon_date = next_coupon_date + relativedelta(years=coupon_freq)

    dirty_price = dirty_price + nominal * interpolate(curve, maturity_date) * math.exp(-spread * t)
    clean_price = dirty_price - accrued_interest

    bond['Clean Price'] = clean_price
    bond['Dirty Price'] = dirty_price
    bond['Accrued Interest'] = accrued_interest

    return bond

def interpolate(curve, date, column='Discount'):
        ln_date = to_ln_timestamp(date)
        return np.interp(ln_date, curve['ln(Date)'], curve[column])

def __z_spread__(date, next_coupon_date, maturity_date, nominal, coupon_value, coupon_freq, curve, z_value):
        t = 0
        pvz = 0
        while (next_coupon_date < maturity_date):
            t = ((next_coupon_date - date).days) / 365.0
            pvz = pvz + coupon_value / (1 + interpolate(curve, next_coupon_date, 'Zero Rate') / 100 + z_value) ** t
            next_coupon_date = next_coupon_date + relativedelta(years=coupon_freq)

        return pvz + nominal / (1 + interpolate(curve, maturity_date, 'Zero Rate') / 100 + z_value) ** t

def __calculate_z_spread__(date, bond, curve):
    dirty_price = bond['Dirty Price']

    coupon = bond['Coupon']
    nominal = bond['Price']
    coupon_value = coupon/100 * nominal
    maturity_date = bond['Maturity']
    # Si es perpetuo, cogemos la fecha del proximo call
    if pd.isnull(maturity_date):
        maturity_date = bond['Next Call Date']

    coupon_freq = bond['Coupon Frequency']
    first_coupon_date = pd.to_datetime(bond['First Coupon Date'])
    next_coupon_date = first_coupon_date

    while (next_coupon_date < date):
        next_coupon_date = next_coupon_date + relativedelta(years=coupon_freq)

    low_barrier = -0.05
    high_barrier = 0.25
    tolerance = 0.00001
    max_iter = 1000
    iteration = 0

    bond['Z Spread'] = 0
    while (iteration < max_iter):
        z_value = (low_barrier + high_barrier) / 2
        z_spread = __z_spread__(date, next_coupon_date, maturity_date, nominal, coupon_value, coupon_freq, curve, z_value)
        if (abs(z_spread - dirty_price) < tolerance):
            bond['Z Spread'] = z_value * 10000 #Convertir a bps
            print(z_value)
            break
        if (z_spread > dirty_price):
            low_barrier = z_value
        else:
            high_barrier = z_value

        iteration += 1

    return bond

def calculate_z_spreads(date, df, curve):
    return df.apply(lambda bond: __calculate_z_spread__(date, bond, curve), axis = 1)
