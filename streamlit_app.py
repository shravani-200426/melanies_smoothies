# Import python packages
import streamlit as st
import requests

# Write directly to the app
st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Create a connection to Snowflake
conn = st.connection("snowflake")
session = conn.session()

# Add name input
name_on_order = st.text_input("Name on order:")

# Get fruit names from Snowflake
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select("FRUIT_NAME")

# Create a list of fruit names
fruit_list = my_dataframe.to_pandas()["FRUIT_NAME"].tolist()

# Create a multiselect widget
ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# Show nutrition information for selected fruits
if ingredients:
    st.subheader("Nutrition Information")

    for fruit_chosen in ingredients:

        # Call SmoothieFroot API
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen.lower()}"
        )

        # Check if API call was successful
        if smoothiefroot_response.status_code == 200:
            fruit_data = smoothiefroot_response.json()

            st.write(f"### {fruit_chosen}")
            st.json(fruit_data)

        else:
            st.write(
                f"Could not get nutrition information for {fruit_chosen}"
            )

# Create an empty string
ingredients_string = ""

# Convert the list to a string
if ingredients:
    ingredients_string = ", ".join(ingredients)

# Build the SQL INSERT statement
my_insert_stmt = """
    INSERT INTO smoothies.public.orders
    (ingredients, name_on_order)
    VALUES (%s, %s)
"""

# Create Submit button
submit = st.button("Submit")

# Insert the order into Snowflake
if submit:

    if not name_on_order:
        st.warning("Please enter your name.")

    elif not ingredients:
        st.warning("Please choose at least one ingredient.")

    else:
        session.sql(
            my_insert_stmt,
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success(
            "Your Smoothie is ordered!",
            icon="✅"
        )
