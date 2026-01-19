# database_setup.py
import sqlite3
import os
from datetime import datetime, timedelta

# Delete old database if exists
if os.path.exists('library.db'):
    os.remove('library.db')
    print("🗑️ Old database deleted")

# Create new database
conn = sqlite3.connect('library.db')
cursor = conn.cursor()

print("🔄 Creating database tables...")

# ===========================================
# 1. PATRON TABLE
# ===========================================
cursor.execute('''
CREATE TABLE Patron (
    patron_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('Admin','Librarian','Student','Guest','Bank')),
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    login_count INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1
)
''')

# ===========================================
# 2. BOOKS TABLE (UPDATED WITH NEW FIELDS)
# ===========================================
cursor.execute('''
CREATE TABLE Books (
    book_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT UNIQUE NOT NULL,
    published_year INTEGER,
    genre TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('Physical', 'E-book', 'Audiobook', 'Reference')),
    call_number TEXT NOT NULL,
    shelf_location TEXT,
    available INTEGER DEFAULT 1
)
''')

# ===========================================
# 3. TRANSACTIONS TABLE
# ===========================================
cursor.execute('''
CREATE TABLE Transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patron_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    borrow_date TEXT NOT NULL,
    return_date TEXT,
    fine REAL DEFAULT 0,
    item_type TEXT DEFAULT 'Physical',  -- Physical, E-book, Audiobook
    FOREIGN KEY (patron_id) REFERENCES Patron(patron_id),
    FOREIGN KEY (book_id) REFERENCES Books(book_id)
)
''')

# ===========================================
# 4. PAYMENTS TABLE
# ===========================================
cursor.execute('''
CREATE TABLE Payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patron_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    payment_date TEXT NOT NULL,
    purpose TEXT,
    FOREIGN KEY (patron_id) REFERENCES Patron(patron_id)
)
''')

# ===========================================
# 5. FEEDBACK TABLE
# ===========================================
cursor.execute('''
CREATE TABLE Feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patron_id INTEGER NULL,
    feedback_date TEXT NOT NULL,
    comment TEXT,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    FOREIGN KEY (patron_id) REFERENCES Patron(patron_id)
)
''')

conn.commit()
print("✅ Tables created successfully!")

# ===========================================
# INSERT SAMPLE DATA
# ===========================================
print("📥 Inserting sample data...")

# Get current date and calculate dates
current_date = datetime.now()
one_week_ago = current_date - timedelta(days=7)
two_weeks_ago = current_date - timedelta(days=14)
three_weeks_ago = current_date - timedelta(days=21)
one_month_ago = current_date - timedelta(days=30)
two_days_ago = current_date - timedelta(days=2)
one_day_ago = current_date - timedelta(days=1)

# Format dates
current_date_str = current_date.strftime('%Y-%m-%d')
one_week_ago_str = one_week_ago.strftime('%Y-%m-%d')
two_weeks_ago_str = two_weeks_ago.strftime('%Y-%m-%d')
three_weeks_ago_str = three_weeks_ago.strftime('%Y-%m-%d')
one_month_ago_str = one_month_ago.strftime('%Y-%m-%d')
two_days_ago_str = two_days_ago.strftime('%Y-%m-%d')
one_day_ago_str = one_day_ago.strftime('%Y-%m-%d')

