import pandas as pd
import numpy as np

# Leer el archivo CSV
df = pd.read_csv('data/universo.csv', sep=';')

print("=" * 80)
print("ANÁLISIS DE GAPS DE DATOS EN universo.csv")
print("=" * 80)
print(f"\nTotal de registros: {len(df)}")
print(f"Total de columnas: {len(df.columns)}")
print(f"\nColumnas: {list(df.columns)}")

print("\n" + "=" * 80)
print("1. VALORES FALTANTES POR COLUMNA")
print("=" * 80)
missing_data = df.isnull().sum()
missing_percent = (missing_data / len(df)) * 100
missing_info = pd.DataFrame({
    'Columna': missing_data.index,
    'Valores Faltantes': missing_data.values,
    'Porcentaje (%)': missing_percent.values
})
missing_info = missing_info[missing_info['Valores Faltantes'] > 0].sort_values('Valores Faltantes', ascending=False)
if len(missing_info) > 0:
    print(missing_info.to_string(index=False))
else:
    print("No se encontraron valores faltantes (NaN)")

print("\n" + "=" * 80)
print("2. CAMPOS VACÍOS (STRING VACÍO)")
print("=" * 80)
empty_strings = {}
for col in df.columns:
    if df[col].dtype == 'object':
        empty_count = (df[col] == '').sum()
        if empty_count > 0:
            empty_strings[col] = empty_count

if empty_strings:
    for col, count in sorted(empty_strings.items(), key=lambda x: x[1], reverse=True):
        print(f"{col}: {count} valores vacíos ({count/len(df)*100:.2f}%)")
else:
    print("No se encontraron campos vacíos")

print("\n" + "=" * 80)
print("3. VALORES ESPECIALES O PROBLEMÁTICOS")
print("=" * 80)

# Buscar valores como #N/A, N/A, etc.
special_values = {}
for col in df.columns:
    if df[col].dtype == 'object':
        na_variants = df[col].str.contains(r'#?N/A|n/a|NULL|null', case=False, na=False).sum()
        if na_variants > 0:
            special_values[col] = na_variants

if special_values:
    for col, count in sorted(special_values.items(), key=lambda x: x[1], reverse=True):
        print(f"{col}: {count} valores con formato N/A")
        # Mostrar ejemplos
        examples = df[df[col].str.contains(r'#?N/A|n/a', case=False, na=False)][col].head(3).tolist()
        print(f"  Ejemplos: {examples}")
else:
    print("No se encontraron valores especiales problemáticos")

print("\n" + "=" * 80)
print("4. ANÁLISIS DE COLUMNAS DE FECHAS")
print("=" * 80)
date_columns = ['Maturity', 'Next Call Date', 'First Coupon Date', 
                'Penultimate Coupon Date', 'Issue date']
for col in date_columns:
    if col in df.columns:
        print(f"\n{col}:")
        # Contar valores vacíos
        empty = (df[col] == '').sum() if df[col].dtype == 'object' else df[col].isnull().sum()
        print(f"  - Valores vacíos/faltantes: {empty} ({empty/len(df)*100:.2f}%)")
        
        # Intentar convertir a fecha y ver cuántos fallan
        if df[col].dtype == 'object':
            try:
                dates = pd.to_datetime(df[col], errors='coerce')
                invalid_dates = dates.isnull().sum() - empty
                if invalid_dates > 0:
                    print(f"  - Fechas inválidas (no vacías): {invalid_dates}")
            except:
                pass

print("\n" + "=" * 80)
print("5. ANÁLISIS DE COLUMNAS NUMÉRICAS")
print("=" * 80)
numeric_columns = ['Price', 'Coupon', 'PD 1YR', 'Outstanding Amount', 
                   'Bid Price', 'Ask Price']
