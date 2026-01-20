import sqlite3
import sys
import os
from datetime import datetime, timedelta
from getpass import getpass

def get_db():
    """Create database connection"""
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initialize database tables if they don't exist"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create Patron table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Patron (
        patron_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('Admin', 'Librarian', 'Student', 'Guest', 'Bank')),
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create Books table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        isbn TEXT UNIQUE NOT NULL,
        published_year INTEGER,
        genre TEXT,
        type TEXT CHECK(type IN ('Physical', 'E-book', 'Audiobook', 'Reference')) DEFAULT 'Physical',
        call_number TEXT UNIQUE NOT NULL,
        shelf_location TEXT,
        available INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create Transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patron_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        borrow_date DATE NOT NULL,
        return_date DATE,
        fine REAL DEFAULT 0,
        item_type TEXT CHECK(item_type IN ('Physical', 'E-book', 'Audiobook')) DEFAULT 'Physical',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patron_id) REFERENCES Patron(patron_id),
        FOREIGN KEY (book_id) REFERENCES Books(book_id)
    )
    ''')
    
    # Create Feedback table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Feedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patron_id INTEGER,
        feedback_date DATE NOT NULL,
        comment TEXT NOT NULL,
        rating INTEGER CHECK(rating BETWEEN 1 AND 5),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patron_id) REFERENCES Patron(patron_id)
    )
    ''')
    
    # Create Payments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        patron_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_date DATE NOT NULL,
        purpose TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (patron_id) REFERENCES Patron(patron_id)
    )
    ''')
    
    # Create default admin if not exists
    cursor.execute("SELECT * FROM Patron WHERE role = 'Admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO Patron (name, email, password, role, is_active) VALUES (?, ?, ?, ?, ?)",
            ("System Admin", "admin@library.com", "admin123", "Admin", 1)
        )
    
    # Create default librarian if not exists
    cursor.execute("SELECT * FROM Patron WHERE role = 'Librarian'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO Patron (name, email, password, role, is_active) VALUES (?, ?, ?, ?, ?)",
            ("Library Staff", "librarian@library.com", "lib123", "Librarian", 1)
        )
    
    # Create default bank if not exists
    cursor.execute("SELECT * FROM Patron WHERE role = 'Bank'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO Patron (name, email, password, role, is_active) VALUES (?, ?, ?, ?, ?)",
            ("Bank Officer", "bank@library.com", "bank123", "Bank", 1)
        )
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

def calculate_fine(borrow_date, return_date=None):
    """Calculate fine based on borrow date"""
    try:
        if isinstance(borrow_date, str):
            borrow_date = datetime.strptime(borrow_date, "%Y-%m-%d")
        
        if return_date:
            if isinstance(return_date, str):
                return_date = datetime.strptime(return_date, "%Y-%m-%d")
            days_diff = (return_date - borrow_date).days
        else:
            days_diff = (datetime.now() - borrow_date).days
        
        # Fine calculation: RM 1 per day after 14 days
        if days_diff > 14:
            fine = (days_diff - 14) * 1.0
            return round(fine, 2)
        return 0.0
    except:
        return 0.0

def get_patron_total_fine(patron_id):
    """Get total fine for a patron"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(fine) as total FROM Transactions WHERE patron_id = ? AND return_date IS NULL", 
                  (patron_id,))
    result = cursor.fetchone()
    conn.close()
    return result['total'] or 0

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def display_title(title):
    """Display title with border"""
    clear_screen()
    print("=" * 60)
    print(f"{title:^60}")
    print("=" * 60)
    print()

def login_role(role):
    """Login for different roles"""
    display_title(f"{role} Login")
    
    if role == "Student":
        name = input("Enter your name: ").strip()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Patron WHERE name=? AND role='Student'", (name,))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return user
        else:
            print("\n❌ No student found with that name!")
            input("Press Enter to continue...")
            return None
    else:
        email = input("Enter email: ").strip()
        password = getpass("Enter password: ").strip()
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Patron WHERE email=? AND password=? AND role=?", 
                      (email, password, role))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return user
        else:
            print("\n❌ Invalid credentials!")
            input("Press Enter to continue...")
            return None

def home_menu():
    """Main home menu"""
    while True:
        display_title("LIBRARY BORROWING SYSTEM")
        print("1. Admin Login")
        print("2. Librarian Login")
        print("3. Student Login")
        print("4. Guest Access")
        print("5. Bank Login")
        print("6. Search Books")
        print("7. Exit")
        print()
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            user = login_role("Admin")
            if user:
                admin_menu(user)
        elif choice == "2":
            user = login_role("Librarian")
            if user:
                librarian_menu(user)
        elif choice == "3":
            user = login_role("Student")
            if user:
                student_menu(user)
        elif choice == "4":
            guest_menu()
        elif choice == "5":
            user = login_role("Bank")
            if user:
                bank_menu(user)
        elif choice == "6":
            search_books()
        elif choice == "7":
            print("\nThank you for using Library System. Goodbye!")
            sys.exit(0)
        else:
            print("\n❌ Invalid choice!")
            input("Press Enter to continue...")

# ==================== ADMIN FUNCTIONS ====================
def admin_menu(user):
    """Admin panel menu"""
    while True:
        display_title(f"ADMIN PANEL - Welcome {user['name']}")
        print("1. View All Patrons")
        print("2. Add New Patron")
        print("3. Update Patron")
        print("4. Delete Patron")
        print("5. View All Books")
        print("6. View All Transactions")
        print("7. Create Transaction")
        print("8. Update Transaction")
        print("9. Delete Transaction")
        print("10. View System Statistics")
        print("11. Logout")
        print()
        
        choice = input("Enter your choice (1-11): ").strip()
        
        if choice == "1":
            view_all_patrons()
        elif choice == "2":
            add_patron()
        elif choice == "3":
            update_patron()
        elif choice == "4":
            delete_patron()
        elif choice == "5":
            view_all_books()
        elif choice == "6":
            view_all_transactions()
        elif choice == "7":
            create_transaction()
        elif choice == "8":
            update_transaction()
        elif choice == "9":
            delete_transaction()
        elif choice == "10":
            view_system_statistics()
        elif choice == "11":
            break
        else:
            print("\n❌ Invalid choice!")
            input("Press Enter to continue...")

def view_all_patrons():
    """View all patrons"""
    display_title("ALL PATRONS")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Patron ORDER BY patron_id")
    patrons = cursor.fetchall()
    
    if not patrons:
        print("No patrons found!")
        input("\nPress Enter to continue...")
        return
    
    print(f"{'ID':<5} {'Name':<20} {'Email':<25} {'Role':<12} {'Status':<10}")
    print("-" * 75)
    for p in patrons:
        status = "Active" if p['is_active'] == 1 else "Inactive"
        print(f"{p['patron_id']:<5} {p['name']:<20} {p['email']:<25} {p['role']:<12} {status:<10}")
    
    conn.close()
    input("\nPress Enter to continue...")

def add_patron():
    """Add new patron"""
    display_title("ADD NEW PATRON")
    
    name = input("Enter name: ").strip()
    email = input("Enter email: ").strip()
    password = getpass("Enter password: ").strip()
    role = input("Enter role (Admin/Librarian/Student/Guest/Bank): ").strip().capitalize()
    
    if role not in ['Admin', 'Librarian', 'Student', 'Guest', 'Bank']:
        print("\n❌ Invalid role!")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO Patron (name, email, password, role, is_active) VALUES (?, ?, ?, ?, 1)",
            (name, email, password, role)
        )
        conn.commit()
        print("\n✅ Patron added successfully!")
    except sqlite3.IntegrityError:
        print("\n❌ Email already exists!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def update_patron():
    """Update patron information"""
    display_title("UPDATE PATRON")
    
    patron_id = input("Enter patron ID to update: ").strip()
    if not patron_id.isdigit():
        print("\n❌ Invalid patron ID!")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Patron WHERE patron_id = ?", (patron_id,))
    patron = cursor.fetchone()
    
    if not patron:
        print("\n❌ Patron not found!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    print(f"\nCurrent details for Patron ID {patron_id}:")
    print(f"Name: {patron['name']}")
    print(f"Email: {patron['email']}")
    print(f"Role: {patron['role']}")
    print(f"Active: {'Yes' if patron['is_active'] == 1 else 'No'}")
    print()
    
    name = input(f"New name (press Enter to keep '{patron['name']}'): ").strip()
    email = input(f"New email (press Enter to keep '{patron['email']}'): ").strip()
    role = input(f"New role (press Enter to keep '{patron['role']}'): ").strip().capitalize()
    is_active = input("Set active? (1=Yes, 0=No, press Enter to skip): ").strip()
    
    updates = []
    params = []
    
    if name:
        updates.append("name = ?")
        params.append(name)
    if email:
        updates.append("email = ?")
        params.append(email)
    if role and role in ['Admin', 'Librarian', 'Student', 'Guest', 'Bank']:
        updates.append("role = ?")
        params.append(role)
    if is_active in ['0', '1']:
        updates.append("is_active = ?")
        params.append(int(is_active))
    
    if updates:
        params.append(patron_id)
        query = f"UPDATE Patron SET {', '.join(updates)} WHERE patron_id = ?"
        cursor.execute(query, params)
        conn.commit()
        print("\n✅ Patron updated successfully!")
    else:
        print("\n⚠️ No changes made.")
    
    conn.close()
    input("Press Enter to continue...")

def delete_patron():
    """Delete patron"""
    display_title("DELETE PATRON")
    
    patron_id = input("Enter patron ID to delete: ").strip()
    if not patron_id.isdigit():
        print("\n❌ Invalid patron ID!")
        input("Press Enter to continue...")
        return
    
    confirm = input(f"Are you sure you want to delete patron ID {patron_id}? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("\n❌ Deletion cancelled.")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Patron WHERE patron_id = ?", (patron_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print("\n✅ Patron deleted successfully!")
        else:
            print("\n❌ Patron not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def view_all_books():
    """View all books"""
    display_title("ALL BOOKS")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Books ORDER BY book_id")
    books = cursor.fetchall()
    
    if not books:
        print("No books found!")
        input("\nPress Enter to continue...")
        return
    
    print(f"{'ID':<5} {'Title':<30} {'Author':<20} {'Type':<12} {'Status':<10}")
    print("-" * 80)
    for b in books:
        status = "Available" if b['available'] == 1 else "Borrowed"
        print(f"{b['book_id']:<5} {b['title'][:28]:<30} {b['author'][:18]:<20} {b['type']:<12} {status:<10}")
    
    conn.close()
    input("\nPress Enter to continue...")

def view_all_transactions():
    """View all transactions"""
    display_title("ALL TRANSACTIONS")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, p.name as patron_name, b.title as book_title 
        FROM Transactions t
        LEFT JOIN Patron p ON t.patron_id = p.patron_id
        LEFT JOIN Books b ON t.book_id = b.book_id
        ORDER BY t.transaction_id DESC
    """)
    transactions = cursor.fetchall()
    
    if not transactions:
        print("No transactions found!")
        input("\nPress Enter to continue...")
        return
    
    print(f"{'TxnID':<6} {'Patron':<20} {'Book':<25} {'Borrow Date':<12} {'Return Date':<12} {'Fine':<8}")
    print("-" * 85)
    for t in transactions:
        return_date = t['return_date'] if t['return_date'] else "Not returned"
        fine = f"RM {t['fine']:.2f}" if t['fine'] else "RM 0.00"
        print(f"{t['transaction_id']:<6} {t['patron_name'][:18]:<20} {t['book_title'][:23]:<25} {t['borrow_date']:<12} {return_date:<12} {fine:<8}")
    
    conn.close()
    input("\nPress Enter to continue...")

def create_transaction():
    """Create new transaction"""
    display_title("CREATE TRANSACTION")
    
    patron_id = input("Enter patron ID: ").strip()
    book_id = input("Enter book ID: ").strip()
    borrow_date = input("Enter borrow date (YYYY-MM-DD) [today]: ").strip()
    
    if not patron_id.isdigit() or not book_id.isdigit():
        print("\n❌ Invalid ID!")
        input("Press Enter to continue...")
        return
    
    if not borrow_date:
        borrow_date = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if patron exists
    cursor.execute("SELECT * FROM Patron WHERE patron_id = ?", (patron_id,))
    patron = cursor.fetchone()
    if not patron:
        print("\n❌ Patron not found!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    # Check if book exists
    cursor.execute("SELECT * FROM Books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    if not book:
        print("\n❌ Book not found!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    try:
        cursor.execute("""
            INSERT INTO Transactions (patron_id, book_id, borrow_date, return_date, fine, item_type) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patron_id, book_id, borrow_date, None, 0, book['type']))
        conn.commit()
        print("\n✅ Transaction created successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def update_transaction():
    """Update transaction"""
    display_title("UPDATE TRANSACTION")
    
    txn_id = input("Enter transaction ID to update: ").strip()
    if not txn_id.isdigit():
        print("\n❌ Invalid transaction ID!")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Transactions WHERE transaction_id = ?", (txn_id,))
    transaction = cursor.fetchone()
    
    if not transaction:
        print("\n❌ Transaction not found!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    print(f"\nCurrent details for Transaction ID {txn_id}:")
    print(f"Patron ID: {transaction['patron_id']}")
    print(f"Book ID: {transaction['book_id']}")
    print(f"Borrow Date: {transaction['borrow_date']}")
    print(f"Return Date: {transaction['return_date'] or 'Not returned'}")
    print(f"Fine: RM {transaction['fine']:.2f}")
    print()
    
    patron_id = input(f"New patron ID (press Enter to keep {transaction['patron_id']}): ").strip()
    book_id = input(f"New book ID (press Enter to keep {transaction['book_id']}): ").strip()
    borrow_date = input(f"New borrow date (press Enter to keep {transaction['borrow_date']}): ").strip()
    return_date = input(f"New return date (press Enter to keep current): ").strip()
    fine = input(f"New fine amount (press Enter to keep {transaction['fine']}): ").strip()
    
    updates = []
    params = []
    
    if patron_id:
        updates.append("patron_id = ?")
        params.append(int(patron_id))
    if book_id:
        updates.append("book_id = ?")
        params.append(int(book_id))
    if borrow_date:
        updates.append("borrow_date = ?")
        params.append(borrow_date)
    if return_date is not None:
        updates.append("return_date = ?")
        params.append(return_date if return_date else None)
    if fine:
        updates.append("fine = ?")
        params.append(float(fine))
    
    if updates:
        params.append(txn_id)
        query = f"UPDATE Transactions SET {', '.join(updates)} WHERE transaction_id = ?"
        cursor.execute(query, params)
        conn.commit()
        print("\n✅ Transaction updated successfully!")
    else:
        print("\n⚠️ No changes made.")
    
    conn.close()
    input("Press Enter to continue...")

def delete_transaction():
    """Delete transaction"""
    display_title("DELETE TRANSACTION")
    
    txn_id = input("Enter transaction ID to delete: ").strip()
    if not txn_id.isdigit():
        print("\n❌ Invalid transaction ID!")
        input("Press Enter to continue...")
        return
    
    confirm = input(f"Are you sure you want to delete transaction ID {txn_id}? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("\n❌ Deletion cancelled.")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Transactions WHERE transaction_id = ?", (txn_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print("\n✅ Transaction deleted successfully!")
        else:
            print("\n❌ Transaction not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def view_system_statistics():
    """View system statistics"""
    display_title("SYSTEM STATISTICS")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Total patrons
    cursor.execute("SELECT COUNT(*) as count FROM Patron")
    total_patrons = cursor.fetchone()['count']
    
    # Total books
    cursor.execute("SELECT COUNT(*) as count FROM Books")
    total_books = cursor.fetchone()['count']
    
    # Available books
    cursor.execute("SELECT COUNT(*) as count FROM Books WHERE available = 1")
    available_books = cursor.fetchone()['count']
    
    # Borrowed books
    cursor.execute("SELECT COUNT(*) as count FROM Books WHERE available = 0")
    borrowed_books = cursor.fetchone()['count']
    
    # Total transactions
    cursor.execute("SELECT COUNT(*) as count FROM Transactions")
    total_transactions = cursor.fetchone()['count']
    
    # Total fines
    cursor.execute("SELECT SUM(fine) as total FROM Transactions")
    total_fines = cursor.fetchone()['total'] or 0
    
    print(f"Total Patrons: {total_patrons}")
    print(f"Total Books: {total_books}")
    print(f"Available Books: {available_books}")
    print(f"Borrowed Books: {borrowed_books}")
    print(f"Total Transactions: {total_transactions}")
    print(f"Total Fines: RM {total_fines:.2f}")
    print()
    
    # Patrons by role
    print("Patrons by Role:")
    cursor.execute("SELECT role, COUNT(*) as count FROM Patron GROUP BY role ORDER BY count DESC")
    roles = cursor.fetchall()
    for r in roles:
        print(f"  {r['role']}: {r['count']}")
    
    print()
    
    # Books by type
    print("Books by Type:")
    cursor.execute("SELECT type, COUNT(*) as count FROM Books GROUP BY type ORDER BY count DESC")
    types = cursor.fetchall()
    for t in types:
        print(f"  {t['type']}: {t['count']}")
    
    conn.close()
    input("\nPress Enter to continue...")

# ==================== LIBRARIAN FUNCTIONS ====================
def librarian_menu(user):
    """Librarian panel menu"""
    while True:
        display_title(f"LIBRARIAN PANEL - Welcome {user['name']}")
        print("1. View All Books")
        print("2. Add New Book")
        print("3. Update Book")
        print("4. Delete Book")
        print("5. Process Book Return")
        print("6. View All Transactions")
        print("7. Search Books")
        print("8. View Borrowed Books")
        print("9. Logout")
        print()
        
        choice = input("Enter your choice (1-9): ").strip()
        
        if choice == "1":
            view_all_books()
        elif choice == "2":
            add_book()
        elif choice == "3":
            update_book()
        elif choice == "4":
            delete_book()
        elif choice == "5":
            process_book_return()
        elif choice == "6":
            view_all_transactions()
        elif choice == "7":
            search_books()
        elif choice == "8":
            view_borrowed_books()
        elif choice == "9":
            break
        else:
            print("\n❌ Invalid choice!")
            input("Press Enter to continue...")

def add_book():
    """Add new book"""
    display_title("ADD NEW BOOK")
    
    title = input("Enter book title: ").strip()
    author = input("Enter author: ").strip()
    isbn = input("Enter ISBN: ").strip()
    published_year = input("Enter published year: ").strip()
    genre = input("Enter genre: ").strip()
    book_type = input("Enter type (Physical/E-book/Audiobook/Reference): ").strip().capitalize()
    call_number = input("Enter call number: ").strip()
    shelf_location = input("Enter shelf location (optional): ").strip()
    
    if book_type not in ['Physical', 'E-book', 'Audiobook', 'Reference']:
        book_type = 'Physical'
    
    if not published_year.isdigit():
        published_year = None
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO Books (title, author, isbn, published_year, genre, type, call_number, shelf_location, available) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        """, (title, author, isbn, published_year, genre, book_type, call_number, shelf_location))
        conn.commit()
        print("\n✅ Book added successfully!")
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in str(e):
            print("\n❌ ISBN or Call Number already exists!")
        else:
            print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def update_book():
    """Update book information"""
    display_title("UPDATE BOOK")
    
    book_id = input("Enter book ID to update: ").strip()
    if not book_id.isdigit():
        print("\n❌ Invalid book ID!")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    
    if not book:
        print("\n❌ Book not found!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    print(f"\nCurrent details for Book ID {book_id}:")
    print(f"Title: {book['title']}")
    print(f"Author: {book['author']}")
    print(f"ISBN: {book['isbn']}")
    print(f"Published Year: {book['published_year']}")
    print(f"Genre: {book['genre']}")
    print(f"Type: {book['type']}")
    print(f"Call Number: {book['call_number']}")
    print(f"Shelf Location: {book['shelf_location'] or 'Not specified'}")
    print(f"Available: {'Yes' if book['available'] == 1 else 'No'}")
    print()
    
    title = input(f"New title (press Enter to keep '{book['title']}'): ").strip()
    author = input(f"New author (press Enter to keep '{book['author']}'): ").strip()
    isbn = input(f"New ISBN (press Enter to keep '{book['isbn']}'): ").strip()
    published_year = input(f"New published year (press Enter to keep {book['published_year']}): ").strip()
    genre = input(f"New genre (press Enter to keep '{book['genre']}'): ").strip()
    book_type = input(f"New type (press Enter to keep '{book['type']}'): ").strip().capitalize()
    call_number = input(f"New call number (press Enter to keep '{book['call_number']}'): ").strip()
    shelf_location = input(f"New shelf location (press Enter to keep current): ").strip()
    available = input("Set available? (1=Yes, 0=No, press Enter to skip): ").strip()
    
    updates = []
    params = []
    
    if title:
        updates.append("title = ?")
        params.append(title)
    if author:
        updates.append("author = ?")
        params.append(author)
    if isbn:
        updates.append("isbn = ?")
        params.append(isbn)
    if published_year:
        updates.append("published_year = ?")
        params.append(published_year)
    if genre:
        updates.append("genre = ?")
        params.append(genre)
    if book_type and book_type in ['Physical', 'E-book', 'Audiobook', 'Reference']:
        updates.append("type = ?")
        params.append(book_type)
    if call_number:
        updates.append("call_number = ?")
        params.append(call_number)
    if shelf_location is not None:
        updates.append("shelf_location = ?")
        params.append(shelf_location)
    if available in ['0', '1']:
        updates.append("available = ?")
        params.append(int(available))
    
    if updates:
        params.append(book_id)
        query = f"UPDATE Books SET {', '.join(updates)} WHERE book_id = ?"
        cursor.execute(query, params)
        conn.commit()
        print("\n✅ Book updated successfully!")
    else:
        print("\n⚠️ No changes made.")
    
    conn.close()
    input("Press Enter to continue...")

def delete_book():
    """Delete book"""
    display_title("DELETE BOOK")
    
    book_id = input("Enter book ID to delete: ").strip()
    if not book_id.isdigit():
        print("\n❌ Invalid book ID!")
        input("Press Enter to continue...")
        return
    
    confirm = input(f"Are you sure you want to delete book ID {book_id}? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("\n❌ Deletion cancelled.")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Books WHERE book_id = ?", (book_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print("\n✅ Book deleted successfully!")
        else:
            print("\n❌ Book not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def process_book_return():
    """Process book return"""
    display_title("PROCESS BOOK RETURN")
    
    book_id = input("Enter book ID to return: ").strip()
    if not book_id.isdigit():
        print("\n❌ Invalid book ID!")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if book exists
    cursor.execute("SELECT * FROM Books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    if not book:
        print("\n❌ Book not found!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    # Check if book is borrowed
    if book['available'] == 1:
        print("\n❌ This book is not borrowed!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    # Get the active transaction
    cursor.execute("""
        SELECT * FROM Transactions 
        WHERE book_id = ? AND return_date IS NULL
        ORDER BY transaction_id DESC LIMIT 1
    """, (book_id,))
    transaction = cursor.fetchone()
    
    if not transaction:
        print("\n❌ No active transaction found for this book!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate final fine
    final_fine = calculate_fine(transaction['borrow_date'], today)
    
    print(f"\nBook: {book['title']}")
    print(f"Borrowed on: {transaction['borrow_date']}")
    print(f"Returning on: {today}")
    print(f"Calculated fine: RM {final_fine:.2f}")
    
    confirm = input("\nConfirm return? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("\n❌ Return cancelled.")
        conn.close()
        input("Press Enter to continue...")
        return
    
    try:
        # Update transaction
        cursor.execute("""
            UPDATE Transactions 
            SET return_date = ?, fine = ?
            WHERE transaction_id = ?
        """, (today, final_fine, transaction['transaction_id']))
        
        # Update book availability (only for physical books)
        if book['type'] == 'Physical':
            cursor.execute("UPDATE Books SET available = 1 WHERE book_id = ?", (book_id,))
        
        conn.commit()
        print("\n✅ Book returned successfully!")
        print(f"Fine charged: RM {final_fine:.2f}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def view_borrowed_books():
    """View all borrowed books"""
    display_title("BORROWED BOOKS")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, p.name as patron_name, t.borrow_date, t.transaction_id
        FROM Books b
        JOIN Transactions t ON b.book_id = t.book_id
        JOIN Patron p ON t.patron_id = p.patron_id
        WHERE b.available = 0 AND t.return_date IS NULL
        ORDER BY t.borrow_date DESC
    """)
    books = cursor.fetchall()
    
    if not books:
        print("No borrowed books found!")
        input("\nPress Enter to continue...")
        return
    
    print(f"{'BookID':<7} {'Title':<30} {'Patron':<20} {'Borrow Date':<12} {'Days':<6}")
    print("-" * 80)
    for b in books:
        borrow_date = datetime.strptime(b['borrow_date'], "%Y-%m-%d")
        days_borrowed = (datetime.now() - borrow_date).days
        overdue = "(Overdue)" if days_borrowed > 14 else ""
        print(f"{b['book_id']:<7} {b['title'][:28]:<30} {b['patron_name'][:18]:<20} {b['borrow_date']:<12} {days_borrowed:<6} {overdue}")
    
    conn.close()
    input("\nPress Enter to continue...")

# ==================== STUDENT FUNCTIONS ====================
def student_menu(user):
    """Student panel menu"""
    while True:
        display_title(f"STUDENT PANEL - Welcome {user['name']}")
        print("1. View Available Books")
        print("2. Borrow Book")
        print("3. View My Current Loans")
        print("4. Return Book")
        print("5. View My Borrow History")
        print("6. View My Fines")
        print("7. Search Books")
        print("8. Logout")
        print()
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == "1":
            view_available_books(user)
        elif choice == "2":
            borrow_book(user)
        elif choice == "3":
            view_my_current_loans(user)
        elif choice == "4":
            return_book(user)
        elif choice == "5":
            view_my_borrow_history(user)
        elif choice == "6":
            view_my_fines(user)
        elif choice == "7":
            search_books()
        elif choice == "8":
            break
        else:
            print("\n❌ Invalid choice!")
            input("Press Enter to continue...")

def view_available_books(user):
    """View available books for borrowing"""
    display_title("AVAILABLE BOOKS")
    conn = get_db()
    cursor = conn.cursor()
    
    # Get books that are available
    cursor.execute("""
        SELECT * FROM Books 
        WHERE available = 1 
        ORDER BY title
    """)
    books = cursor.fetchall()
    
    if not books:
        print("No available books at the moment.")
        conn.close()
        input("\nPress Enter to continue...")
        return
    
    print(f"{'ID':<5} {'Title':<30} {'Author':<20} {'Type':<12} {'Call No':<15}")
    print("-" * 85)
    for b in books:
        print(f"{b['book_id']:<5} {b['title'][:28]:<30} {b['author'][:18]:<20} {b['type']:<12} {b['call_number']:<15}")
    
    conn.close()
    input("\nPress Enter to continue...")

def borrow_book(user):
    """Borrow a book"""
    display_title("BORROW BOOK")
    
    book_id = input("Enter book ID to borrow: ").strip()
    if not book_id.isdigit():
        print("\n❌ Invalid book ID!")
        input("Press Enter to continue...")
        return
    
    borrow_date = input("Enter borrow date (YYYY-MM-DD) [today]: ").strip()
    if not borrow_date:
        borrow_date = datetime.now().strftime("%Y-%m-%d")
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if book exists
    cursor.execute("SELECT * FROM Books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    
    if not book:
        print("\n❌ Book not found!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    # Check if book is available
    if book['available'] == 0:
        print("\n❌ This book is already borrowed!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    # Check if student already borrowed this book
    cursor.execute("""
        SELECT * FROM Transactions 
        WHERE patron_id = ? AND book_id = ? AND return_date IS NULL
    """, (user['patron_id'], book_id))
    existing_loan = cursor.fetchone()
    
    if existing_loan:
        print("\n❌ You already borrowed this book!")
        print(f"You borrowed it on {existing_loan['borrow_date']}")
        conn.close()
        input("Press Enter to continue...")
        return
    
    try:
        # Create transaction
        cursor.execute("""
            INSERT INTO Transactions (patron_id, book_id, borrow_date, return_date, fine, item_type) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user['patron_id'], book_id, borrow_date, None, 0, book['type']))
        
        # Update book availability (only for physical books)
        if book['type'] == 'Physical':
            cursor.execute("UPDATE Books SET available = 0 WHERE book_id = ?", (book_id,))
        
        conn.commit()
        print("\n✅ Book borrowed successfully!")
        print(f"Book: {book['title']}")
        print(f"Borrow Date: {borrow_date}")
        print(f"Due Date: {(datetime.strptime(borrow_date, '%Y-%m-%d') + timedelta(days=14)).strftime('%Y-%m-%d')}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def view_my_current_loans(user):
    """View student's current loans"""
    display_title("MY CURRENT LOANS")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, b.title, b.author, b.type
        FROM Transactions t 
        JOIN Books b ON t.book_id = b.book_id 
        WHERE t.patron_id = ? AND t.return_date IS NULL
        ORDER BY t.borrow_date DESC
    """, (user['patron_id'],))
    loans = cursor.fetchall()
    
    if not loans:
        print("You have no current loans.")
        conn.close()
        input("\nPress Enter to continue...")
        return
    
    total_fine = 0
    print(f"{'TxnID':<7} {'Book':<30} {'Borrow Date':<12} {'Days':<6} {'Fine':<8}")
    print("-" * 70)
    for loan in loans:
        borrow_date = datetime.strptime(loan['borrow_date'], "%Y-%m-%d")
        days_borrowed = (datetime.now() - borrow_date).days
        overdue_days = max(0, days_borrowed - 14)
        fine = overdue_days * 1.0
        total_fine += fine
        
        status = ""
        if days_borrowed > 14:
            status = f"(Overdue {overdue_days} days)"
        
        print(f"{loan['transaction_id']:<7} {loan['title'][:28]:<30} {loan['borrow_date']:<12} {days_borrowed:<6} RM {fine:.2f} {status}")
    
    print("-" * 70)
    print(f"Total fine due: RM {total_fine:.2f}")
    
    conn.close()
    input("\nPress Enter to continue...")

def return_book(user):
    """Return a borrowed book"""
    display_title("RETURN BOOK")
    
    transaction_id = input("Enter transaction ID to return: ").strip()
    if not transaction_id.isdigit():
        print("\n❌ Invalid transaction ID!")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if transaction exists and belongs to user
    cursor.execute("""
        SELECT t.*, b.title, b.type
        FROM Transactions t 
        JOIN Books b ON t.book_id = b.book_id 
        WHERE t.transaction_id = ? AND t.patron_id = ? AND t.return_date IS NULL
    """, (transaction_id, user['patron_id']))
    transaction = cursor.fetchone()
    
    if not transaction:
        print("\n❌ Transaction not found or already returned!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Calculate final fine
    final_fine = calculate_fine(transaction['borrow_date'], today)
    
    print(f"\nBook: {transaction['title']}")
    print(f"Borrowed on: {transaction['borrow_date']}")
    print(f"Returning on: {today}")
    print(f"Calculated fine: RM {final_fine:.2f}")
    
    confirm = input("\nConfirm return? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("\n❌ Return cancelled.")
        conn.close()
        input("Press Enter to continue...")
        return
    
    try:
        # Update transaction
        cursor.execute("""
            UPDATE Transactions 
            SET return_date = ?, fine = ?
            WHERE transaction_id = ? AND patron_id = ?
        """, (today, final_fine, transaction_id, user['patron_id']))
        
        # Update book availability (only for physical books)
        if transaction['type'] == 'Physical':
            cursor.execute("UPDATE Books SET available = 1 WHERE book_id = ?", (transaction['book_id'],))
        
        conn.commit()
        print("\n✅ Book returned successfully!")
        if final_fine > 0:
            print(f"Fine charged: RM {final_fine:.2f}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def view_my_borrow_history(user):
    """View student's borrow history"""
    display_title("MY BORROW HISTORY")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, b.title, b.author
        FROM Transactions t 
        JOIN Books b ON t.book_id = b.book_id 
        WHERE t.patron_id = ?
        ORDER BY t.borrow_date DESC
    """, (user['patron_id'],))
    history = cursor.fetchall()
    
    if not history:
        print("You have no borrow history.")
        conn.close()
        input("\nPress Enter to continue...")
        return
    
    print(f"{'Date':<12} {'Book':<30} {'Status':<12} {'Fine':<8}")
    print("-" * 65)
    for h in history:
        status = "Returned" if h['return_date'] else "Borrowed"
        fine = f"RM {h['fine']:.2f}" if h['fine'] else "RM 0.00"
        date = h['borrow_date']
        print(f"{date:<12} {h['title'][:28]:<30} {status:<12} {fine:<8}")
    
    conn.close()
    input("\nPress Enter to continue...")

def view_my_fines(user):
    """View student's fines"""
    display_title("MY FINES")
    conn = get_db()
    cursor = conn.cursor()
    
    # Current unpaid fines
    cursor.execute("""
        SELECT SUM(fine) as total_fine 
        FROM Transactions 
        WHERE patron_id = ? AND return_date IS NULL
    """, (user['patron_id'],))
    current_fine = cursor.fetchone()['total_fine'] or 0
    
    # Paid fines
    cursor.execute("""
        SELECT SUM(fine) as total_paid 
        FROM Transactions 
        WHERE patron_id = ? AND return_date IS NOT NULL
    """, (user['patron_id'],))
    paid_fine = cursor.fetchone()['total_paid'] or 0
    
    print(f"Current unpaid fines: RM {current_fine:.2f}")
    print(f"Total fines paid: RM {paid_fine:.2f}")
    print(f"Total fines: RM {current_fine + paid_fine:.2f}")
    print()
    
    # Show overdue books
    cursor.execute("""
        SELECT b.title, t.borrow_date, t.fine
        FROM Transactions t 
        JOIN Books b ON t.book_id = b.book_id 
        WHERE t.patron_id = ? AND t.return_date IS NULL
        ORDER BY t.borrow_date
    """, (user['patron_id'],))
    loans = cursor.fetchall()
    
    if loans:
        print("Current loans:")
        for loan in loans:
            borrow_date = datetime.strptime(loan['borrow_date'], "%Y-%m-%d")
            days_borrowed = (datetime.now() - borrow_date).days
            if days_borrowed > 14:
                overdue_days = days_borrowed - 14
                print(f"  {loan['title'][:30]}: {overdue_days} days overdue (RM {overdue_days * 1.0:.2f})")
    
    conn.close()
    input("\nPress Enter to continue...")

# ==================== GUEST FUNCTIONS ====================
def guest_menu():
    """Guest access menu"""
    while True:
        display_title("GUEST ACCESS")
        print("1. View All Books")
        print("2. Search Books")
        print("3. View Feedback")
        print("4. Add Feedback")
        print("5. Back to Main Menu")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            view_all_books_guest()
        elif choice == "2":
            search_books()
        elif choice == "3":
            view_feedback()
        elif choice == "4":
            add_feedback()
        elif choice == "5":
            break
        else:
            print("\n❌ Invalid choice!")
            input("Press Enter to continue...")

def view_all_books_guest():
    """View all books for guest"""
    display_title("BOOK COLLECTION")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Books ORDER BY title")
    books = cursor.fetchall()
    
    if not books:
        print("No books found in the library.")
        conn.close()
        input("\nPress Enter to continue...")
        return
    
    print(f"{'ID':<5} {'Title':<30} {'Author':<20} {'Type':<12} {'Status':<10}")
    print("-" * 80)
    for b in books:
        status = "Available" if b['available'] == 1 else "Borrowed"
        print(f"{b['book_id']:<5} {b['title'][:28]:<30} {b['author'][:18]:<20} {b['type']:<12} {status:<10}")
    
    conn.close()
    input("\nPress Enter to continue...")

def view_feedback():
    """View all feedback"""
    display_title("FEEDBACK")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.*, p.name as patron_name 
        FROM Feedback f 
        LEFT JOIN Patron p ON f.patron_id = p.patron_id 
        ORDER BY f.feedback_date DESC
    """)
    feedbacks = cursor.fetchall()
    
    if not feedbacks:
        print("No feedback yet.")
        conn.close()
        input("\nPress Enter to continue...")
        return
    
    for f in feedbacks:
        print(f"\nDate: {f['feedback_date']}")
        print(f"From: {f['patron_name'] or 'Anonymous'}")
        print(f"Rating: {'⭐' * f['rating']} ({f['rating']}/5)")
        print(f"Comment: {f['comment']}")
        print("-" * 50)
    
    conn.close()
    input("\nPress Enter to continue...")

def add_feedback():
    """Add feedback"""
    display_title("ADD FEEDBACK")
    
    name = input("Your name (optional): ").strip()
    feedback_date = input("Feedback date (YYYY-MM-DD) [today]: ").strip()
    if not feedback_date:
        feedback_date = datetime.now().strftime("%Y-%m-%d")
    
    rating = input("Rating (1-5): ").strip()
    if not rating.isdigit() or int(rating) < 1 or int(rating) > 5:
        print("\n❌ Rating must be between 1 and 5!")
        input("Press Enter to continue...")
        return
    
    comment = input("Your comments: ").strip()
    if not comment:
        print("\n❌ Comment cannot be empty!")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    patron_id = None
    if name:
        # Find or create guest patron
        cursor.execute("SELECT * FROM Patron WHERE name = ? AND role = 'Guest'", (name,))
        patron = cursor.fetchone()
        if not patron:
            cursor.execute(
                "INSERT INTO Patron (name, role, email, password, is_active) VALUES (?, 'Guest', ?, ?, 1)",
                (name, f"{name.lower().replace(' ', '')}@guest.com", "guest123")
            )
            conn.commit()
            cursor.execute("SELECT * FROM Patron WHERE name = ? AND role = 'Guest'", (name,))
            patron = cursor.fetchone()
        patron_id = patron['patron_id']
    
    try:
        cursor.execute(
            "INSERT INTO Feedback (patron_id, feedback_date, comment, rating) VALUES (?, ?, ?, ?)",
            (patron_id, feedback_date, comment, int(rating))
        )
        conn.commit()
        print("\n✅ Feedback added successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

# ==================== BANK FUNCTIONS ====================
def bank_menu(user):
    """Bank panel menu"""
    while True:
        display_title(f"BANK PANEL - Welcome {user['name']}")
        print("1. View All Payments")
        print("2. Record Payment")
        print("3. Update Payment")
        print("4. Delete Payment")
        print("5. View Patrons with Fines")
        print("6. Search Payments by Patron")
        print("7. View Bank Statistics")
        print("8. Logout")
        print()
        
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == "1":
            view_all_payments()
        elif choice == "2":
            record_payment()
        elif choice == "3":
            update_payment()
        elif choice == "4":
            delete_payment()
        elif choice == "5":
            view_patrons_with_fines()
        elif choice == "6":
            search_payments_by_patron()
        elif choice == "7":
            view_bank_statistics()
        elif choice == "8":
            break
        else:
            print("\n❌ Invalid choice!")
            input("Press Enter to continue...")

def view_all_payments():
    """View all payments"""
    display_title("ALL PAYMENTS")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, pt.name as patron_name 
        FROM Payments p 
        LEFT JOIN Patron pt ON p.patron_id = pt.patron_id 
        ORDER BY p.payment_date DESC
    """)
    payments = cursor.fetchall()
    
    if not payments:
        print("No payments found!")
        conn.close()
        input("\nPress Enter to continue...")
        return
    
    print(f"{'ID':<5} {'Date':<12} {'Patron':<20} {'Amount':<10} {'Purpose':<20}")
    print("-" * 70)
    for p in payments:
        print(f"{p['payment_id']:<5} {p['payment_date']:<12} {p['patron_name'][:18]:<20} RM {p['amount']:<7.2f} {p['purpose'][:18]:<20}")
    
    conn.close()
    input("\nPress Enter to continue...")

def record_payment():
    """Record a payment"""
    display_title("RECORD PAYMENT")
    
    patron_id = input("Enter patron ID: ").strip()
    amount = input("Enter amount (RM): ").strip()
    payment_date = input("Enter payment date (YYYY-MM-DD) [today]: ").strip()
    purpose = input("Enter purpose (e.g., Fine Payment): ").strip()
    
    if not patron_id.isdigit():
        print("\n❌ Invalid patron ID!")
        input("Press Enter to continue...")
        return
    
    try:
        amount = float(amount)
        if amount <= 0:
            print("\n❌ Amount must be positive!")
            input("Press Enter to continue...")
            return
    except ValueError:
        print("\n❌ Invalid amount!")
        input("Press Enter to continue...")
        return
    
    if not payment_date:
        payment_date = datetime.now().strftime("%Y-%m-%d")
    
    if not purpose:
        purpose = "Fine Payment"
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if patron exists
    cursor.execute("SELECT * FROM Patron WHERE patron_id = ?", (patron_id,))
    patron = cursor.fetchone()
    if not patron:
        print("\n❌ Patron not found!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    try:
        cursor.execute(
            "INSERT INTO Payments (patron_id, amount, payment_date, purpose) VALUES (?, ?, ?, ?)",
            (patron_id, amount, payment_date, purpose)
        )
        conn.commit()
        print("\n✅ Payment recorded successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def update_payment():
    """Update payment"""
    display_title("UPDATE PAYMENT")
    
    payment_id = input("Enter payment ID to update: ").strip()
    if not payment_id.isdigit():
        print("\n❌ Invalid payment ID!")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Payments WHERE payment_id = ?", (payment_id,))
    payment = cursor.fetchone()
    
    if not payment:
        print("\n❌ Payment not found!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    print(f"\nCurrent details for Payment ID {payment_id}:")
    print(f"Patron ID: {payment['patron_id']}")
    print(f"Amount: RM {payment['amount']:.2f}")
    print(f"Date: {payment['payment_date']}")
    print(f"Purpose: {payment['purpose']}")
    print()
    
    patron_id = input(f"New patron ID (press Enter to keep {payment['patron_id']}): ").strip()
    amount = input(f"New amount (press Enter to keep {payment['amount']:.2f}): ").strip()
    payment_date = input(f"New date (press Enter to keep {payment['payment_date']}): ").strip()
    purpose = input(f"New purpose (press Enter to keep '{payment['purpose']}'): ").strip()
    
    updates = []
    params = []
    
    if patron_id:
        updates.append("patron_id = ?")
        params.append(int(patron_id))
    if amount:
        try:
            updates.append("amount = ?")
            params.append(float(amount))
        except ValueError:
            print("\n❌ Invalid amount format!")
            conn.close()
            input("Press Enter to continue...")
            return
    if payment_date:
        updates.append("payment_date = ?")
        params.append(payment_date)
    if purpose:
        updates.append("purpose = ?")
        params.append(purpose)
    
    if updates:
        params.append(payment_id)
        query = f"UPDATE Payments SET {', '.join(updates)} WHERE payment_id = ?"
        cursor.execute(query, params)
        conn.commit()
        print("\n✅ Payment updated successfully!")
    else:
        print("\n⚠️ No changes made.")
    
    conn.close()
    input("Press Enter to continue...")

def delete_payment():
    """Delete payment"""
    display_title("DELETE PAYMENT")
    
    payment_id = input("Enter payment ID to delete: ").strip()
    if not payment_id.isdigit():
        print("\n❌ Invalid payment ID!")
        input("Press Enter to continue...")
        return
    
    confirm = input(f"Are you sure you want to delete payment ID {payment_id}? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("\n❌ Deletion cancelled.")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM Payments WHERE payment_id = ?", (payment_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print("\n✅ Payment deleted successfully!")
        else:
            print("\n❌ Payment not found!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    conn.close()
    input("Press Enter to continue...")

def view_patrons_with_fines():
    """View patrons with outstanding fines"""
    display_title("PATRONS WITH FINES")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.patron_id, p.name, p.role, SUM(t.fine) as total_fine
        FROM Patron p
        JOIN Transactions t ON p.patron_id = t.patron_id
        WHERE t.return_date IS NULL AND t.fine > 0
        GROUP BY p.patron_id
        ORDER BY total_fine DESC
    """)
    patrons = cursor.fetchall()
    
    if not patrons:
        print("No patrons with outstanding fines.")
        conn.close()
        input("\nPress Enter to continue...")
        return
    
    print(f"{'ID':<5} {'Name':<20} {'Role':<12} {'Total Fine':<12}")
    print("-" * 50)
    for p in patrons:
        print(f"{p['patron_id']:<5} {p['name']:<20} {p['role']:<12} RM {p['total_fine']:<9.2f}")
    
    conn.close()
    input("\nPress Enter to continue...")

def search_payments_by_patron():
    """Search payments by patron ID"""
    display_title("SEARCH PAYMENTS BY PATRON")
    
    patron_id = input("Enter patron ID: ").strip()
    if not patron_id.isdigit():
        print("\n❌ Invalid patron ID!")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if patron exists
    cursor.execute("SELECT * FROM Patron WHERE patron_id = ?", (patron_id,))
    patron = cursor.fetchone()
    if not patron:
        print("\n❌ Patron not found!")
        conn.close()
        input("Press Enter to continue...")
        return
    
    print(f"\nPatron: {patron['name']} ({patron['role']})")
    print(f"Email: {patron['email']}")
    print()
    
    # Get payments for this patron
    cursor.execute("""
        SELECT * FROM Payments 
        WHERE patron_id = ? 
        ORDER BY payment_date DESC
    """, (patron_id,))
    payments = cursor.fetchall()
    
    if not payments:
        print("No payments found for this patron.")
    else:
        print(f"{'Date':<12} {'Amount':<10} {'Purpose':<20}")
        print("-" * 45)
        total = 0
        for p in payments:
            print(f"{p['payment_date']:<12} RM {p['amount']:<7.2f} {p['purpose'][:18]:<20}")
            total += p['amount']
        print("-" * 45)
        print(f"Total paid: RM {total:.2f}")
    
    conn.close()
    input("\nPress Enter to continue...")

def view_bank_statistics():
    """View bank statistics"""
    display_title("BANK STATISTICS")
    conn = get_db()
    cursor = conn.cursor()
    
    # Total payments
    cursor.execute("SELECT COUNT(*) as count FROM Payments")
    total_payments = cursor.fetchone()['count']
    
    # Total received
    cursor.execute("SELECT SUM(amount) as total FROM Payments")
    total_received = cursor.fetchone()['total'] or 0
    
    # Average payment
    cursor.execute("SELECT AVG(amount) as avg FROM Payments")
    avg_payment = cursor.fetchone()['avg'] or 0
    
    # Patrons with fines
    cursor.execute("""
        SELECT COUNT(DISTINCT p.patron_id) as count
        FROM Patron p
        JOIN Transactions t ON p.patron_id = t.patron_id
        WHERE t.return_date IS NULL AND t.fine > 0
    """)
    patrons_with_fines = cursor.fetchone()['count']
    
    print(f"Total payments received: {total_payments}")
    print(f"Total amount received: RM {total_received:.2f}")
    print(f"Average payment amount: RM {avg_payment:.2f}")
    print(f"Patrons with outstanding fines: {patrons_with_fines}")
    print()
    
    # Recent payments
    cursor.execute("""
        SELECT p.payment_date, SUM(p.amount) as daily_total
        FROM Payments p
        GROUP BY p.payment_date
        ORDER BY p.payment_date DESC
        LIMIT 7
    """)
    recent = cursor.fetchall()
    
    if recent:
        print("Recent daily totals (last 7 days):")
        for r in recent:
            print(f"  {r['payment_date']}: RM {r['daily_total']:.2f}")
    
    conn.close()
    input("\nPress Enter to continue...")

# ==================== SEARCH BOOKS ====================
def search_books():
    """Search books"""
    display_title("SEARCH BOOKS")
    
    keyword = input("Enter search keyword (title, author, genre, ISBN): ").strip()
    if not keyword:
        print("\n❌ Please enter a search keyword!")
        input("Press Enter to continue...")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM Books 
        WHERE title LIKE ? OR author LIKE ? OR genre LIKE ? OR isbn LIKE ? 
        ORDER BY title
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    books = cursor.fetchall()
    
    if not books:
        print(f"\nNo books found matching '{keyword}'")
        conn.close()
        input("Press Enter to continue...")
        return
    
    print(f"\nFound {len(books)} book(s) matching '{keyword}':")
    print(f"{'ID':<5} {'Title':<30} {'Author':<20} {'Type':<12} {'Status':<10}")
    print("-" * 80)
    for b in books:
        status = "Available" if b['available'] == 1 else "Borrowed"
        print(f"{b['book_id']:<5} {b['title'][:28]:<30} {b['author'][:18]:<20} {b['type']:<12} {status:<10}")
    
    conn.close()
    input("\nPress Enter to continue...")

# ==================== MAIN ====================
def main():
    """Main function"""
    # Initialize database
    initialize_database()
    
    # Display welcome message
    display_title("WELCOME TO LIBRARY BORROWING SYSTEM")
    print("A complete library management system with multiple user roles.")
    print()
    print("Default login credentials:")
    print("  Admin: admin@library.com / admin123")
    print("  Librarian: librarian@library.com / lib123")
    print("  Bank: bank@library.com / bank123")
    print()
    print("Students: Login with your name")
    print("Guests: No login required")
    print()
    input("Press Enter to continue...")
    
    # Start main menu
    home_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)