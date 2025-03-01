import streamlit as st
import pandas as pd
import pymysql
from streamlit_option_menu import option_menu

# Function to establish a database connection
def connect_to_tidb():
    try:
        conn = pymysql.connect(
            host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
            port=4000,
            user="CX5EJS1zx2L6stA.root",  # Ensure this is correct!
            password="usboEd1nOyLvwbLk",  # Ensure this is correct!
            database="first",
            ssl_ca="c:/users/inbak/downloads/isrgrootx1.pem"  # Ensure this file exists!
        )
        return conn
    except pymysql.MySQLError as e:  # Corrected to MySQLError
        st.error(f"Database connection error: {e}")
        return None  # Use None instead of 'none'

# Function to close the connection
def close_connection(conn):
    if conn:
        conn.close()

# Streamlit UI setup
st.markdown(
    """
    <h1 style="text-align:center; color: red;">Welcome to Zomato</h1>
    <h6 style="text-align:center;color:green;">Better food for everyone</h6>
    """,
    unsafe_allow_html=True  # Use True instead of lowercase 'true'
)

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Zomato Data View",
        options=["Home", "Main", "CRUD", "Queries"],
        icons=["house", "book-fill", "pencil", "floppy"],
        default_index=0
    )

# Display image if 'Home' is selected
if selected == "Home":
    st.image(r"c:\users\inbak\onedrive\zomato\zomato-marketing-strategy-–-a-case-study-2023-1.webp")
else:
    st.write(f"Showing data for: {selected}")  # Provide feedback on selected option

# Sidebar for table selection if "Main" is selected
if selected == "Main":
    table_options = ["customers_table", "restaurants_table", "orders_table", "deliveries_table", "delivery_persons_table", "None"]
    selected_table = st.sidebar.selectbox("Select Table", table_options)

    # Connect to the database
    conn = connect_to_tidb()
    if conn:
        try:
            with conn.cursor() as cur:  # Use 'with' for cursor management
                # Mapping table selection to actual database table names
                table_map = {
                    "customers_table": "customers",
                    "restaurants_table": "restaurants",
                    "orders_table": "orders",
                    "deliveries_table": "deliveries",
                    "delivery_persons_table": "delivery_persons",
                }

                table_name = table_map.get(selected_table)
                if table_name:
                    query = f"SELECT * FROM {table_name}"  # Use uppercase SQL keywords for readability
                    cur.execute(query)
                    data = cur.fetchall()
                    columns = [col[0] for col in cur.description]

                    # Create DataFrame
                    df = pd.DataFrame(data, columns=columns)  # Fixed capitalization of 'DataFrame'
                    st.dataframe(df)
                else:
                    st.error("Go back")

        except pymysql.MySQLError as err:
            st.error(f"Error during database operation: {err}")
        finally:
            close_connection(conn)  # Close the connection

# CRUD section for other table
if selected == "CRUD":
    table_name = "other"
    operation = st.sidebar.selectbox("Select Operation", ["Create", "Read", "Update", "Delete", "Drop Table"])

    conn = connect_to_tidb()
    if conn:
        try:
            with conn.cursor() as c:  # Use 'with' for cursor management
                # Ensure the other table exists
                c.execute('''
                    CREATE TABLE IF NOT EXISTS other (
                        other_id INTEGER PRIMARY KEY,
                        owner_name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        phone TEXT NOT NULL
                    )
                ''')
                conn.commit()

                # Streamlit UI for selected table's CRUD operations
                st.title(f"CRUD Operations for {table_name}")

                # Create operation
                if operation == "Create":
                    st.header("Create New Entry")
                    with st.form(key='create_other_form'):
                        other_id = st.number_input("Other ID", min_value=1)
                        owner_name = st.text_input("Owner Name")
                        email = st.text_input("Email")
                        phone = st.text_input("Phone")
                        submit_button = st.form_submit_button(label='Add Entry')

                        if submit_button:
                            c.execute('SELECT * FROM other WHERE other_id = %s', (other_id,))
                            existing_entry = c.fetchone()
                            if existing_entry:
                                st.error("Entry with this ID already exists.")
                            else:
                                c.execute('INSERT INTO other (other_id, owner_name, email, phone) VALUES (%s, %s, %s, %s)',
                                          (other_id, owner_name, email, phone))
                                conn.commit()
                                st.success("Entry added successfully!")

                # Read operation
                elif operation == "Read":
                    st.header("Existing Entries")
                    c.execute('SELECT * FROM other')
                    result = c.fetchall()
                    df = pd.DataFrame(result, columns=["Other ID", "Owner Name", "Email", "Phone"])  # Fixed capitalization
                    st.dataframe(df)

                # Update operation
                elif operation == "Update":
                    st.header("Update Entry")
                    c.execute('SELECT * FROM other')
                    entries = c.fetchall()
                    entry_to_update = st.selectbox("Select Entry to Update", [row[0] for row in entries])
                    c.execute('SELECT * FROM other WHERE other_id = %s', (entry_to_update,))
                    existing_data = c.fetchone()  # This should be separate now

                    if existing_data:
                        new_owner_name = st.text_input("New Owner Name", value=existing_data[1])
                        new_email = st.text_input("New Email", value=existing_data[2])
                        new_phone = st.text_input("New Phone", value=existing_data[3])
                        update_button = st.button("Update Entry")

                        if update_button:
                            c.execute('UPDATE other SET owner_name = %s, email = %s, phone = %s WHERE other_id = %s',
                                      (new_owner_name, new_email, new_phone, entry_to_update))
                            conn.commit()
                            st.success("Entry updated successfully!")

                # Delete operation
                elif operation == "Delete":
                    st.header("Delete Entry")
                    c.execute('SELECT * FROM other')
                    entries = c.fetchall()
                    entry_to_delete = st.selectbox("Select Entry to Delete", [row[0] for row in entries])
                    delete_button = st.button("Delete Entry")

                    if delete_button:
                        c.execute('DELETE FROM other WHERE other_id = %s', (entry_to_delete,))
                        conn.commit()
                        st.success("Entry deleted successfully!")

                # Drop table operation
                elif operation == "Drop Table":
                    drop_button = st.button(label='Drop Other Table')
                    if drop_button:
                        c.execute('DROP TABLE IF EXISTS other')
                        conn.commit()
                        st.success("Other table dropped successfully.")

        except pymysql.MySQLError as err:
            st.error(f"Error during CRUD operation: {err}")
        finally:
            close_connection(conn)  # Close the connection