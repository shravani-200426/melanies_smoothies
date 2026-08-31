# Import python packages
import streamlit as st
import requests
import pandas as pd

# Write directly to the app
st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Create a connection to Snowflake
conn = st.connection("snowflake")
session = conn.session()

# Add name input
name_on_order = st.text_input("Name on order:")

# Get fruit names and API search values from Snowflake
my_dataframe = session.table(
    "smoothies.public.fruit_options"
).select("FRUIT_NAME", "SEARCH_ON")

# Convert Snowpark dataframe to Pandas dataframe
pd_df = my_dataframe.to_pandas()

# Create list for the multiselect
fruit_list = pd_df["FRUIT_NAME"].tolist()

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

        # Find the SEARCH_ON value for the selected fruit
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # Show the value being used for the API search
        st.write(
            "The search value for ",
            fruit_chosen,
            " is ",
            search_on,
            "."
        )

        # Call SmoothieFroot API using SEARCH_ON
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on.lower().replace(' ', '')}"
        )

        # Check if API call was successful
        if smoothiefroot_response.status_code == 200:

            api_data = smoothiefroot_response.json()

            st.write(f"### {fruit_chosen}")
            st.json(api_data)

        else:
            st.write(
                f"Could not get nutrition information for {fruit_chosen}"
            )

# Create ingredients string
ingredients_string = ", ".join(ingredients)

# Create Submit button
submit = st.button("Submit")

# Insert order into Snowflake
if submit:

    if not name_on_order:
        st.warning("Please enter your name.")

    elif not ingredients:
        st.warning("Please choose at least one ingredient.")

    else:
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders
            (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """

        session.sql(my_insert_stmt).collect()

        st.success(
            "Your Smoothie is ordered!",
            icon="✅"
        )
