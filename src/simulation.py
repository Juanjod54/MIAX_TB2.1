import math
import datetime

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from dateutil.relativedelta import relativedelta


def to_ln_timestamp(date):
    return math.log(pd.to_datetime(date, dayfirst=True, utc=True).timestamp())

def from_ln_timestamp(ln_timestamp):
    return datetime.datetime.fromtimestamp((math.e ** ln_timestamp)).strftime('%d/%m/%Y')

def read_curve(filename):
    # Ruta relativa desde src/ hacia data/ (un nivel arriba)
    data_path = Path(__file__).parent.parent / 'data' / filename
    curve = pd.read_csv(data_path, sep=';', encoding='utf-8-sig')
    # Convertimos las fechas a ln(timestamp) para poder interpolar posteriormente
    curve['Date'] = curve['Date'].apply(to_ln_timestamp)
    return curve

def plot_curve(curve):
    curve_plt = curve.copy()
    columns = curve_plt.columns.drop('Date').values
    curve_plt['Date'] = curve_plt['Date'].apply(from_ln_timestamp)
    plt.plot(curve_plt['Date'], curve_plt[columns], label=columns)
    plt.xticks(curve_plt['Date'][::5], rotation=45)

def evaluate_bond(date, bond, curve, spread):
    clean_price = 0
    dirty_price = 0
    accrued_interest = 0

    coupon = bond['Coupon']
    nominal = bond['Price']
    maturity_date = bond['Maturity']
    coupon_freq = bond['Coupon Frequency']
    first_coupon_date = pd.to_datetime(bond['First Coupon Date'])
    next_coupon_date = first_coupon_date

    while (next_coupon_date < date):
        next_coupon_date = next_coupon_date + relativedelta(years=coupon_freq)
    last_coupon_date = next_coupon_date - relativedelta(years=coupon_freq)

    days_from_last_coupon_payment = (date - last_coupon_date).days
    days_until_next_coupon_payment = (next_coupon_date - date).days
    accrued_interest = coupon * days_from_last_coupon_payment/days_until_next_coupon_payment

    bond_price = 0
    # TODO
    # Calcular la funcion de interpolacion
    # Con la funcion de interpolacion, sacar el ytm en el siguiente pago
    # Calcular el precio sucio
    # Calcular el precio limpio
    # Devolver un DF con todos los nuevos campos

def interpolate(curve, date, column='Discount'):
    ln_date = to_ln_timestamp(date)
    return np.interp(ln_date, curve['Date'], curve[column])