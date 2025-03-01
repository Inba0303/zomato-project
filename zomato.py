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
            user="CX5EJS1zx2L6stA.root",
            password="FERptSw6pN5p9Oda",
            database="first",
            ssl_ca="c:/users/inbak/downloads/isrgrootx1.pem"
        )
        return conn
    except pymysql.err.OperationalError as e:
        st.error(f"Database connection error: {e}")
        return None

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
    unsafe_allow_html=True
)

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Zomato Data View",
        options=["home", "main", "crud", "queries"],
        icons=["house", "book-fill", "pencil", "floppy"],
        default_index=0
    )
selected_query = None
# Display image if 'home' is selected
if selected == "home":
    st.image(r"c:\users\inbak\onedrive\zomato\zomato-marketing-strategy-–-a-case-study-2023-1.webp")
else:
    st.write(f"Showing data for: {selected}")

# Sidebar for table selection if "main" is selected
if selected == "main":
    table_options = ["customers_table", "restaurants_table", "orders_table", "deliveries_table", "delivery_persons_table", "None"]
    selected_table = st.sidebar.selectbox("Select table", table_options)

    # Connect to the database
    conn = connect_to_tidb()
    if conn:
        try:
            with conn.cursor() as cur:
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
                    query = f"SELECT * FROM {table_name}"
                    cur.execute(query)
                    data = cur.fetchall()
                    columns = [col[0] for col in cur.description]

                    # Create and store the DataFrame in session state
                    if selected_table == "customers_table":
                        st.session_state.customers = pd.DataFrame(data, columns=columns)
                    elif selected_table == "restaurants_table":
                        st.session_state.restaurants = pd.DataFrame(data, columns=columns)

                    # Display the DataFrame
                    df = pd.DataFrame(data, columns=columns)
                    st.dataframe(df)
                else:
                    st.error("GO BACK")

        except pymysql.err.OperationalError as err:
            st.error(f"Error during database operation: {err}")
        finally:
            close_connection(conn)

         

# CRUD section for other table
if selected == "crud":
    table_name = "other"
    operation = st.sidebar.selectbox("Select operation", ["create", "read", "update", "delete", "drop table"])

    conn = connect_to_tidb()
    if conn:
        try:
            with conn.cursor() as c:  # Use 'with' for cursor management
                # Ensure the 'other' table exists
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
                if operation == "create":
                    st.header("Create new entry")
                    with st.form(key='create_other_form'):
                        other_id = st.number_input("Other ID", min_value=1)
                        owner_name = st.text_input("Owner name")
                        email = st.text_input("Email")
                        phone = st.text_input("Phone")
                        submit_button = st.form_submit_button(label='Add entry')

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
                elif operation == "read":
                    st.header("Existing entries")
                    c.execute('SELECT * FROM other')
                    result = c.fetchall()
                    df = pd.DataFrame(result, columns=["Other ID", "Owner Name", "Email", "Phone"])  # Fixed capitalization
                    st.dataframe(df)

                # Update operation
                elif operation == "update":
                    st.header("Update entry")
                    c.execute('SELECT * FROM other')
                    entries = c.fetchall()
                    entry_to_update = st.selectbox("Select entry to update", [row[0] for row in entries])
                    c.execute('SELECT * FROM other WHERE other_id = %s', (entry_to_update,))
                    existing_data = c.fetchone()  # Fetching existing data

                    if existing_data:
                        new_owner_name = st.text_input("New owner name", value=existing_data[1])
                        new_email = st.text_input("New email", value=existing_data[2])
                        new_phone = st.text_input("New phone", value=existing_data[3])
                        update_button = st.button("Update entry")

                        if update_button:
                            c.execute('UPDATE other SET owner_name = %s, email = %s, phone = %s WHERE other_id = %s',
                                      (new_owner_name, new_email, new_phone, entry_to_update))
                            conn.commit()
                            st.success("Entry updated successfully!")

                # Delete operation
                elif operation == "delete":
                    st.header("Delete entry")
                    c.execute('SELECT * FROM other')
                    entries = c.fetchall()
                    entry_to_delete = st.selectbox("Select entry to delete", [row[0] for row in entries])
                    delete_button = st.button("Delete entry")

                    if delete_button:
                        c.execute('DELETE FROM other WHERE other_id = %s', (entry_to_delete,))
                        conn.commit()
                        st.success("Entry deleted successfully!")

                # Drop table operation
                elif operation == "drop table":
                    drop_button = st.button(label='Drop other table')
                    if drop_button:
                        c.execute('DROP TABLE IF EXISTS other')
                        conn.commit()
                        st.success("Other table dropped successfully.")

        except pymysql.err.OperationalError as err:  # Corrected
            st.error(f"Error during CRUD operation: {err}")
        finally:
            close_connection(conn)  # Close the connection
            
            
            

