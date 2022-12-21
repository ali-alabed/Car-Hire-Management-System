import mysql.connector

user_name = 'root'
password = 'rootroot'
host = '127.0.0.1'
db_name = 'CAR_RENTAL'


def create_db():
    # establishing the connection
    conn = mysql.connector.connect(user=user_name, password=password, host=host)
    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    # Preparing query to create a database
    sql = "CREATE database CAR_RENTAL"
    # Creating a database
    cursor.execute(sql)
    cursor.execute("SHOW DATABASES")
    # Closing the connection
    conn.close()


# function that creates a table in the database using a list as its columns
def create_table(table_name, columns):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "CREATE TABLE " + table_name + " ("
    for i in columns:
        sql += i + " VARCHAR(255), "
    sql = sql[:-2]
    sql += ")"
    cursor.execute(sql)
    conn.commit()
    conn.close()


# function add new column to existing table in the database and fill it with a default value, and the type of the
# column is given
def add_column(table_name, column_name, default_value, type):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "ALTER TABLE " + table_name + " ADD " + column_name + " " + type + " DEFAULT '" + default_value + "'"
    cursor.execute(sql)
    conn.commit()
    conn.close()


# function that inserts a row in the database and returns the row as a dictionary using a list of all columns as keys
def insert_and_get(table_name, columns, values):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "INSERT INTO " + table_name + " ("
    for i in columns:
        sql += i + ", "
    sql = sql[:-2]
    sql += ") VALUES ("
    for i in values:
        sql += "'" + str(i) + "', "
    sql = sql[:-2]
    sql += ")"
    cursor.execute(sql)
    conn.commit()
    sql = "SELECT * FROM " + table_name + " WHERE id = " + str(cursor.lastrowid)
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    return get_row_by_column(table_name, "id", result[0][0])


def return_as_class_object(table_name, result):
    if type(result) == list:
        result = result[0]
    if table_name == "Cars":
        return Cars([i for i in result])
    elif table_name == "Booking":
        return Booking([i for i in result])


def return_as_list_class_object(table_name, result):
    to_return = []
    for item in result:
        to_return.append(return_as_class_object(table_name, item))
    return to_return


# function returns all row as a dictionary of "columns and its values",  order by column
def get_all_row_order_by_dict(table_name, column):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name + " ORDER BY " + column
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return []
    else:
        return return_as_list_class_object(table_name, result)


# function returns a rows using list of column and list of value
def get_row_by_column_list(table_name, column, value):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name + " WHERE "
    for i in range(len(column)):
        sql += column[i] + " = '" + str(value[i]) + "' AND "
    sql = sql[:-5]
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return []
    elif len(result) > 1:
        return return_as_list_class_object(table_name, result)
    else:
        return return_as_class_object(table_name, result)




# function returns a row using a column and a value
def get_row_by_column(table_name, column, value):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name + " WHERE " + column + " = '" + str(value) + "'"
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return []
    elif len(result) > 1:
        return return_as_list_class_object(table_name, result)
    else:
        return return_as_class_object(table_name, result)


# function returns all row as a dictionary of "columns and its values",  order by column
def get_all_row_order_by_dict_by_desc(table_name, column):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name + " ORDER BY " + column + " DESC"
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return []
    else:
        return return_as_list_class_object(table_name, result)


# function search for all rows that contains a value that is in a range of two values
def get_row_by_column_between(table_name, column, value1, value2):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name + " WHERE " + column + " BETWEEN '" + str(value1) + "' AND '" + str(
        value2) + "'"
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return []
    else:
        return return_as_list_class_object(table_name, result)


# function search for all rows that contains a value in all columns
def get_row_by_all_column(table_name, value):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    all_column = get_columns(table_name)
    sql = "SELECT * FROM " + table_name + " WHERE "  # + all_column[0] + " = '" + str(value) + "'"
    for col in all_column:
        sql += col + " LIKE '%" + str(value) + "%'" + " OR "
    sql = sql[:-3]
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
        return []
    elif len(result) > 1:
        return return_as_list_class_object(table_name, result)
    else:
        return return_as_class_object(table_name, result)


# function search for all rows that contains a date value that is in a range of two date values
def get_row_by_column_between_date(table_name, column, value1, value2):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name + " WHERE " + column + " BETWEEN '" + str(value1) + "' AND '" + str(
        value2) + "'"
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return []
    else:
        return return_as_list_class_object(table_name, result)


# function that creates a table in the database using a list as its columns and its types
def create_table_with_type(table_name, columns, types):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "CREATE TABLE " + table_name + " ("
    for i in range(len(columns)):
        sql += columns[i] + " " + types[i] + ", "
    sql = sql[:-2]
    sql += ")"
    cursor.execute(sql)
    conn.commit()
    conn.close()


# function that inserts a row in the database
def insert(table_name, columns, values):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "INSERT INTO " + table_name + " ("
    for i in columns:
        sql += i + ", "
    sql = sql[:-2]
    sql += ") VALUES ("
    for i in values:
        sql += "'" + str(i) + "', "
    sql = sql[:-2]
    sql += ")"
    cursor.execute(sql)
    conn.commit()
    conn.close()


# start update the table rows

# function that updates a row in the database
def update(table_name, columns, values, id):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "UPDATE " + table_name + " SET "
    for i in range(len(columns)):
        sql += columns[i] + " = '" + str(values[i]) + "', "
    sql = sql[:-2]
    sql += " WHERE id = " + str(id)
    cursor.execute(sql)
    conn.commit()
    conn.close()


