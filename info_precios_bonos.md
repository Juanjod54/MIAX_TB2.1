# Información necesaria de universo.csv para análisis de precios de bonos

## 📊 Información esencial para valoración y análisis de precios

### 1. **Precios de mercado** (información directa de precios)
- **`Price`**: Precio medio/mid del bono (precio de referencia)
- **`Bid Price`**: Precio de compra (precio al que puedes vender)
- **`Ask Price`**: Precio de venta (precio al que puedes comprar)
- **Spread Bid-Ask**: Diferencia entre Ask y Bid (indica liquidez)
  - Spread grande = menor liquidez
  - Spread pequeño = mayor liquidez

### 2. **Características del cupón** (necesarias para valoración)
- **`Coupon`**: Tasa de cupón anual (ej: 4.5 = 4.5%)
- **`Coupon Frequency`**: Frecuencia de pago (1 = anual, 2 = semestral, 4 = trimestral)
- **`Coupon Type`**: Tipo de cupón
  - `FIXED`: Cupón fijo (necesario para valoración estándar)
  - `VARIABLE`: Cupón variable (requiere curva de referencia adicional)
- **`First Coupon Date`**: Fecha del primer pago de cupón
- **`Penultimate Coupon Date`**: Fecha del penúltimo cupón
- **`Issue date`**: Fecha de emisión del bono

### 3. **Fechas críticas** (necesarias para cálculos de valoración)
- **`Maturity`**: Fecha de vencimiento del bono
  - ⚠️ **IMPORTANTE**: Algunos bonos pueden ser perpetuos (campo vacío)
  - Para perpetuos, usar `Next Call Date` como fecha de referencia
- **`Next Call Date`**: Fecha de la próxima opción de compra (call)
  - Crítica si `Callable = 'Y'`
  - Para bonos perpetuos, esta es la fecha de referencia para valoración

### 4. **Características de la emisión** (afectan valoración y riesgo)
- **`Callable`**: Si el bono es rescatable
  - `Y`: Sí es callable (afecta la valoración, usar Next Call Date)
  - `N`: No es callable
- **`Seniority`**: Prioridad en caso de default
  - `Sr Unsecured`: Senior no garantizado
  - `Sr Preferred`: Senior preferente
  - `Subordinated`: Subordinado (mayor riesgo)
  - `Jr Subordinated`: Junior subordinado (máximo riesgo)
- **`Outstanding Amount`**: Tamaño de la emisión (afecta liquidez)

### 5. **Información de riesgo** (para análisis de spreads y valoración ajustada)
- **`Rating`**: Calificación crediticia
  - `AAA`, `AA`, `A`, `BBB`: Investment Grade (IG)
  - `BB`, `B`, `CCC`, etc.: High Yield (HY)
  - `NR`: No rated
- **`PD 1YR`**: Probabilidad de default a 1 año
  - Necesaria para calcular spreads de crédito
  - Usada en modelos de valoración ajustados por riesgo

### 6. **Información adicional** (contexto y filtros)
- **`ISIN`**: Identificador único del bono
- **`Description`**: Descripción del bono
- **`Ccy`**: Moneda (EUR en este caso)
- **`Issuer`**: Emisor del bono
- **`Industry Sector`**: Sector industrial (para análisis de concentración)

---

## 🔍 Análisis específico según el objetivo

### Para **valoración teórica del bono**:
```
Necesitas:
✓ Maturity (o Next Call Date si es perpetuo/callable)
✓ Coupon
✓ Coupon Frequency
✓ Coupon Type
✓ First Coupon Date
✓ Issue date
✓ Curva de tipos de interés (€STR)
✓ Spread de crédito (calculado o estimado)
```

### Para **comparar con precios de mercado**:
```
Necesitas:
✓ Price (precio teórico calculado)
✓ Price del CSV (precio de mercado)
✓ Bid Price y Ask Price (para ver spread de liquidez)
```

### Para **calcular Yield, Duración y Convexidad**:
```
Necesitas:
✓ Price (o precio de mercado)
✓ Coupon
✓ Coupon Frequency
✓ Maturity
✓ Fechas de cupones
```

### Para **análisis de spreads**:
```
Necesitas:
✓ Price de mercado
✓ Curva de descuento (€STR)
✓ Características del cupón
✓ Maturity
✓ Rating / PD 1YR (para análisis de riesgo de crédito)
```

### Para **análisis de liquidez**:
```
Necesitas:
✓ Bid Price
✓ Ask Price
✓ Outstanding Amount
✓ Spread Bid-Ask = Ask Price - Bid Price
```

---

## ⚠️ Gaps de datos a verificar

1. **Maturity vacío**: Bonos perpetuos → usar Next Call Date
2. **Next Call Date vacío**: Si Callable='Y' pero sin fecha → problema
3. **Fechas inválidas**: Verificar formato de fechas
4. **Precios faltantes**: Price, Bid Price, Ask Price
5. **Coupon Type = VARIABLE**: Requiere información adicional de curva de referencia
6. **Rating = NR**: Sin calificación → mayor incertidumbre en spreads

---

## 💡 Recomendaciones

1. **Usar Price (mid) para cálculos teóricos** cuando esté disponible
2. **Usar Bid/Ask para análisis de trading** (costes de transacción)
3. **Verificar consistencia**: Bid Price ≤ Price ≤ Ask Price
4. **Para bonos perpetuos**: Tratar como bonos con vencimiento en Next Call Date
5. **Para bonos callable**: Considerar la opción de call en la valoración
6. **Spread Bid-Ask alto**: Indicador de baja liquidez → puede afectar ejecución