# Initialize session state for customers, restaurants, etc.
if 'customers' not in st.session_state:
    st.session_state.customers = pd.DataFrame()  # Corrected
if 'restaurants' not in st.session_state:
    st.session_state.restaurants = pd.DataFrame()  # Corrected
if 'orders' not in st.session_state:
    st.session_state.orders = pd.DataFrame()  # Corrected
if 'deliveries' not in st.session_state:
    st.session_state.deliveries = pd.DataFrame()  # Corrected
if 'delivery_persons' not in st.session_state:
    st.session_state.delivery_persons = pd.DataFrame()  # Corrected

# Queries section
if selected == "queries":
    selected_queries = ["query 1", "query 2", "query 3", "query 4", "query 5", 
                        "query 6", "query 7", "query 8", "query 9", "query 10",
                        "query 11", "query 12", "query 13", "query 14", 
                        "query 15", "query 16", "query 17", "query 18", 
                        "query 19", "query 20"]
    selected_query = st.selectbox("Select a query", selected_queries)
if selected_query:
    if selected_query == "query 1":
        st.markdown("<h2>Find the total number of customers</h2>", unsafe_allow_html=True)
        st.markdown("<h4>query:</h4>", unsafe_allow_html=True)
        st.write("SELECT COUNT(customer_id) FROM customers;")

        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(customer_id) FROM customers;")
                    res = cur.fetchall()
                    st.markdown("<h3>output:</h3>", unsafe_allow_html=True)
                    st.write(f"Total number of customers: {res[0][0] if res else 0}")
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)

    elif selected_query == "query 2":
        st.markdown("<h2>The top customers based on order frequency</h2>", unsafe_allow_html=True)
        st.markdown("<h4>query:</h4>", unsafe_allow_html=True)
        st.write("""
        SELECT customer_id, COUNT(order_id) AS order_count 
        FROM orders 
        GROUP BY customer_id 
        ORDER BY order_count DESC 
        LIMIT 6;
        """)

        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                    SELECT customer_id, COUNT(order_id) AS order_count 
                    FROM orders 
                    GROUP BY customer_id 
                    ORDER BY order_count DESC 
                    LIMIT 6;
                    """)
                    res = cur.fetchall()
                    st.markdown("<h3>output:</h3>", unsafe_allow_html=True)
                    columns = [desc[0] for desc in cur.description]
                    df = pd.DataFrame(res, columns=columns)
                    st.dataframe(df)
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)

    # Repeat similar structure for other queries

    elif selected_query == "query 12":
        st.markdown("<h2>Find the total number of restaurants</h2>", unsafe_allow_html=True)
        st.markdown("<h4>query:</h4>", unsafe_allow_html=True)
        st.write("SELECT COUNT(restaurant_id) FROM restaurants;")

        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(restaurant_id) FROM restaurants;")
                    res = cur.fetchall()
                    st.markdown("<h3>output:</h3>", unsafe_allow_html=True)
                    total_restaurants = res[0][0] if res else 0
                    st.write(f"Total number of restaurants: {total_restaurants}")
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                close_connection(conn)

# Continue for remaining queries...

# Handling query 3 (average rating by delivery persons)
    elif selected_query == "query 3":
       st.markdown("<h2>Get the average rating given by delivery persons</h2>", unsafe_allow_html=True)
       st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
       st.write("SELECT AVG(average_rating) AS average FROM delivery_persons;")

    # Connect to the database to execute the average rating query
       conn = connect_to_tidb()
       if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT AVG(average_rating) AS average FROM delivery_persons;")
                    res = cur.fetchall()

                # Check for results
                if res and res[0][0] is not None:  # Changed to None
                    st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                    st.write("Average rating given by delivery persons is:", res[0][0])
                else:
                    st.write("No ratings available for delivery persons.")

            except pymysql.err.ProgrammingError as e:
               if e.args[0] == 1146:  # Error code for "table doesn't exist"
                st.error("The table 'delivery_persons' does not exist in the database.")
               else:
                st.error(f"An unexpected error occurred: {e}")
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)

# Handling query 4 (find the most preferred cuisine type among customers)
    elif selected_query == "query 4":
        st.markdown("<h2>Find the most preferred cuisine type among customers</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("""SELECT preferred_cuisine, COUNT(*) AS cuisine_count 
                 FROM customers 
                 GROUP BY preferred_cuisine 
                 ORDER BY cuisine_count DESC 
                 LIMIT 5;""")

    # Connect to the database to retrieve preferred cuisine data
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                     cur.execute("""
                    SELECT preferred_cuisine, COUNT(*) AS cuisine_count 
                    FROM customers 
                    GROUP BY preferred_cuisine 
                    ORDER BY cuisine_count DESC 
                    LIMIT 5;
                """)
                res = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            except pymysql.err.ProgrammingError as e:
                st.error(f"An unexpected SQL error occurred: {e}")
            finally:
                close_connection(conn)

# Handling query 5 (retrieve the number of premium vs non-premium customers)
    elif selected_query == "query 5":
        st.markdown("<h2>Retrieve the number of premium vs non-premium customers</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("""SELECT 
                     (SELECT COUNT(customer_id) FROM customers WHERE is_premium = TRUE) AS premium_customer,
                     (SELECT COUNT(customer_id) FROM customers WHERE is_premium = FALSE) AS non_premium_customer;""")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                    SELECT 
                        (SELECT COUNT(customer_id) FROM customers WHERE is_premium = TRUE) AS premium_customer,
                        (SELECT COUNT(customer_id) FROM customers WHERE is_premium = FALSE) AS non_premium_customer;
                """)
                res = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            except pymysql.err.ProgrammingError as e:
                st.error(f"An unexpected SQL error occurred: {e}")
            finally:
                close_connection(conn)

