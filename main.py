import hashlib
import sqlite3
from getpass import getpass

# Connect to SQLite database
conn = sqlite3.connect('food_ordering.db')
cursor = conn.cursor()

# Global variable to store user's cart
cart = []


# ----------------register User------------------------
def register_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    # Check if the username already exists
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        print("Username already exists. Please choose a different username.")
        return

    try:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                       (username, hashed_password, 'user'))
        conn.commit()
        print("Restaurant owner registration successful! Please log in.")
    except sqlite3.Error as e:
        print(f"Error registering restaurant owner: {e}")


# ----------------register Owner------------------------
def register_owner(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Check if the username already exists
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        print("Username already exists. Please choose a different username.")
        return

    try:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                       (username, hashed_password, 'owner'))
        conn.commit()
        print("Restaurant owner registration successful! Please log in.")
    except sqlite3.Error as e:
        print(f"Error registering restaurant owner: {e}")


# ----------------Login User------------------------
def login_user(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = cursor.fetchone()
    return user


# ----------------Add restaurant------------------------
def add_restaurant(user_id):
    restaurant_name = input("Enter the name of your restaurant: ")

    # Check if the restaurant name already exists
    cursor.execute('SELECT * FROM restaurants WHERE name = ?', (restaurant_name,))
    existing_restaurant = cursor.fetchone()
    if existing_restaurant:
        print("Restaurant with this name already exists.")
    else:
        # Insert new restaurant into the database
        cursor.execute('INSERT INTO restaurants (name, owner) VALUES (?, ?)', (restaurant_name, user_id))
        conn.commit()
        print("Restaurant added successfully!")


# ----------------Update Order Status------------------------
def update_order_status(order_id, new_status):
    # Check if the order exists
    cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    if not order:
        print("Order not found.")
        return

    # Update the status of the order
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    print(f"Order {order_id} status updated to '{new_status}'.")


# ----------------Add Menu Items------------------------
def add_menu_item(user_id):
    restaurant_name = input("Enter the name of your restaurant: ")
    # Check if the restaurant exists and belongs to the owner
    cursor.execute('SELECT * FROM restaurants WHERE name = ? AND owner = ?', (restaurant_name, user_id))
    restaurant = cursor.fetchone()
    if not restaurant:
        print("Restaurant not found or you do not have permission to manage this restaurant.")
        return

    item_name = input("Enter the name of the menu item: ")
    item_price = float(input("Enter the price of the menu item: "))

    cursor.execute('INSERT INTO menu_items (restaurant_id, name, price) VALUES (?, ?, ?)',
                   (restaurant[0], item_name, item_price))
    conn.commit()
    print("Menu item added successfully.")


# ----------------Update Menu Items------------------------
def update_menu_item(user_id):
    restaurant_name = input("Enter the name of your restaurant: ")
    # Check if the restaurant exists and belongs to the owner
    cursor.execute('SELECT * FROM restaurants WHERE name = ? AND owner = ?', (restaurant_name, user_id))
    restaurant = cursor.fetchone()
    if not restaurant:
        print("Restaurant not found or you do not have permission to manage this restaurant.")
        return

    item_name = input("Enter the name of the menu item to update: ")
    new_price = float(input("Enter the new price of the menu item: "))

    cursor.execute('UPDATE menu_items SET price = ? WHERE restaurant_id = ? AND name = ?',
                   (new_price, restaurant[0], item_name))
    conn.commit()
    print("Menu item updated successfully.")


# ----------------Restaurant Menu------------------------
def resturent_menu(user_id):
    restaurant_name = input("Enter the name of your restaurant: ")
    # Check if the restaurant exists and belongs to the owner
    cursor.execute('SELECT * FROM restaurants WHERE name = ? AND owner = ?', (restaurant_name, user_id))
    restaurant = cursor.fetchone()
    if not restaurant:
        print("Restaurant not found or you do not have permission to manage this restaurant.")
        return

    cursor.execute('SELECT * FROM menu_items WHERE restaurant_id = ?', (restaurant[0],))
    menu_items = cursor.fetchall()
    if not menu_items:
        print("No menu items found.")
    else:
        print(f"Menu for {restaurant_name}:")
        for item in menu_items:
            print(f"{item[0]}. {item[2]} - Rs.{item[3]:.2f}")


# ----------------Browse Restaurants------------------------
def browse_restaurants():
    cursor.execute('SELECT * FROM restaurants')
    restaurants = cursor.fetchall()
    print("Available Restaurants:")
    for restaurant in restaurants:
        print(f"{restaurant[0]}. {restaurant[1]}")

    while True:
        try:
            choice = int(input("Please enter the number of the restaurant you'd like to browse: "))
            if choice < 1 or choice > len(restaurants):
                print("Invalid choice. Please try again.")
            else:
                browse_menu(restaurants[choice - 1][0])
                break
        except ValueError:
            print("Invalid input. Please enter a valid number.")


# ----------------Browse Menu------------------------
def browse_menu(restaurant_id):
    cursor.execute('SELECT * FROM menu_items WHERE restaurant_id = ?', (restaurant_id,))
    menu_items = cursor.fetchall()
    print(f"\nMenu for this restaurant:")
    for index, item in enumerate(menu_items, start=1):
        print(f"{index}. {item[2]} - Rs.{item[3]:.2f}")

    global cart
    while True:
        try:
            choice = int(
                input("\nPlease enter the number of the item you'd like to add to your cart (or 0 to go back): "))
            if choice == 0:
                break
            elif choice < 1 or choice > len(menu_items):
                print("Invalid choice. Please try again.")
            else:
                quantity = int(input("Quantity: "))
                if quantity < 1:
                    print("Invalid quantity. Please enter a valid quantity.")
                else:
                    cart.append((menu_items[choice - 1], quantity))
                    print(f"{menu_items[choice - 1][2]} added to cart.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    return cart


# ----------------View Cart------------------------
def view_cart():
    global cart
    if not cart:
        print("Your cart is empty.")
        return

    total = 0
    print("Your Cart:")
    for item, quantity in cart:
        item_name, price = item[2], item[3]
        item_total = price * quantity
        print(f"{item_name} - Rs.{price:.2f} x {quantity} = Rs.{item_total:.2f}")
        total += item_total

    print(f"\nTotal: Rs.{total:.2f}")

    return total


# ----------------Place Order------------------------
def place_order(user_id):
    global cart
    if not cart:
        print("Your cart is empty. Please add items before placing an order.")
        return

    for item, quantity in cart:
        item_id = item[0]
        cursor.execute('INSERT INTO orders (user_id, item_id, quantity, status) VALUES (?, ?, ?, ?)',
                       (user_id, item_id, quantity, 'pending'))

    conn.commit()
    print("Order placed successfully!")
    cart.clear()  # Clear cart after placing order


# ----------------Owner Menu------------------------
def owner_menu(user_id):
    global new_status
    while True:
        print("\n1. Add Menu Item")
        print("2. Update Menu Item")
        print("3. View Menu")
        print("4. Add Restaurant")
        print("5. Update Order Status")
        print("6. Back to Main Menu")
        choice = input("Please enter your choice: ")

        if choice == "1":
            add_menu_item(user_id)
        elif choice == "2":
            update_menu_item(user_id)
        elif choice == "3":
            resturent_menu(user_id)
        elif choice == "4":
            add_restaurant(user_id)
        elif choice == "5":
            order_id = int(input("Enter the ID of the order you want to update: "))
            print("Chose the status of order")
            print("\n1. Pending")
            print("2. Confirmed")
            print("3. Preparing")
            print("4. Out for Delivery")
            print("5. Delivered")
            print("6. Cancelled")
            choice = input("Please enter your choice: ")
            if choice == "1":
                new_status = "Pending"
            elif choice == "2":
                new_status = "Confirmed"
            elif choice == "3":
                new_status = "Preparing"
            elif choice == "2":
                new_status = "Confirmed"
            elif choice == "4":
                new_status = "Out for Delivery"
            elif choice == "5":
                new_status = "Delivered"
            elif choice == "6":
                new_status = "Cancelled"
            update_order_status(order_id, new_status)
        elif choice == "6":
            print("Returning to main menu.")
            break
        else:
            print("Invalid choice. Please try again.")


# ----------------User Menu------------------------
def user_menu(user_id):
    while True:
        print("\n1. Browse Restaurants")
        print("2. View Cart")
        print("3. Place Order")
        print("4. Logout")
        choice = input("Please enter your choice: ")

        if choice == "1":
            browse_restaurants()
        elif choice == "2":
            view_cart()
        elif choice == "3":
            place_order(user_id)
        elif choice == "4":
            print("Logged out successfully. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


# ----------------Main Menu------------------------
def main_menu():
    print("\n\033[92m" + "*" * 15 + " Welcome to Our Food Ordering System! " + "*" * 15 + "\033[0m")
    while True:
        print("\n1. Login as User")
        print("2. Register as User")
        print("3. Login as Restaurant Owner")
        print("4. Register as Restaurant Owner")
        print("5. Exit")
        choice = input("Please enter your choice: ")

        if choice == "1":
            # Regular user login
            username = input("Username: ")
            password = getpass("Password: ")
            user = login_user(username, password)
            if user:
                print(f"Login successful! Welcome, {username}!")
                if user[3] != 'owner':
                    user_menu(user[0])  # Pass user_id to user_menu
                else:
                    print("You are logged in as a restaurant owner. Switch to owner menu.")
                    owner_menu(user[0])  # Pass user_id to owner_menu
            else:
                print("Invalid credentials. Please try again.")
        elif choice == "2":
            # Regular user registration
            username = input("Username: ")
            password = getpass("Password: ")
            register_user(username, password)
            print("Registration successful! Please log in.")
        elif choice == "3":
            # Restaurant owner login
            username = input("Username: ")
            password = getpass("Password: ")
            user = login_user(username, password)
            if user and user[3] == 'owner':
                print(f"Login successful! Welcome, {username}!")
                owner_menu(user[0])  # Pass user_id to owner_menu
            else:
                print("Invalid credentials. Please try again.")
        elif choice == "4":
            # Restaurant owner registration
            username = input("Username: ")
            password = getpass("Password: ")
            register_owner(username, password)
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("\033[91mInvalid choice. Please try again.\033[0m")


if __name__ == "__main__":
    main_menu()



# Food ordering system
# Code by Chathura Devinda Gamage @Sabaragamuwa University of Sri Lanka