# Sample Patrons - FIXED: No duplicate patron_id
patrons = [
    # Admins
    (202501, 'Admin Zen', 'Admin', 'admin@lib.com', 'admin123', 5, 1),
    (202502, 'Admin Suri', 'Admin', 'admin2@lib.com', 'admin456', 3, 1),
    
    # Librarians
    (202503, 'Librarian Ali', 'Librarian', 'librarian@lib.com', 'lib123', 10, 1),
    (202504, 'Librarian Jane', 'Librarian', 'librarian2@lib.com', 'lib456', 8, 1),
    
    # Students
    (202505, 'Hathimi', 'Student', 'student@edu.com', 'student123', 15, 1),
    (202506, 'Auliya', 'Student', 'student2@edu.com', 'student456', 12, 1),
    (202507, 'Qisya', 'Student', 'student3@edu.com', 'student789', 7, 1),
    (202508, 'Farish', 'Student', 'student4@edu.com', 'student000', 5, 1),
    
    # Guests
    (202509, 'Maya', 'Guest', 'guest@mail.com', 'guest123', 2, 1),
    (202510, 'David', 'Guest', 'guest2@mail.com', 'guest456', 1, 1),
    (202511, 'Lina', 'Guest', 'guest3@mail.com', 'guest789', 0, 1),

    # Bank
    (202512, 'Bank Officer', 'Bank', 'bank@lib.com', 'bank123', 6, 1),
    (202513, 'Bank Manager', 'Bank', 'bank2@lib.com', 'bank456', 4, 1),
]

cursor.executemany('''
INSERT INTO Patron (patron_id, name, role, email, password, login_count, is_active)
VALUES (?, ?, ?, ?, ?, ?, ?)
''', patrons)