# Handling query 6 (find the total number of orders placed)
    elif selected_query == "query 6":
        st.markdown("<h2>Find the total number of orders placed</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("SELECT COUNT(order_id) AS order_count FROM orders;")

    # Connect to the database to execute the order count query
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(order_id) AS order_count FROM orders;")
                res = cur.fetchall()
                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                st.write(f"Total number of orders: {res[0][0] if res else 0}")
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)

# Handling query 7 (get the count of orders by status)
    elif selected_query == "query 7":
        st.markdown("<h2>Get the count of orders by status (pending, delivered, canceled)</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("SELECT status, COUNT(*) AS status_count FROM orders GROUP BY status;")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
               with conn.cursor() as cur:
                cur.execute("SELECT status, COUNT(*) AS status_count FROM orders GROUP BY status;")
                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                # Creating a DataFrame from the result
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)  # Display the DataFrame
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)

# Handling query 8 (find the average order value)
    elif selected_query == "query 8":
        st.markdown("<h2>Find the average order value</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("SELECT ROUND(AVG(total_amount), 2) AS avg_order_value FROM orders;")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                   cur.execute("SELECT ROUND(AVG(total_amount), 2) AS avg_order_value FROM orders;")
                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                # Display the average order value
                st.write(f"Average order value is: {res[0][0] if res else 0}")

            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)

