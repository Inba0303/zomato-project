
import mysql.connector
import pandas as pd
from faker import Faker
from datetime import timedelta
import random

# Initialize Faker
fake = Faker()

# Database connection
one = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    user="CX5EJS1zx2L6stA.root",
    port=4000,
    password="6V9o8HJadD3ZpqoO",
    database="first"
)

# Define constants
NUM_CUSTOMERS = 100

# Customers Table data generation
customers_table1 = []
customers = []  # Reinitialize customers list
for _ in range(NUM_CUSTOMERS):
    customer_id = _
    name = fake.name()
    email = fake.email()
    # Truncate or modify the phone number to fit the column length
    phone = fake.phone_number()[:20]  # Limit to 20 characters
    location = fake.address()
    signup_date = fake.date_between(start_date='-5y', end_date='today')
    is_premium = random.choice(['normal', 'goald'])
    preferred_cuisine = random.choice(['Indian', 'Chinese', 'Italian', 'Mexican', 'Thai'])
    total_orders = random.randint(1, 50)
    average_rating = round(random.uniform(1, 5), 2)
    customers.append([customer_id, name, email, phone, location, signup_date, is_premium,
                      preferred_cuisine, total_orders, average_rating])

customers_df = pd.DataFrame(customers, columns=['customer_id', 'name', 'email', 'phone',
                                                'location', 'signup_date', 'is_premium',
                                                'preferred_cuisine', 'total_orders', 'average_rating'])

# Create the Customers table
cursor = one.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(20),  -- Adjust the length of the phone column if necessary
    location VARCHAR(255),
    signup_date DATE,
    is_premium ENUM('normal', 'goald'),
    preferred_cuisine VARCHAR(50),
    total_orders INT,
    average_rating FLOAT
)
""")
one.commit()

# Insert data into the Customers table, wrapping in a transaction
try:
    cursor.execute("START TRANSACTION")  # Start a transaction
    for index, row in customers_df.iterrows():
        sql = "INSERT INTO Customers (customer_id, name, email, phone, location, signup_date, is_premium, preferred_cuisine, total_orders, average_rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (row['customer_id'], row['name'], row['email'], row['phone'], row['location'], row['signup_date'], row['is_premium'], row['preferred_cuisine'], row['total_orders'], row['average_rating'])
        cursor.execute(sql, val)
    cursor.execute("COMMIT")  # Commit the transaction
    print("Data inserted into Customers table successfully.")
except mysql.connector.Error as err:
    cursor.execute("ROLLBACK")  # Rollback if any error occurs
    print(f"Error: {err}")
finally:
    cursor.close()  # Close the cursor in the finally block
    one.close()  # Close the connection in the finally block
    
    
    
import mysql.connector
import pandas as pd
from faker import Faker
from datetime import timedelta
import random

# Initialize Faker
fake = Faker()

# Database connection
two = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    user="CX5EJS1zx2L6stA.root",
    port=4000,
    password="6V9o8HJadD3ZpqoO",
    database="first"
)

NUM_RESTAURANTS = 100
restaurants_table1 = []
for _ in range(NUM_RESTAURANTS):
    restaurant_id = _
    name = fake.company() + " Restaurant"
    cuisine_type = random.choice(['Indian', 'Chinese', 'Italian', 'Mexican', 'Thai'])
    location = fake.address()
    owner_name = fake.name()
    average_delivery_time = random.randint(20, 60)
    # Limit contact_number to 20 characters
    contact_number = fake.phone_number()[:20]
    rating = round(random.uniform(1, 5), 2)
    total_orders = random.randint(1, 100)
    is_active = random.choice([True, False])
    restaurants.append([restaurant_id, name, cuisine_type, location, owner_name,
                        average_delivery_time, contact_number, rating, total_orders, is_active])

restaurants_df = pd.DataFrame(restaurants, columns=['restaurant_id', 'name', 'cuisine_type',
                                                    'location', 'owner_name', 'average_delivery_time',
                                                    'contact_number', 'rating', 'total_orders', 'is_active'])

# Create the Restaurants table
cursor = two.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS Restaurants (
    restaurant_id INT PRIMARY KEY,
    name VARCHAR(255),
    cuisine_type VARCHAR(50),
    location VARCHAR(255),
    owner_name VARCHAR(255),
    average_delivery_time INT,
    contact_number VARCHAR(20),  -- Adjust length if needed
    rating FLOAT,
    total_orders INT,
    is_active BOOLEAN
)
""")
two.commit()