# function updates a row in the database using a column and a value
def update_by_column(table_name, columns, values, column, value):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "UPDATE " + table_name + " SET "
    for i in range(len(columns)):
        sql += columns[i] + " = '" + values[i] + "', "
    sql = sql[:-2]
    sql += " WHERE " + column + " = '" + str(value) + "'"
    cursor.execute(sql)
    conn.commit()
    conn.close()


# function updates a single value in a row in the database using a column and a value to find the row
def update_single_value_by_column(table_name, column, value, column2, value2):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "UPDATE " + table_name + " SET " + column + " = '" + str(value) + "' WHERE " + column2 + " = '" + str(value2) + "'"
    cursor.execute(sql)
    conn.commit()
    conn.close()


# end update the table rows


# function that deletes a row in the database
def delete(table_name, id):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "DELETE FROM " + table_name + " WHERE id = " + str(id)
    cursor.execute(sql)
    conn.commit()
    conn.close()


# function that deletes a row in the database using a column and a value
def delete_by_column(table_name, column, value):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "DELETE FROM " + table_name + " WHERE " + column + " = '" + str(value) + "'"
    cursor.execute(sql)
    conn.commit()
    conn.close()


def modify_by_column(table_name, column, value, column2, value2):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "UPDATE " + table_name + " SET " + column2 + " = '" + str(value2) + "' WHERE " + column + " = '" + str(value) + "'"
    cursor.execute(sql)
    conn.commit()
    conn.close()


# function return a column value then deletes the row in the database using a column and a value
def delete_by_column_and_return(table_name, column, value):
    to_return = get_row_by_column(table_name, column, str(value))
    delete_by_column(table_name, column, str(value))
    return to_return


# function that return the id of a row in the database a column and a value if not return false
def get_id(table_name, column, value):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT id FROM " + table_name + " WHERE " + column + " = '" + str(value) + "'"
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return False
    return result[0][0]


# function returns a row using its id
def get_row(table_name, id):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name + " WHERE id = " + str(id)
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return False
    return result[0]


# function returns all row
def get_all_row(table_name):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return []
    return result


# function returns all row and order by column
def get_all_row_order_by(table_name, column):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name + " ORDER BY " + column
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return []
    return result


# function returns all row and descending order by column
def get_all_row_order_by_desc(table_name, column):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name + " ORDER BY " + column + " DESC"
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.close()
    if len(result) == 0:
        return []
    return result


# function displays table columns
def display_columns(table_name):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name
    cursor.execute(sql)
    result = cursor.fetchall()
    for i in cursor.description:
        print(i[0], end=" ")
    print()
    for i in result:
        for j in i:
            print(j, end=" ")
        print()
    conn.close()


# function return table columns
def get_columns(table_name):
    conn = mysql.connector.connect(user=user_name, password=password, host=host, database=db_name)
    cursor = conn.cursor()
    sql = "SELECT * FROM " + table_name
    cursor.execute(sql)
    result = cursor.fetchall()
    columns = []
    for i in cursor.description:
        columns.append(i[0])
    conn.close()
    return columns


class Cars:
    def __init__(self, id1=-1, name="", model=0, year=0, price=False):
        if type(id1) == list:
            self.id = id1[0]
            self.car_name = id1[1]
            self.car_type = id1[2]
            self.car_price = id1[3]
            if id1[4] == 0:
                self.rented = False
            else:
                self.rented = True
        else:
            self.id = id1
            self.car_name = name
            self.car_type = model
            self.car_price = year
            if price == 0:
                self.rented = False
            else:
                self.rented = True

    def __int__(self):
        return self.id

class Booking:
    def __init__(self, id1, car_id=0, user_id="", start_date="", end_date="", price="", asdf=""):
        if len(id1) > 1:
            self.id = id1[0]
            self.car_obj = id1[1]
            self.customer_name = id1[2]
            self.email = id1[3]
            self.phone = id1[4]
            self.hire_date = id1[5]
            self.return_date = id1[6]
        else:
            self.id = id1
            self.car_obj = car_id
            self.customer_name = user_id
            self.email = start_date
            self.phone = end_date
            self.hire_date = price
            self.return_date = asdf


if __name__ == '__main__':
    create_db()
    create_table_with_type("Cars", ["id", "car_name", "car_type", "car_price", "rented"],
                           ["INT AUTO_INCREMENT PRIMARY KEY", "VARCHAR(255)", "INT", "INT", "BOOLEAN"])

    create_table_with_type("Booking", ["id", "car_obj", "customer_name", "email", "phone", "hire_date", "return_date", "returned"],
                           ["INT AUTO_INCREMENT PRIMARY KEY", "INT", "VARCHAR(255)", "VARCHAR(255)", "VARCHAR(255)", "DATE", "DATE", "BOOLEAN"])

    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Toyota", 1, 100, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Honda", 1, 100, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["BMW", 2, 200, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Mercedes", 2, 200, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Audi", 3, 300, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Lamborghini", 3, 300, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Ferrari", 3, 300, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Porsche", 3, 300, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Bugatti", 3, 300, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Koenigsegg", 3, 300, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["McLaren", 3, 300, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Rolls Royce", 1, 400, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Bentley", 1, 400, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Lexus", 2, 500, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Maserati", 2, 500, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Jaguar", 1, 500, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Land Rover", 2, 500, 0])
    insert("Cars", ["car_name", "car_type", "car_price", "rented"], ["Range Rover", 1, 500, 0])