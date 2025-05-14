import streamlit as st

from App_data_Olist import load_csv


#Seleccion columnas
df_select_customer = load_csv.df_customer[['customer_id', 'customer_city', 'customer_state']]
df_select_orders = load_csv.df_orders[['order_id', 'customer_id', 'order_status','order_purchase_timestamp','order_approved_at','order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']]

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
late_df = late_by_city.sort_values(ascending=False).reset_index()
late_df.columns = ['Ciudad', 'Pedidos_Retrasados']
top = late_df.head(top_n)
# Gráfico con Altair
chart = alt.Chart(top).mark_bar(color='#66c2a5').encode(
    y=alt.Y('Pedidos_Retrasados:Q', title='Pedidos Retrasados'),
    x=alt.X('Ciudad:N', sort='-y', title='Ciudad'),
    tooltip=['Ciudad', 'Pedidos_Retrasados']
).properties(
    title='Top ciudades con más pedidos retrasados',
    width=700,
    height=400
)

# Mostrar gráfico
st.altair_chart(chart, use_container_width=True)
