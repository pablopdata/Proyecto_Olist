import pandas as pd
import streamlit as st
import numpy as np
#Carga de csv
df_customer = pd.read_csv('recursos\Olist_Data\olist_customers_dataset.csv')
df_orders = pd.read_csv('recursos\Olist_Data\olist_orders_dataset.csv')

#Seleccion columnas
df_select_customer = df_customer[['customer_id', 'customer_city', 'customer_state']]
df_select_orders = df_orders[['order_id', 'customer_id', 'order_status','order_purchase_timestamp','order_approved_at','order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']]

#Merge de df
df_merge = df_merge = pd.merge(df_select_customer, df_select_orders, on='customer_id')
print(df_merge.columns)
#Dejamos la fecha solo en dias
df_merge['order_delivered_customer_date'] = pd.to_datetime(df_merge['order_delivered_customer_date']).dt.date
df_merge['order_estimated_delivery_date'] = pd.to_datetime(df_merge['order_estimated_delivery_date']).dt.date

#Filtra los pedidos que tienen el estado entregado
delivered = df_merge['order_status'] == "delivered"
df_merge_delivered = df_merge[delivered].copy()
#Posibles estados del pedido
status = df_merge['order_status'].unique()
#Crea una columna donde True indica que el pedido llego tarde y False que llego a tiempo
df_merge_delivered['too_late'] = df_merge_delivered['order_delivered_customer_date'] > df_merge_delivered['order_estimated_delivery_date']
#Agrupa por ciudad y cuenta la cantidad de pedidos retrasados
late_by_city = df_merge_delivered.groupby('customer_city')['too_late'].sum().head(5)


st.bar_chart(late_by_city)
#Agrupa por ciudad y cuenta la cantidad total de pedidos
orders_by_city = df_merge.groupby('customer_city')['order_id'].count()
#Porcentaje de retrasdos por ciudad
procent_by_city = (late_by_city/orders_by_city) * 100
#Rellenamos los posibles nulos
procent_by_city = procent_by_city.fillna(0)
#Vemos los dias retrasados
df_merge_delivered['delay_days'] = (df_merge_delivered['order_delivered_customer_date'] - df_merge_delivered['order_estimated_delivery_date']).dt.days
#Filtramos solo los retrasos (días > 0)
late_only = df_merge_delivered[df_merge_delivered['delay_days'] > 0]
#Media de retrasos por ciudad
mean_delay_by_city = late_only.groupby('customer_city')['delay_days'].mean().sort_values(ascending=False)

#Titulo
st.title("Media de Días de Retraso por Ciudad")

# Mostrar tabla
st.dataframe(mean_delay_by_city.reset_index().rename(columns={'delay_days': 'media_retraso_dias'}))

# Gráfico de barras
st.bar_chart(mean_delay_by_city.head(20)) 

#Motivo del retraso
df_merge_delivered['approved_time'] = (df_merge_delivered['order_approved_at'] - df_merge_delivered['order_purchase_timestamp']).dt.days
df_merge_delivered['preparation_time'] = (df_merge_delivered['order_delivered_carrier_date'] - df_merge['order_approved_at']).dt.days
df_merge_delivered['delivery_time'] = (df_merge['order_delivered_customer_date'] - df_merge['order_delivered_carrier_date']).dt.days

import numpy as np

# Condición: solo si hubo retraso
condiciones = [
    df_merge['dias_retraso'] > 0,  # Hay retraso
]

# Evaluamos cuál de los tiempos fue mayor
razones = np.select([
        (df_merge['delivered_time'] > df_merge['preparation_time']) & 
        (df_merge['delivered_time'] > df_merge['tiempo_aprobacion']),
        
        (df_merge['preparation_time'] > df_merge['delivered_time']) & 
        (df_merge['preparation_time'] > df_merge['approved_time']),
        
        (df_merge['approved_time'] > df_merge['delivered_time']) & 
        (df_merge['approved_time'] > df_merge['preparation_time']),],
    ['envío', 'preparación', 'aprobación'],
    default='a_tiempo'
)
# Asignamos al dataframe
df_merge['delay_cause'] = razones