for col in numeric_columns:
    if col in df.columns:
        print(f"\n{col}:")
        # Valores faltantes
        missing = df[col].isnull().sum()
        print(f"  - Valores faltantes: {missing} ({missing/len(df)*100:.2f}%)")
        
        # Valores cero o negativos (pueden ser problemáticos según el campo)
        if col in ['Price', 'Bid Price', 'Ask Price', 'Outstanding Amount']:
            zeros = (df[col] == 0).sum()
            negatives = (df[col] < 0).sum()
            if zeros > 0:
                print(f"  - Valores cero: {zeros}")
            if negatives > 0:
                print(f"  - Valores negativos: {negatives}")

print("\n" + "=" * 80)
print("6. ANÁLISIS DE COLUMNA 'Callable'")
print("=" * 80)
if 'Callable' in df.columns:
    print(df['Callable'].value_counts())
    # Verificar si hay valores faltantes cuando Callable = 'Y'
    if 'Next Call Date' in df.columns:
        callable_y = df[df['Callable'] == 'Y']
        missing_call_date = (callable_y['Next Call Date'] == '').sum() if callable_y['Next Call Date'].dtype == 'object' else callable_y['Next Call Date'].isnull().sum()
        print(f"\nBonos callable (Y) sin 'Next Call Date': {missing_call_date} de {len(callable_y)}")

print("\n" + "=" * 80)
print("7. ANÁLISIS DE COLUMNA 'Maturity'")
print("=" * 80)
if 'Maturity' in df.columns:
    # Bonos perpétuos (sin maturity)
    if df['Maturity'].dtype == 'object':
        perpetual = (df['Maturity'] == '').sum()
        print(f"Bonos perpétuos (sin Maturity): {perpetual}")
        if perpetual > 0:
            print("Ejemplos de bonos perpétuos:")
            print(df[df['Maturity'] == ''][['ISIN', 'Description', 'Maturity']].head())

print("\n" + "=" * 80)
print("8. CONSISTENCIA DE DATOS")
print("=" * 80)

# Verificar que Bid Price < Ask Price cuando ambos existen
if 'Bid Price' in df.columns and 'Ask Price' in df.columns:
    both_present = df[df['Bid Price'].notna() & df['Ask Price'].notna()]
    inconsistent_spread = (both_present['Bid Price'] >= both_present['Ask Price']).sum()
    print(f"Casos donde Bid Price >= Ask Price: {inconsistent_spread}")

# Verificar que Price está entre Bid y Ask (aproximadamente)
if all(col in df.columns for col in ['Price', 'Bid Price', 'Ask Price']):
    all_present = df[df[['Price', 'Bid Price', 'Ask Price']].notna().all(axis=1)]
    price_outside_spread = ((all_present['Price'] < all_present['Bid Price']) | 
                           (all_present['Price'] > all_present['Ask Price'])).sum()
    print(f"Casos donde Price está fuera del spread Bid-Ask: {price_outside_spread}")

print("\n" + "=" * 80)
print("9. RESUMEN DE GAPS ENCONTRADOS")
print("=" * 80)

total_gaps = 0
gap_summary = []

# Valores NaN
for col in df.columns:
    missing = df[col].isnull().sum()
    if missing > 0:
        total_gaps += missing
        gap_summary.append(f"- {col}: {missing} valores NaN")

# Strings vacíos
for col in df.columns:
    if df[col].dtype == 'object':
        empty = (df[col] == '').sum()
        if empty > 0:
            total_gaps += empty
            gap_summary.append(f"- {col}: {empty} campos vacíos")

# Valores especiales
for col in df.columns:
    if df[col].dtype == 'object':
        special = df[col].str.contains(r'#?N/A|n/a', case=False, na=False).sum()
        if special > 0:
            total_gaps += special
            gap_summary.append(f"- {col}: {special} valores con formato N/A")

if gap_summary:
    print(f"Total de gaps encontrados: {total_gaps}")
    print("\nDetalle:")
    for gap in gap_summary:
        print(gap)
else:
    print("No se encontraron gaps significativos")

