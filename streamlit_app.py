# Import python packages
import streamlit as st
import os

# Import Snowpark column function
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!"""
)

# Create a connection to Snowflake
conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))
session = conn.session()

# Add name input
name_on_order = st.text_input("Name on order:")

# Get only the FRUIT_NAME column
my_dataframe = session.table("smoothies.public.fruit_options").select(
    col("FRUIT_NAME")
)

# Create a multiselect widget
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe,
    max_selections=5
)

# Create an empty string
ingredients_string = ""

# Convert the list to a string
if ingredients:
    for fruit_chosen in ingredients:
        ingredients_string += fruit_chosen

    st.write("Your ingredients as a string:", ingredients_string)

# Build the SQL INSERT statement
my_insert_stmt = """insert into smoothies.public.orders
                    (ingredients, name_on_order)
                    values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

# Create Submit button
submit = st.button("Submit")

# Insert the order into Snowflake
if submit:
    session.sql(my_insert_stmt).collect()
    st.success('Your Smoothie is ordered!', icon="✅")
