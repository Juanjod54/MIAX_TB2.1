import pandas as pd
from datetime import datetime
from pathlib import Path
from dateutil.relativedelta import relativedelta

def read_curve(filename):
    # Ruta relativa desde src/ hacia data/ (un nivel arriba)
    data_path = Path(__file__).parent.parent / 'data' / filename
    curve = pd.read_csv(data_path, sep=';', encoding='utf-8-sig')
    return curve

def plot_curve(curve):
    curve.plot()

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