# Handling query 9 (get the count of orders by payment mode)
    elif selected_query == "query 9":
        st.markdown("<h2>Get the count of orders by payment mode (cash, credit card, UPI)</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("SELECT payment_mode, COUNT(*) AS payment_mode_count FROM orders GROUP BY payment_mode;")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
               with conn.cursor() as cur:
                cur.execute("SELECT payment_mode, COUNT(*) AS payment_mode_count FROM orders GROUP BY payment_mode;")
                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                # Creating a DataFrame from the result
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)  # Display the DataFrame
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)

# Handling query 10 (identify peak ordering times)
    elif selected_query == "query 10":
        st.markdown("<h2>Find the top 5 most expensive orders</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("SELECT order_id, ROUND(total_amount, 2) AS total_amount FROM orders ORDER BY total_amount DESC LIMIT 5")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                  cur.execute("SELECT order_id, ROUND(total_amount, 2) AS total_amount FROM orders ORDER BY total_amount DESC LIMIT 5")
                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                # Creating a DataFrame from the result
                columns = [desc[0] for desc in cur.description]  # Fetch column names
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)  # Display the DataFrame
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)

    elif selected_query == "query 11":
        st.markdown("<h2>Find customers who spent more than Rs. 50</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("""
        SELECT 
            c.name AS customer_name, 
            r.name AS restaurant_name, 
            o.total_amount AS amount 
        FROM customers c 
        JOIN orders o ON c.customer_id = o.customer_id 
        JOIN restaurants r ON o.restaurant_id = r.restaurant_id  
        WHERE o.total_amount > 50
    """)

    # Connect to the database to retrieve data
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""
                    SELECT 
                        c.name AS customer_name, 
                        r.name AS restaurant_name, 
                        o.total_amount AS amount 
                    FROM customers c 
                    JOIN orders o ON c.customer_id = o.customer_id 
                    JOIN restaurants r ON o.restaurant_id = r.restaurant_id 
                    WHERE o.total_amount > 50
                    LIMIT 10;
                """)
                res = cur.fetchall()
                columns = [j[0] for j in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            except pymysql.err.ProgrammingError as e:
                st.error(f"An unexpected SQL error occurred: {e}")
            finally:
                close_connection(conn)

    elif selected_query == "query 12":
        st.markdown("<h2>Find the total number of restaurants</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("SELECT COUNT(restaurant_id) FROM restaurants;")

    # Connect to the database to execute the count query
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(restaurant_id) FROM restaurants;")
                res = cur.fetchall()

                # Output the result
                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                total_restaurants = res[0][0] if res else 0  # Handle empty results case
                st.write(f"Total number of restaurants: {total_restaurants}")
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                close_connection(conn)

    elif selected_query == "query 13":
        st.markdown("<h2>Find the total number of orders across all restaurants</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("SELECT SUM(total_orders) FROM restaurants;")

    # Connect to the database to execute the sum query
        conn = connect_to_tidb()
        if conn:
            try:
               with conn.cursor() as cur:
                cur.execute("SELECT SUM(total_orders) FROM restaurants;")
                res = cur.fetchall()

                # Output the result
                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                total_orders = res[0][0] if res and res[0][0] is not None else 0  # Handle empty results case
                st.write(f"Total number of orders: {total_orders}")
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                close_connection(conn)

    elif selected_query == "query 14":
        st.markdown("<h2>Get the count of delivery status (delivered, on the way)</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("SELECT delivery_status, COUNT(*) AS status_count FROM deliveries GROUP BY delivery_status;")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
               with conn.cursor() as cur:
                cur.execute("SELECT delivery_status, COUNT(*) AS status_count FROM deliveries GROUP BY delivery_status;")
                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                # Creating a DataFrame from the result
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)  # Display the DataFrame
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)

    elif selected_query == "query 15":
        st.markdown("<h2>Get the count of vehicle type (car, bike)</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("SELECT vehicle_type, COUNT(*) AS vehicle_type_count FROM deliveries GROUP BY vehicle_type;")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
               with conn.cursor() as cur:
                cur.execute("SELECT vehicle_type, COUNT(*) AS vehicle_type_count FROM deliveries GROUP BY vehicle_type;")
                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                # Creating a DataFrame from the result
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)  # Display the DataFrame
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)
               
    elif selected_query == "query 16":
        st.markdown("<h2>Find the percentage of active vs. inactive restaurants</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("""SELECT is_active, 
                 CONCAT(ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM restaurants)), 2), '%') AS percentage
                 FROM restaurants 
                 GROUP BY is_active;""")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""SELECT is_active, 
                                     CONCAT(ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM restaurants)), 2), '%') AS percentage
                                     FROM restaurants 
                                     GROUP BY is_active;""")
                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                # Creating a DataFrame from the result
                columns = [j[0] for j in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)  # Display the DataFrame
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                close_connection(conn)  # Ensure connection is closed       

    elif selected_query == "query 17":
        st.markdown("<h2>Find the top 5 longest deliveries distances</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("""SELECT CONCAT(distance ,' km') AS longest_distance FROM deliveries ORDER BY distance DESC LIMIT 5""")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                   cur.execute("""SELECT CONCAT(distance ,' km') AS longest_distance FROM deliveries ORDER BY distance DESC LIMIT 5""")

                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                # Creating a DataFrame from the result
                columns = [j[0] for j in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)  # Display the DataFrame
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                close_connection(conn)  # Ensure connection is closed

    elif selected_query == "query 18":
        st.markdown("<h2>Find the top 5 delivery persons by average rating</h2>", unsafe_allow_html=True)
        st.markdown("<h4>SQL Query:</h4>", unsafe_allow_html=True)
        st.write("""SELECT CONCAT(average_rating) AS average_rating FROM delivery_persons ORDER BY average_rating DESC LIMIT 5""")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                  cur.execute("""SELECT CONCAT(average_rating) AS average_rating FROM delivery_persons ORDER BY average_rating DESC LIMIT 5""")

                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)

                # Creating a DataFrame from the result
                columns = [j[0] for j in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)  # Display the DataFrame
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                close_connection(conn)  # Ensure connection is closed  

    elif selected_query == "query 19":
        st.markdown("<h2>Find the percentage of active vs. inactive orders (cash, credit card, UPI)</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("""SELECT payment_mode, 
                 CONCAT(ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders)), 2), '%') AS percentage
                 FROM orders
                 GROUP BY payment_mode;""")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("""SELECT payment_mode, 
                                     CONCAT(ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders)), 2), '%') AS percentage
                                     FROM orders 
                                     GROUP BY payment_mode;""")
                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                # Creating a DataFrame from the result
                columns = [j[0] for j in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)  # Display the DataFrame
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
            finally:
                close_connection(conn)  # Ensure connection is closed             

    elif selected_query == "query 20":
        st.markdown("<h2>Get the count of restaurant_id, average_delivery_time</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Query:</h4>", unsafe_allow_html=True)
        st.write("SELECT restaurant_id, average_delivery_time, COUNT(*) AS average_delivery_time_count FROM restaurants GROUP BY restaurant_id;")

    # Connect to the database to execute the query
        conn = connect_to_tidb()
        if conn:
            try:
                with conn.cursor() as cur:
                  cur.execute("SELECT restaurant_id, average_delivery_time, COUNT(*) AS average_delivery_time_count FROM restaurants GROUP BY restaurant_id;")
                res = cur.fetchall()

                st.markdown("<h3>Output:</h3>", unsafe_allow_html=True)
                # Creating a DataFrame from the result
                columns = [desc[0] for desc in cur.description]
                df = pd.DataFrame(res, columns=columns)  # Correct DataFrame creation
                st.dataframe(df)  # Display the DataFrame
            except pymysql.err.OperationalError as err:
                st.error(f"Error during database operation: {err}")
            finally:
                close_connection(conn)  # Ensure connection is closed