import pandas as pd
import numpy as np
import seaborn as sns
import streamlit as st
import matplotlib.pyplot as plt


#Leemos los dos archivos CSV para los dos primeros ejercicios

df = pd.read_csv('recursos/Olist_Data/olist_customers_dataset.csv') 
df2 = pd.read_csv('recursos/Olist_Data/olist_orders_dataset.csv')

#Formateamos la fecha del dataset para poder trabajar con el campo 

df2["order_purchase_timestamp"] = pd.to_datetime(df2["order_purchase_timestamp"])

#Realizamos el merge de los dos CSV utilizando el campo en común

df_final = df.merge(df2, on="customer_id")

#Obtenemos la fecha minima del dataset y máxima del dataset para introducirla como preestablecida en el dateinput de streamlit

min_fecha = df_final["order_purchase_timestamp"].min().date()
max_fecha = df_final["order_purchase_timestamp"].max().date()

#Creamos el date input, lo utilizaremos para poder variar la fecha y que el gráfico cambie en función de las fechas

fecha_inicio, fecha_fin = st.date_input("Selecciona un rango de fechas", [min_fecha, max_fecha])
   
fecha_inicio = pd.to_datetime(fecha_inicio)
fecha_fin = pd.to_datetime(fecha_fin)

df_filtrado = df_final[(df_final["order_purchase_timestamp"] >= fecha_inicio) & (df_final["order_purchase_timestamp"] <= fecha_fin)]
  
top_estados = df_filtrado["customer_state"].value_counts(ascending=False).head(5)

st.subheader("Estados con más clientes en el rango de fechas seleccionado")

#Gráfico streamlit con los 5 estados con mas clientes en un rango de fechas variable

st.bar_chart(top_estados)

tabla = df_filtrado.groupby(["customer_state", "customer_city"])["customer_id"].nunique().reset_index(name="num_clientes")
tabla2 = df_final.groupby('customer_city')['order_id'].count().reset_index(name='num_pedidos_ciudad')
total2 = tabla2['num_pedidos_ciudad'].sum()
tabla2['numero de pedidos y %'] = tabla2['num_pedidos_ciudad'].apply(
    lambda x: f"{x} pedidos ({(x / total2 * 100):.1f}%)"
)
tabla_completa = pd.merge(tabla, tabla2, on='customer_city')
tabla_completa = tabla_completa.sort_values(by="num_clientes", ascending=False)
tabla_completa.pop('num_pedidos_ciudad')
st.subheader("Clientes por estado y ciudad")
st.dataframe(tabla_completa)


#========================================================================================

st.title("Distribución de Pedidos por Ciudad")

# Ordenar por cantidad de pedidos y seleccionar las top N
top_n = st.slider('Selecciona cuántas ciudades mostrar (Top N)', min_value=3, max_value=20, value=10)

tabla_top = tabla_completa.sort_values(by='num_clientes', ascending=False).head(top_n)

# Gráfico de pastel
fig, ax = plt.subplots()
ax.pie(
    tabla_top['num_clientes'],
    labels=tabla_top['customer_city'],
    autopct='%1.1f%%',
    startangle=140
)
ax.axis('equal')  # Mantiene el círculo
plt.title(f'Distribución porcentual de pedidos por ciudad (Top {top_n})')

st.pyplot(fig)