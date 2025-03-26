import streamlit as st
import requests

# Title of the app
st.title("Supply Chain Agent")

# Input field for the user query
query = st.text_input("Enter your query:")

# Submit button
if st.button("Submit"):
    if query.strip():  # Check if the query is not empty
        with st.spinner("Fetching response..."):  # Show a loading spinner
            try:
                # Send the query to the backend API
                response = requests.post(
                    "http://127.0.0.1:8000/query/",
                    json={"query": query}
                )

                # Check the response status
                if response.status_code == 200:
                    st.success("Response received!")
                    st.write("Response:", response.json()["response"])
                else:
                    # Display the error message from the backend
                    error_message = response.json().get("detail", "Unknown error")
                    st.error(f"Error: {error_message}")
            except Exception as e:
                # Handle any unexpected errors
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a query.")