# Insert data into the Restaurants table, using a transaction
try:
    cursor.execute("START TRANSACTION")
    for index, row in restaurants_df.iterrows():
        sql = "INSERT INTO Restaurants (restaurant_id, name, cuisine_type, location, owner_name, average_delivery_time, contact_number, rating, total_orders, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (row['restaurant_id'], row['name'], row['cuisine_type'], row['location'], row['owner_name'], row['average_delivery_time'], row['contact_number'], row['rating'], row['total_orders'], row['is_active'])
        cursor.execute(sql, val)
    cursor.execute("COMMIT")
    print("Data inserted into Restaurants table successfully.")
except mysql.connector.Error as err:
    cursor.execute("ROLLBACK")
    print(f"Error: {err}")
finally:
    cursor.close()
    two.close()    
    
    
    

import mysql.connector
import pandas as pd
from faker import Faker
from datetime import timedelta
import random

# Initialize Faker
fake = Faker()

# Database connection
three = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    user="CX5EJS1zx2L6stA.root",
    port=4000,
    password="6V9o8HJadD3ZpqoO",
    database="first"
)
 # Adjust this if needed
NUM_ORDERS = 100
orders_table1 = []
orders = [] # Initialize 'orders' list before using it


for _ in range(NUM_ORDERS):
    order_id = _
    # Ensure customer_id and restaurant_id are within valid ranges
    customer_id = random.randint(0, NUM_CUSTOMERS - 1)
    restaurant_id = random.randint(0, NUM_RESTAURANTS - 1)
    order_date = fake.date_time_between(start_date='-1y', end_date='now')
    delivery_time = order_date + timedelta(minutes=random.randint(20, 60))
    status = random.choice(['pending', 'delivered', 'cancelled'])
    total_amount = round(random.uniform(10, 100), 2)
    payment_mode = random.choice(['credit card', 'cash', 'upi'])
    discount_applied = round(random.uniform(0, 20), 2)
    feedback_rating = round(random.uniform(1, 5), 2)
    # Convert datetime objects to strings before appending
    orders.append([order_id, customer_id, restaurant_id, order_date.strftime('%Y-%m-%d %H:%M:%S'), delivery_time.strftime('%Y-%m-%d %H:%M:%S'),
                   status, total_amount, payment_mode, discount_applied, feedback_rating])

orders_df = pd.DataFrame(orders, columns=['order_id', 'customer_id', 'restaurant_id', 'order_date',
                                           'delivery_time', 'status', 'total_amount', 'payment_mode',
                                           'discount_applied', 'feedback_rating'])

