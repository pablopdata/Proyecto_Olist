import pandas as pd
import streamlit as st
import numpy as np
#Carga de csv
df_customer = pd.read_csv('recursos\Olist_Data\olist_customers_dataset.csv')
df_orders = pd.read_csv('recursos\Olist_Data\olist_orders_dataset.csv')
df_review = pd.read_csv('recursos\Olist_Data\olist_order_reviews_dataset.csv')

#Seleccion columnas
df_select_customer = df_customer[['customer_id', 'customer_city', 'customer_state']]
df_select_orders = df_orders[['order_id', 'customer_id', 'order_status','order_purchase_timestamp','order_approved_at','order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']]

#Merge de df
df_merge = df_merge = pd.merge(df_select_customer, df_select_orders, on='customer_id')
print(df_merge.columns)
#Dejamos la fecha solo en dias
df_merge['order_delivered_customer_date'] = pd.to_datetime(df_merge['order_delivered_customer_date']).dt.date
df_merge['order_estimated_delivery_date'] = pd.to_datetime(df_merge['order_estimated_delivery_date']).dt.date
df_merge['order_purchase_timestamp'] = pd.to_datetime(df_merge['order_purchase_timestamp']).dt.date
df_merge['order_approved_at'] = pd.to_datetime(df_merge['order_approved_at']).dt.date
df_merge['order_delivered_carrier_date'] = pd.to_datetime(df_merge['order_delivered_carrier_date']).dt.date

#Filtra los pedidos que tienen el estado entregado
delivered = df_merge['order_status'] == "delivered"
df_merge_delivered = df_merge[delivered].copy()
#Posibles estados del pedido
status = df_merge['order_status'].unique()
#Crea una columna donde True indica que el pedido llego tarde y False que llego a tiempo
df_merge_delivered['too_late'] = df_merge_delivered['order_delivered_customer_date'] > df_merge_delivered['order_estimated_delivery_date']
#Agrupa por ciudad y cuenta la cantidad de pedidos retrasados
late_by_city = df_merge_delivered.groupby('customer_city')['too_late'].sum().sort_values(ascending=False).head(10)

#Titulo
st.title("Pedidos retrasados por ciudad")
st.bar_chart(late_by_city, x_label="City", y_label="Quantity of delayed delivery", color= "#ffaa00")

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
st.dataframe(mean_delay_by_city)

# Gráfico de barras
st.bar_chart(mean_delay_by_city.head(20)) 

#Motivo del retraso
df_merge_delivered['approved_time'] = (df_merge_delivered['order_approved_at'] - df_merge_delivered['order_purchase_timestamp']).dt.days
df_merge_delivered['preparation_time'] = (df_merge_delivered['order_delivered_carrier_date'] - df_merge['order_approved_at']).dt.days
df_merge_delivered['delivery_time'] = (df_merge['order_delivered_customer_date'] - df_merge['order_delivered_carrier_date']).dt.days

# Condición: solo si hubo retraso
condiciones = [
    df_merge_delivered['delay_days'] > 0, 
]

# Evaluamos cuál de los tiempos fue mayor
razones = np.select([
        (df_merge_delivered['delivery_time'] > df_merge_delivered['preparation_time']) & 
        (df_merge_delivered['delivery_time'] > df_merge_delivered['approved_time']),
        
        (df_merge_delivered['preparation_time'] > df_merge_delivered['delivery_time']) & 
        (df_merge_delivered['preparation_time'] > df_merge_delivered['approved_time']),
        
        (df_merge_delivered['approved_time'] > df_merge_delivered['delivery_time']) & 
        (df_merge_delivered['approved_time'] > df_merge_delivered['preparation_time']),],
    ['envío', 'preparación', 'aprobación'],
    default='a_tiempo'
)
# Asignamos al dataframe
df_merge_delivered['delay_cause'] = razones


#Filtramos los pedidos sin delay
df_no_late = df_merge_delivered[df_merge_delivered['delay_days'] <= 0]
#Hacemos merge de tabla de pedidos y de reviews
df_merge_review_non_delayed = pd.merge(df_no_late, df_review,on = 'order_id')
#Selecciona columnas a utilizar
df_merge_review_non_delayed = df_merge_review_non_delayed[['order_id', 'customer_state', 'review_score', 'review_id']]
print(df_merge_review_non_delayed.columns)

review_count =  df_merge_review_non_delayed.groupby('customer_state')['review_id'].count()
review_count['mean_score'] = df_merge_review_non_delayed.groupby('review_id')['review_score'].mean()

print(review_count)