# Sample Books with new fields (genre, type, call_number, shelf_location)
books = [
    # Format: (book_id, title, author, isbn, published_year, genre, type, call_number, shelf_location, available)
    (1, 'The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 1925, 'Classic', 'Physical', 'FIC FIT 001', 'Fiction A1', 1),
    (2, 'To Kill a Mockingbird', 'Harper Lee', '9780061120084', 1960, 'Classic', 'Physical', 'FIC LEE 002', 'Fiction A2', 1),
    (3, '1984', 'George Orwell', '9780451524935', 1949, 'Dystopian', 'Physical', 'FIC ORW 003', 'Fiction B1', 1),
    (4, 'Pride and Prejudice', 'Jane Austen', '9780141439518', 1813, 'Romance', 'Physical', 'FIC AUS 004', 'Fiction A3', 0),  # Borrowed by Hathimi
    (5, 'The Catcher in the Rye', 'J.D. Salinger', '9780316769488', 1951, 'Coming-of-age', 'Physical', 'FIC SAL 005', 'Fiction B2', 0),  # Borrowed by Auliya
    (6, 'The Hobbit', 'J.R.R. Tolkien', '9780547928227', 1937, 'Fantasy', 'Physical', 'FIC TOL 006', 'Fantasy C1', 0),  # Borrowed by Maya
    (7, 'Fahrenheit 451', 'Ray Bradbury', '9781451673319', 1953, 'Dystopian', 'E-book', 'E-FIC BRA 007', 'Digital', 1),
    (8, 'Moby Dick', 'Herman Melville', '9781503280786', 1851, 'Adventure', 'Audiobook', 'AUD FIC MEL 008', 'Audio Section', 0),  # Borrowed by Lina
    (9, 'Python Programming', 'John Smith', '9780134444321', 2023, 'Technology', 'Physical', '005.133 PYTHON 009', 'Computer Science D1', 1),
    (10, 'Database Systems', 'Maria Garcia', '9780133970777', 2022, 'Technology', 'Physical', '005.74 SQL 010', 'Computer Science D2', 1),
    (11, 'The Silent Patient', 'Alex Michaelides', '9781250301697', 2019, 'Thriller', 'Physical', 'FIC MIC 011', 'Mystery E1', 1),
    (12, 'Becoming', 'Michelle Obama', '9781524763138', 2018, 'Biography', 'Physical', 'B OBA 012', 'Biography F1', 1),
    (13, 'Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', '9780062316097', 2015, 'History', 'Reference', 'REF 909 HAR 013', 'Reference G1', 1),
    (14, 'The Alchemist', 'Paulo Coelho', '9780062315007', 1988, 'Fiction', 'Physical', 'FIC COE 014', 'Fiction A4', 1),
    (15, 'Atomic Habits', 'James Clear', '9780735211292', 2018, 'Self-help', 'E-book', 'E-158.1 CLE 015', 'Digital', 0),  # Borrowed by Farish
    (16, 'Educated', 'Tara Westover', '9780399590504', 2018, 'Memoir', 'Physical', 'B WES 016', 'Biography F2', 1),
    (17, 'The Lord of the Rings', 'J.R.R. Tolkien', '9780544003415', 1954, 'Fantasy', 'Physical', 'FIC TOL 017', 'Fantasy C2', 1),
    (18, 'Thinking, Fast and Slow', 'Daniel Kahneman', '9780374533557', 2011, 'Psychology', 'Reference', 'REF 153.4 KAH 018', 'Reference G2', 1),
    (19, 'The Hunger Games', 'Suzanne Collins', '9780439023481', 2008, 'Young Adult', 'Physical', 'YA FIC COL 019', 'Young Adult H1', 1),
    (20, 'Clean Code', 'Robert C. Martin', '9780132350884', 2008, 'Technology', 'Physical', '005.1 MAR 020', 'Computer Science D3', 1),
]

cursor.executemany('''
INSERT INTO Books (book_id, title, author, isbn, published_year, genre, type, call_number, shelf_location, available)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', books)

# Sample Transactions - UPDATED WITH CURRENT DATES AND REDUCED FINES
# Hanya 3 orang yang belum return
transactions = [
    # Format: (patron_id, book_id, borrow_date, return_date, fine, item_type)
    # ======================================
    # Transaction dengan return (SUDAH DIKEMBALIKAN)
    # ======================================
    (202505, 1, one_month_ago_str, two_weeks_ago_str, 0.00, 'Physical'),  # Hathimi - returned
    (202506, 3, three_weeks_ago_str, two_weeks_ago_str, 0.00, 'Physical'),  # Auliya - returned
    (202507, 7, one_week_ago_str, two_days_ago_str, 0.00, 'E-book'),  # Qisya - returned (ebook, no fine)
    (202510, 10, two_weeks_ago_str, one_week_ago_str, 0.00, 'Physical'),  # David - returned
    (202509, 2, two_weeks_ago_str, one_week_ago_str, 0.00, 'Physical'),  # Maya - returned another book
    
    # ======================================
    # Transaction TANPA return (BELUM DIKEMBALIKAN) - HANYA 3 ORANG
    # ======================================
    # 1. Hathimi - borrowed 3 weeks ago (fine RM 7.00)
    (202505, 4, three_weeks_ago_str, None, 7.00, 'Physical'),  # Hathimi - belum return
    
    # 2. Auliya - borrowed 16 days ago (fine RM 2.00)
    (202506, 5, (current_date - timedelta(days=16)).strftime('%Y-%m-%d'), None, 2.00, 'Physical'),  # Auliya - belum return
    
    # 3. Maya - borrowed 20 days ago (fine RM 6.00)
    (202509, 6, (current_date - timedelta(days=20)).strftime('%Y-%m-%d'), None, 6.00, 'Physical'),  # Maya - belum return
    
    # ======================================
    # Transaction lain dengan return
    # ======================================
    (202511, 8, one_week_ago_str, two_days_ago_str, 0.00, 'Audiobook'),  # Lina - returned (audiobook)
    (202508, 15, two_days_ago_str, one_day_ago_str, 0.00, 'E-book'),  # Farish - returned
]

cursor.executemany('''
INSERT INTO Transactions (patron_id, book_id, borrow_date, return_date, fine, item_type)
VALUES (?, ?, ?, ?, ?, ?)
''', transactions)

# Sample Payments - UPDATED WITH REDUCED AMOUNTS
payments = [
    # Small fines for the 3 people who haven't returned yet
    (202505, 3.50, one_week_ago_str, 'Partial Fine Payment'),  # Hathimi - partial payment
    (202506, 1.00, two_days_ago_str, 'Fine Payment'),  # Auliya - small payment
    (202509, 3.00, one_week_ago_str, 'Fine Payment'),  # Maya - partial payment
    
    # Other payments
    (202505, 25.00, one_month_ago_str, 'Membership Fee'),
    (202506, 25.00, one_month_ago_str, 'Membership Fee'),
    (202507, 25.00, two_weeks_ago_str, 'Membership Fee'),
    (202505, 15.99, two_weeks_ago_str, 'Book Purchase'),
    (202506, 12.50, one_week_ago_str, 'Book Purchase'),
    (202511, 5.00, two_days_ago_str, 'Audiobook Access'),
    (202508, 4.99, one_day_ago_str, 'E-book Access'),
]

cursor.executemany('''
INSERT INTO Payments (patron_id, amount, payment_date, purpose)
VALUES (?, ?, ?, ?)
''', payments)

# Sample Feedbacks - Updated with current dates
feedback_dates = [
    (current_date - timedelta(days=5)).strftime('%Y-%m-%d'),
    (current_date - timedelta(days=4)).strftime('%Y-%m-%d'),
    (current_date - timedelta(days=3)).strftime('%Y-%m-%d'),
    (current_date - timedelta(days=2)).strftime('%Y-%m-%d'),
    current_date.strftime('%Y-%m-%d'),
    (current_date - timedelta(days=1)).strftime('%Y-%m-%d'),
    (current_date - timedelta(days=6)).strftime('%Y-%m-%d'),
]

feedbacks = [
    (202505, feedback_dates[0], 'Great book selection and helpful staff!', 5),
    (202506, feedback_dates[1], 'System is easy to use but could be faster.', 4),
    (202507, feedback_dates[2], 'Had trouble logging in, but support was responsive.', 3),
    (202508, feedback_dates[3], 'Love the cozy reading area!', 5),
    (202509, feedback_dates[4], 'Found some outdated books, please update.', 2),
    (202510, feedback_dates[5], 'Payment process was smooth and secure.', 5),
    (202511, feedback_dates[6], 'Appreciate the financial transparency.', 4),
    (202512, feedback_dates[0], 'Bank services are efficient.', 5),
    (202513, feedback_dates[1], 'Good financial management system.', 4),
    (202505, feedback_dates[2], 'The new genre categories are helpful for finding books!', 5),
    (202506, feedback_dates[3], 'Call numbers make it easy to locate books on shelves.', 4),
]

cursor.executemany('''
INSERT INTO Feedback (patron_id, feedback_date, comment, rating)
VALUES (?, ?, ?, ?)
''', feedbacks)

conn.commit()
conn.close()

print(f"✅ Inserted {len(patrons)} patrons, {len(books)} books, {len(transactions)} transactions, {len(payments)} payments, {len(feedbacks)} feedbacks")
print("🎉 Database created successfully: library.db")
print("\n📊 DATABASE SUMMARY:")
print("=====================")
print(f"📚 Total Books: {len(books)}")
print(f"👥 Total Patrons: {len(patrons)}")
print(f"📋 Total Transactions: {len(transactions)}")
print(f"💰 Total Payments: {len(payments)}")
print(f"💬 Total Feedbacks: {len(feedbacks)}")
print("\n📖 BORROWING STATUS:")
print("=====================")
print("✅ 7 transactions have been returned")
print("❌ 3 transactions NOT returned yet:")
print("   - Hathimi: Borrowed Pride and Prejudice 3 weeks ago (Fine: RM 7.00)")
print("   - Auliya: Borrowed The Catcher in the Rye 16 days ago (Fine: RM 2.00)")
print("   - Maya: Borrowed The Hobbit 20 days ago (Fine: RM 6.00)")
print("\n💰 FINE SUMMARY:")
print("================")
print("Total outstanding fines: RM 15.00")
print("Total fines paid: RM 7.50")
print("\n📅 DATES USED:")
print("==============")
print(f"Current Date: {current_date_str}")
print(f"One Week Ago: {one_week_ago_str}")
print(f"Two Weeks Ago: {two_weeks_ago_str}")
print(f"Three Weeks Ago: {three_weeks_ago_str}")
print(f"One Month Ago: {one_month_ago_str}")


print(f"✅ Inserted {len(patrons)} patrons, {len(books)} books, {len(transactions)} transactions, {len(payments)} payments, {len(feedbacks)} feedbacks")
print("🎉 Database created successfully: library.db")