# Create the 'orders' table if it doesn't exist
cursor = three.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    restaurant_id INT,
    order_date DATETIME,
    delivery_time DATETIME,
    status VARCHAR(255),
    total_amount FLOAT,
    payment_mode VARCHAR(255),
    discount_applied FLOAT,
    feedback_rating FLOAT
)
""")
three.commit()

# Now insert data into the 'orders' table, handling potential duplicate entries
# and null values with 'ON DUPLICATE KEY UPDATE'
try:
    for index, row in orders_df.iterrows():
        sql = """
        INSERT INTO orders (order_id, customer_id, restaurant_id, order_date, delivery_time, status, total_amount, payment_mode, discount_applied, feedback_rating)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            customer_id = VALUES(customer_id),
            restaurant_id = VALUES(restaurant_id),
            order_date = VALUES(order_date),
            delivery_time = VALUES(delivery_time),
            status = VALUES(status),
            total_amount = VALUES(total_amount),
            payment_mode = VALUES(payment_mode),
            discount_applied = VALUES(discount_applied),
            feedback_rating = VALUES(feedback_rating)
        """
        val = (row['order_id'], row['customer_id'], row['restaurant_id'], row['order_date'], row['delivery_time'], row['status'], row['total_amount'], row['payment_mode'], row['discount_applied'], row['feedback_rating'])

        cursor.execute(sql, val)
        three.commit() # Commit after each successful insertion

    print(cursor.rowcount, "record inserted.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
    three.rollback() # Rollback in case of any error during insertion
finally:
    cursor.close()
    three.close()    
        
        
        
 
import mysql.connector
import pandas as pd
from faker import Faker
from datetime import timedelta
import random

# Initialize Faker
fake = Faker()

# Database connection
four = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    user="CX5EJS1zx2L6stA.root",
    port=4000,
    password="6V9o8HJadD3ZpqoO",
    database="first"
)



# Generate orders data
#Removed the unexpected indent from the next line
Deliveries_table = []
# Define Deliveries - Assuming NUM_CUSTOMERS, NUM_RESTAURANTS, NUM_DELIVERY_PERSONS are defined somewhere
# If not, please define them appropriately
NUM_Deliveries = 100
NUM_CUSTOMERS = 100 # Replace with your actual number of customers
NUM_RESTAURANTS = 100 # Replace with your actual number of restaurants
NUM_DELIVERY_PERSONS = 50 # Replace with your actual number of delivery persons
orders = []  # Initialize 'orders' list before using it
for _ in range(NUM_Deliveries):
    order_id = _
    customer_id = random.randint(0, NUM_CUSTOMERS - 1)
    restaurant_id = random.randint(0, NUM_RESTAURANTS - 1)
    order_date = fake.date_time_between(start_date='-1y', end_date='now')
    delivery_time = order_date + timedelta(minutes=random.randint(20, 60))
    status = random.choice(['pending', 'delivered', 'cancelled'])
    total_amount = round(random.uniform(10, 100), 2)
    payment_mode = random.choice(['credit card', 'cash', 'upi'])
    discount_applied = round(random.uniform(0, 20), 2)
    feedback_rating = round(random.uniform(1, 5), 2)
    orders.append([order_id, customer_id, restaurant_id, order_date.strftime('%Y-%m-%d %H:%M:%S'), delivery_time.strftime('%Y-%m-%d %H:%M:%S'),
                   status, total_amount, payment_mode, discount_applied, feedback_rating])


# ... (rest of your code) ...

# Deliveries Table
deliveries_table1 = []
deliveries = []  # Initialize deliveries list
delivery_id_counter = 0  # Initialize a counter for delivery_id

for order in orders:
    #delivery_id = order[0]  # Assuming order_id is the first element in the order list
    #order_id = order[0]
    delivery_id = delivery_id_counter  # Use the counter for delivery_id
    delivery_id_counter += 1  # Increment the counter for the next delivery
    order_id = order[0]
    delivery_person_id = random.randint(0, NUM_DELIVERY_PERSONS - 1)
    delivery_status = random.choice(['on the way', 'delivered'])
    distance = round(random.uniform(1, 10), 2)
    delivery_time = random.randint(10, 60)
    estimated_time = delivery_time + random.randint(5, 15)
    delivery_fee = round(random.uniform(2, 10), 2)
    vehicle_type = random.choice(['bike', 'car'])
    deliveries.append([delivery_id, order_id, delivery_person_id, delivery_status, distance,
                       delivery_time, estimated_time, delivery_fee, vehicle_type])

deliveries_df = pd.DataFrame(deliveries, columns=['delivery_id', 'order_id', 'delivery_person_id', 'delivery_status', 'distance',
                                               'delivery_time', 'estimated_time', 'delivery_fee', 'vehicle_type'])
# ... (rest of your code) ...

# Create the 'Deliveries' table if it doesn't exist
cursor = four.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS Deliveries (
    delivery_id INT PRIMARY KEY,
    order_id INT,
    delivery_person_id INT,
    delivery_status VARCHAR(255),
    distance FLOAT,
    delivery_time INT,
    estimated_time INT,
    delivery_fee FLOAT,
    vehicle_type VARCHAR(255)
)
""")
four.commit()

