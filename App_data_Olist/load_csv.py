import pandas as pd

#Carga de csv
df_customer = pd.read_csv('recursos\Olist_Data\olist_customers_dataset.csv')
df_orders = pd.read_csv('recursos\Olist_Data\olist_orders_dataset.csv')
df_review = pd.read_csv('recursos\Olist_Data\olist_order_reviews_dataset.csv')
df_items = pd.read_csv('recursos\Olist_Data\olist_order_items_dataset.csv')
df_products = pd.read_csv('recursos\Olist_Data\olist_products_dataset.csv')
df_translation = pd.read_csv('recursos\Olist_Data\product_category_name_translation.csv')
