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
late_by_city = df_merge_delivered.groupby('customer_city')['too_late'].sum().sort_values(ascending=False)

# Título
st.title("Pedidos retrasados por ciudad")
# Selector: número de ciudades a mostrar
top_n = st.slider("Selecciona cuántas ciudades quieres mostrar", min_value=5, max_value=30, value=10)
# Mostrar gráfica con top N ciudades
st.bar_chart(late_by_city.head(top_n), color="#66c2a5")

#Agrupa por ciudad y cuenta la cantidad total de pedidos
orders_by_city = df_merge.groupby('customer_city')['order_id'].count()
#Porcentaje de retrasdos por ciudad
procent_by_city = (late_by_city/orders_by_city) * 100
#Rellenamos los posibles nulos
procent_by_city = procent_by_city.fillna(0)

#Vemos los dias retrasados
df_merge_delivered['delay_days'] = (df_merge_delivered['order_delivered_customer_date'] - df_merge_delivered['order_estimated_delivery_date']).dt.days


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
#Filtramos solo los retrasos (días > 0)
late_only = df_merge_delivered[df_merge_delivered['delay_days'] > 0]
#Media de retrasos por ciudad
mean_delay_by_city = late_only.groupby('customer_city')['delay_days'].mean().sort_values(ascending=False)


# Solo ciudades con retraso
ciudades_con_retraso = late_only['customer_city'].unique()

# Filtramos el porcentaje solo a esas ciudades
procent_by_city_filtrado = procent_by_city[procent_by_city.index.isin(ciudades_con_retraso)]

#Titulo
st.title("Resumen de Retrasos por Ciudad")
causa_principal = late_only.groupby('customer_city')['delay_cause'].first()
causa_principal = causa_principal.rename("Causa Principal")
 
# Agrupamos por ciudad 
resumen = pd.concat([
        procent_by_city_filtrado.rename("Porcentaje de Retrasos"),
        mean_delay_by_city.rename("Media de Días de Retraso"),
        causa_principal
          ], axis=1).round(2).sort_values(by="Porcentaje de Retrasos", ascending=False)
# Cambiamos nombre de primera columna
resumen = resumen.reset_index().rename(columns={'customer_city': 'Ciudad'})
st.dataframe(resumen)


#Filtramos los pedidos sin delay
df_no_late = df_merge_delivered[df_merge_delivered['delay_days'] <= 0]
#Hacemos merge de tabla de pedidos y de reviews
df_merge_review_non_delayed = pd.merge(df_no_late, df_review,on = 'order_id')
#Selecciona columnas a utilizar
df_merge_review_non_delayed = df_merge_review_non_delayed[['order_id', 'customer_state', 'review_score', 'review_id']]
print(df_merge_review_non_delayed.columns)
#Cuenta las reviews por estado
review_count =  df_merge_review_non_delayed.groupby('customer_state')['review_id'].count()
#Hace la media de las notas de esas reviews
review_mean = round(df_merge_review_non_delayed.groupby('customer_state')['review_score'].mean(),2)

review_stats = pd.concat([review_count, review_mean], axis=1)

print(review_stats)

# Título
st.title("Análisis de Reviews por Estado")
# Selector 1: tipo de gráfico
opcion = st.selectbox("Selecciona qué gráfico quieres visualizar:",
    ("Número de reviews por estado", "Media de puntuación por estado"))

# Selector 2: cuántos estados mostrar 
# Mira cuantos estados hay en total
max_estados = len(review_count)
# Deja seleccionar el numero, con un minimo, un maximo y estableciendo el estandar en 10
top_n = st.slider("Número de estados a mostrar", min_value=3, max_value=max_estados, value=10)

# Mostrar gráfico según opción
if opcion == "Número de reviews por estado":
    st.bar_chart(review_count.sort_values(ascending=False).head(top_n))
elif opcion == "Media de puntuación por estado":
    st.bar_chart(review_mean.sort_values(ascending=False).head(top_n))