# Insert data into the Deliveries table, using a transaction and handling potential duplicate entries
try:
    cursor.execute("START TRANSACTION")  # Start a transaction for atomicity
    for index, row in deliveries_df.iterrows():
        sql = """
        INSERT INTO Deliveries (delivery_id, order_id, delivery_person_id, delivery_status, distance, delivery_time, estimated_time, delivery_fee, vehicle_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE  -- Handle duplicate entries
            order_id = VALUES(order_id),
            delivery_person_id = VALUES(delivery_person_id),
            delivery_status = VALUES(delivery_status),
            distance = VALUES(distance),
            delivery_time = VALUES(delivery_time),
            estimated_time = VALUES(estimated_time),
            delivery_fee = VALUES(delivery_fee),
            vehicle_type = VALUES(vehicle_type)
        """
        val = (row['delivery_id'], row['order_id'], row['delivery_person_id'], row['delivery_status'], row['distance'], row['delivery_time'], row['estimated_time'], row['delivery_fee'], row['vehicle_type'])
        cursor.execute(sql, val)
    cursor.execute("COMMIT")  # Commit the transaction if all insertions are successful
    print("Data inserted into Deliveries table successfully.")
except mysql.connector.Error as err:
    cursor.execute("ROLLBACK")  # Rollback the transaction if any error occurs
    print(f"Error: {err}")
finally:
    cursor.close()
    four.close()      
    
    
    
    

import mysql.connector
import pandas as pd
from faker import Faker
from datetime import timedelta
import random

# Initialize Faker
fake = Faker()

# Database connection
six= mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    user="CX5EJS1zx2L6stA.root",
    port=4000,
    password="uPyy7r4KDtQauj9b",
    database="first"
)

NUM_DELIVERY_PERSONS = 100

# Delivery Persons Table
delivery_persons_table1 = []
delivery_persons = []  # Initialize delivery_persons list

for _ in range(NUM_DELIVERY_PERSONS):
    delivery_person_id = _
    name = fake.name()
    # Generate contact number and truncate if necessary
    contact_number = fake.phone_number()[:20]  # Truncate to 20 characters
    vehicle_type = random.choice(['bike', 'car']) if random.random() < 0.9 else None
    total_deliveries = random.randint(10, 100)
    average_rating = round(random.uniform(1, 5), 2)
    location = fake.address() if random.random() < 0.7 else None
    delivery_persons.append([delivery_person_id, name, contact_number, vehicle_type,
                              total_deliveries, average_rating, location])

delivery_persons_df = pd.DataFrame(delivery_persons, columns=['delivery_person_id', 'name',
                                                              'contact_number', 'vehicle_type',
                                                              'total_deliveries', 'average_rating',
                                                              'location'])

# Create the Delivery_Persons table
cursor = five.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS Delivery_Persons (
    delivery_person_id INT PRIMARY KEY,
    name VARCHAR(255),
    contact_number VARCHAR(20),
    vehicle_type VARCHAR(50),
    total_deliveries INT,
    average_rating FLOAT,
    location VARCHAR(255)
)
""")
five.commit()  # Commit the table creation

# Insert data into the Delivery_Persons table, handling duplicate entries
insert_query = """
INSERT INTO Delivery_Persons (delivery_person_id, name, contact_number, vehicle_type, total_deliveries, average_rating, location)
VALUES (%s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE  -- Handle duplicate entries
    name = VALUES(name),
    contact_number = VALUES(contact_number),
    vehicle_type = VALUES(vehicle_type),
    total_deliveries = VALUES(total_deliveries),
    average_rating = VALUES(average_rating),
    location = VALUES(location)
"""
# Pass both the insert_query and delivery_persons to executemany
cursor.executemany(insert_query, delivery_persons)
five.commit()

# Close the cursor and connection
cursor.close()
five.close()    