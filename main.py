# main.py
import sqlite3
import os
import sys
from datetime import datetime

# === VISUAL STYLES ===
class Color:
    HEADER = '\033[95m'; BLUE = '\033[94m'; CYAN = '\033[96m'
    GREEN = '\033[92m'; YELLOW = '\033[93m'; RED = '\033[91m'
    BOLD = '\033[1m'; END = '\033[0m'

def get_db():
    db_path = os.path.join(os.path.dirname(__file__), 'library.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def draw_header(title, color=Color.HEADER):
    print(f"{Color.BOLD}{color}{'='*125}")
    print(f"{title.center(125)}")
    print(f"{'='*125}{Color.END}")

# --- BOOK DISPLAY FUNCTION (ANTI-CRASH) ---
def display_books_full(rows):
    if not rows:
        print(f"\n{Color.RED}⚠ No records found in the library.{Color.END}")
        return
    print(f"{Color.BOLD}{'ID':<4} | {'Title':<25} | {'Genre':<12} | {'Year':<6} | {'Type':<10} | {'Call Number':<18} | {'Status'}{Color.END}")
    print("-" * 125)
    for b in rows:
        status = f"{Color.GREEN}Available{Color.END}" if b['available'] else f"{Color.RED}Borrowed{Color.END}"
        
        # Handle None values to prevent formatting errors
        bid = str(b['book_id'] if b['book_id'] is not None else "")
        title = str(b['title'] if b['title'] is not None else "")[:25]
        genre = str(b['genre'] if b['genre'] is not None else "")
        year = str(b['published_year'] if b['published_year'] is not None else "")
        btype = str(b['type'] if b['type'] is not None else "")
        call = str(b['call_number'] if b['call_number'] is not None else "")
        
        print(f"{bid:<4} | {title:<25} | {genre:<12} | {year:<6} | {btype:<10} | {call:<18} | {status}")

# --- PATRON DISPLAY FUNCTION ---
def display_patrons_full(rows):
    if not rows:
        print(f"\n{Color.RED}⚠ No patrons found.{Color.END}")
        return
    print(f"{Color.BOLD}{'ID':<8} | {'Name':<20} | {'Role':<12} | {'Email':<25} | {'Status'}{Color.END}")
    print("-" * 125)
    for p in rows:
        status = f"{Color.GREEN}Active{Color.END}" if p['is_active'] else f"{Color.RED}Inactive{Color.END}"
        pid = str(p['patron_id'] if p['patron_id'] is not None else "")
        name = str(p['name'] if p['name'] is not None else "")[:20]
        role = str(p['role'] if p['role'] is not None else "")
        email = str(p['email'] if p['email'] is not None else "")[:25]
        
        print(f"{pid:<8} | {name:<20} | {role:<12} | {email:<25} | {status}")

# --- TRANSACTION DISPLAY FUNCTION ---
def display_transactions_full(rows):
    if not rows:
        print(f"\n{Color.RED}⚠ No transactions found.{Color.END}")
        return
    print(f"{Color.BOLD}{'ID':<4} | {'Patron ID':<8} | {'Book ID':<7} | {'Borrow Date':<12} | {'Return Date':<12} | {'Fine':<8} | {'Status'}{Color.END}")
    print("-" * 125)
    for t in rows:
        status = f"{Color.RED}Borrowed{Color.END}" if t['return_date'] is None else f"{Color.GREEN}Returned{Color.END}"
        tid = str(t['transaction_id'] if t['transaction_id'] is not None else "")
        pid = str(t['patron_id'] if t['patron_id'] is not None else "")
        bid = str(t['book_id'] if t['book_id'] is not None else "")
        borrow = str(t['borrow_date'] if t['borrow_date'] is not None else "")
        ret = str(t['return_date'] if t['return_date'] is not None else "Not Yet")
        fine = f"RM {float(t['fine'] or 0):.2f}"
        
        print(f"{tid:<4} | {pid:<8} | {bid:<7} | {borrow:<12} | {ret:<12} | {fine:<8} | {status}")

# --- PAYMENT DISPLAY FUNCTION ---
def display_payments_full(rows):
    if not rows:
        print(f"\n{Color.RED}⚠ No payments found.{Color.END}")
        return
    print(f"{Color.BOLD}{'ID':<4} | {'Patron ID':<8} | {'Amount':<10} | {'Date':<12} | {'Purpose'}{Color.END}")
    print("-" * 125)
    for p in rows:
        pid = str(p['payment_id'] if p['payment_id'] is not None else "")
        patron = str(p['patron_id'] if p['patron_id'] is not None else "")
        amount = f"RM {float(p['amount'] or 0):.2f}"
        date = str(p['payment_date'] if p['payment_date'] is not None else "")
        purpose = str(p['purpose'] if p['purpose'] is not None else "")[:30]
        
        print(f"{pid:<4} | {patron:<8} | {amount:<10} | {date:<12} | {purpose}")

# --- FEEDBACK DISPLAY FUNCTION ---
def display_feedbacks_full(rows):
    if not rows:
        print(f"\n{Color.RED}⚠ No feedbacks found.{Color.END}")
        return
    print(f"{Color.BOLD}{'ID':<4} | {'Patron ID':<8} | {'Date':<12} | {'Rating':<6} | {'Comment'}{Color.END}")
    print("-" * 125)
    for f in rows:
        fid = str(f['feedback_id'] if f['feedback_id'] is not None else "")
        pid = str(f['patron_id'] if f['patron_id'] is not None else "Anonymous")
        date = str(f['feedback_date'] if f['feedback_date'] is not None else "")
        rating = "⭐" * int(f['rating']) if f['rating'] else "No rating"
        comment = str(f['comment'] if f['comment'] is not None else "")[:40]
        
        print(f"{fid:<4} | {pid:<8} | {date:<12} | {rating:<6} | {comment}")

# ==================== LOGIN SYSTEM ====================
def login_portal(role):
    clear()
    draw_header(f"🔑 {role.upper()} PORTAL LOGIN", Color.YELLOW)
    email = input("Email: ").strip()
    password = input("Password: ").strip()
    conn = get_db()
    user = conn.execute("SELECT * FROM Patron WHERE email=? AND password=? AND role=?", (email, password, role)).fetchone()
    conn.close()
    if user:
        print(f"\n{Color.GREEN}✔ SUCCESS: Welcome, {user['name']}.{Color.END}")
        input("Press Enter to continue..."); return user
    print(f"\n{Color.RED}✘ FAILED: Invalid credentials.{Color.END}")
    input("Press Enter to try again..."); return None

# ==================== 1. ADMIN PORTAL (FULL CRUD) ====================
def menu_admin():
    user = login_portal("Admin")
    if not user: return
    while True:
        clear(); draw_header("🛡️ ADMIN CONTROL PANEL", Color.RED)
        print(f"{Color.CYAN}Welcome, {user['name']} (Admin){Color.END}\n")
        print("1. PATRON MANAGEMENT (CRUD)    2. TRANSACTION MANAGEMENT (CRUD)")
        print("3. VIEW ALL BOOKS               4. FEEDBACK MANAGEMENT (CRUD)")
        print("5. PAYMENT MANAGEMENT (CRUD)    6. SYSTEM STATISTICS")
        print("7. Logout")
        choice = input(f"\n{Color.YELLOW}Select Menu: {Color.END}")
        conn = get_db()
        
        if choice == '1': # Patron CRUD
            while True:
                clear(); draw_header("👥 PATRON MANAGEMENT", Color.RED)
                print("1. View All Patrons    2. Add New Patron    3. Update Patron")
                print("4. Delete Patron       5. Search Patron      6. Back")
                sub = input(f"{Color.YELLOW}> {Color.END}")
                
                if sub == '1':
                    rows = conn.execute("SELECT * FROM Patron ORDER BY patron_id").fetchall()
                    display_patrons_full(rows)
                    
                elif sub == '2':
                    print(f"\n{Color.CYAN}--- ADD NEW PATRON ---{Color.END}")
                    try:
                        pid = input("Patron ID: ").strip()
                        name = input("Name: ").strip()
                        email = input("Email: ").strip()
                        password = input("Password: ").strip()
                        role = input("Role (Admin/Librarian/Student/Guest/Bank): ").strip().capitalize()
                        
                        if role not in ['Admin', 'Librarian', 'Student', 'Guest', 'Bank']:
                            print(f"{Color.RED}Invalid role!{Color.END}")
                        else:
                            conn.execute("""
                                INSERT INTO Patron (patron_id, name, email, password, role, login_count, is_active) 
                                VALUES (?, ?, ?, ?, ?, 0, 1)
                            """, (pid, name, email, password, role))
                            conn.commit()
                            print(f"{Color.GREEN}✅ Patron added successfully.{Color.END}")
                    except Exception as e:
                        print(f"{Color.RED}❌ FAILED: {str(e)}{Color.END}")
                        
                elif sub == '3':
                    print(f"\n{Color.CYAN}--- UPDATE PATRON ---{Color.END}")
                    pid = input("Patron ID to update: ").strip()
                    patron = conn.execute("SELECT * FROM Patron WHERE patron_id=?", (pid,)).fetchone()
                    
                    if not patron:
                        print(f"{Color.RED}Patron not found!{Color.END}")
                    else:
                        print(f"\nCurrent Info: {patron['name']} - {patron['email']} - {patron['role']}")
                        name = input(f"New Name [{patron['name']}]: ").strip() or patron['name']
                        email = input(f"New Email [{patron['email']}]: ").strip() or patron['email']
                        role = input(f"New Role [{patron['role']}]: ").strip().capitalize() or patron['role']
                        active = input("Active? (1=Yes, 0=No) [1]: ").strip() or "1"
                        
                        conn.execute("""
                            UPDATE Patron SET name=?, email=?, role=?, is_active=? WHERE patron_id=?
                        """, (name, email, role, int(active), pid))
                        conn.commit()
                        print(f"{Color.GREEN}✅ Patron updated successfully.{Color.END}")
                        
                elif sub == '4':
                    print(f"\n{Color.RED}--- DELETE PATRON ---{Color.END}")
                    pid = input("Patron ID to delete: ").strip()
                    confirm = input(f"Are you sure? (y/n): ").strip().lower()
                    
                    if confirm == 'y':
                        try:
                            conn.execute("DELETE FROM Patron WHERE patron_id=?", (pid,))
                            conn.commit()
                            print(f"{Color.GREEN}✅ Patron deleted successfully.{Color.END}")
                        except Exception as e:
                            print(f"{Color.RED}❌ Failed: {str(e)}{Color.END}")
                            
                elif sub == '5':
                    keyword = input("Search by name or email: ").strip()
                    rows = conn.execute("""
                        SELECT * FROM Patron 
                        WHERE name LIKE ? OR email LIKE ? 
                        ORDER BY patron_id
                    """, (f"%{keyword}%", f"%{keyword}%")).fetchall()
                    display_patrons_full(rows)
                    
                elif sub == '6':
                    break
                    
                input(f"\n{Color.CYAN}Press Enter to continue...{Color.END}")
                
        elif choice == '2': # Transaction CRUD
            while True:
                clear(); draw_header("📋 TRANSACTION MANAGEMENT", Color.RED)
                print("1. View All Transactions    2. Add New Transaction")
                print("3. Update Transaction       4. Delete Transaction")
                print("5. Search Transactions      6. View Borrowed Books")
                print("7. Return Book              8. Back")
                sub = input(f"{Color.YELLOW}> {Color.END}")
                
                if sub == '1':
                    rows = conn.execute("SELECT * FROM Transactions ORDER BY transaction_id DESC").fetchall()
                    display_transactions_full(rows)
                    
                elif sub == '2':
                    print(f"\n{Color.CYAN}--- ADD NEW TRANSACTION ---{Color.END}")
                    try:
                        patron_id = input("Patron ID: ").strip()
                        book_id = input("Book ID: ").strip()
                        borrow_date = input("Borrow Date (YYYY-MM-DD): ").strip()
                        return_date = input("Return Date (YYYY-MM-DD) or Enter for none: ").strip() or None
                        fine = input("Fine amount (0.00): ").strip() or "0.00"
                        item_type = input("Item Type (Physical/E-book/Audiobook) [Physical]: ").strip() or "Physical"
                        
                        # Check if patron exists
                        patron = conn.execute("SELECT * FROM Patron WHERE patron_id=?", (patron_id,)).fetchone()
                        if not patron:
                            print(f"{Color.RED}Patron ID not found!{Color.END}")
                            continue
                            
                        # Check if book exists
                        book = conn.execute("SELECT * FROM Books WHERE book_id=?", (book_id,)).fetchone()
                        if not book:
                            print(f"{Color.RED}Book ID not found!{Color.END}")
                            continue
                            
                        conn.execute("""
                            INSERT INTO Transactions (patron_id, book_id, borrow_date, return_date, fine, item_type) 
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (patron_id, book_id, borrow_date, return_date, float(fine), item_type))
                        
                        # Update book availability if physical
                        if item_type == 'Physical' and return_date is None:
                            conn.execute("UPDATE Books SET available=0 WHERE book_id=?", (book_id,))
                            
                        conn.commit()
                        print(f"{Color.GREEN}✅ Transaction added successfully.{Color.END}")
                        
                    except Exception as e:
                        print(f"{Color.RED}❌ FAILED: {str(e)}{Color.END}")
                        
                elif sub == '3':
                    print(f"\n{Color.CYAN}--- UPDATE TRANSACTION ---{Color.END}")
                    tid = input("Transaction ID to update: ").strip()
                    txn = conn.execute("SELECT * FROM Transactions WHERE transaction_id=?", (tid,)).fetchone()
                    
                    if not txn:
                        print(f"{Color.RED}Transaction not found!{Color.END}")
                    else:
                        print(f"\nCurrent: Patron:{txn['patron_id']} Book:{txn['book_id']} Borrow:{txn['borrow_date']}")
                        return_date = input(f"Return Date [{txn['return_date'] or 'Not returned'}]: ").strip() or txn['return_date']
                        fine = input(f"Fine [{txn['fine']}]: ").strip() or str(txn['fine'])
                        
                        conn.execute("""
                            UPDATE Transactions SET return_date=?, fine=? WHERE transaction_id=?
                        """, (return_date if return_date else None, float(fine), tid))
                        
                        # Update book availability
                        if txn['item_type'] == 'Physical':
                            if return_date and not txn['return_date']:
                                conn.execute("UPDATE Books SET available=1 WHERE book_id=?", (txn['book_id'],))
                            elif not return_date and txn['return_date']:
                                conn.execute("UPDATE Books SET available=0 WHERE book_id=?", (txn['book_id'],))
                                
                        conn.commit()
                        print(f"{Color.GREEN}✅ Transaction updated successfully.{Color.END}")
                        
                elif sub == '4':
                    print(f"\n{Color.RED}--- DELETE TRANSACTION ---{Color.END}")
                    tid = input("Transaction ID to delete: ").strip()
                    confirm = input(f"Are you sure? (y/n): ").strip().lower()
                    
                    if confirm == 'y':
                        try:
                            conn.execute("DELETE FROM Transactions WHERE transaction_id=?", (tid,))
                            conn.commit()
                            print(f"{Color.GREEN}✅ Transaction deleted successfully.{Color.END}")
                        except Exception as e:
                            print(f"{Color.RED}❌ Failed: {str(e)}{Color.END}")
                            
                elif sub == '5':
                    keyword = input("Search by patron ID or book ID: ").strip()
                    rows = conn.execute("""
                        SELECT * FROM Transactions 
                        WHERE patron_id LIKE ? OR book_id LIKE ? 
                        ORDER BY transaction_id DESC
                    """, (f"%{keyword}%", f"%{keyword}%")).fetchall()
                    display_transactions_full(rows)
                    
                elif sub == '6':
                    rows = conn.execute("""
                        SELECT t.*, b.title, p.name 
                        FROM Transactions t 
                        JOIN Books b ON t.book_id = b.book_id 
                        JOIN Patron p ON t.patron_id = p.patron_id 
                        WHERE t.return_date IS NULL 
                        ORDER BY t.borrow_date DESC
                    """).fetchall()
                    
                    if rows:
                        print(f"\n{Color.CYAN}--- CURRENTLY BORROWED BOOKS ---{Color.END}")
                        print(f"{Color.BOLD}{'Transaction':<10} | {'Patron':<20} | {'Book':<25} | {'Borrow Date':<12}{Color.END}")
                        print("-" * 125)
                        for r in rows:
                            print(f"{r['transaction_id']:<10} | {r['name']:<20} | {r['title'][:25]:<25} | {r['borrow_date']:<12}")
                    else:
                        print(f"{Color.YELLOW}No books currently borrowed.{Color.END}")
                        
                elif sub == '7':
                    print(f"\n{Color.CYAN}--- RETURN BOOK ---{Color.END}")
                    book_id = input("Book ID to return: ").strip()
                    
                    # Find active transaction for this book
                    txn = conn.execute("""
                        SELECT * FROM Transactions 
                        WHERE book_id=? AND return_date IS NULL 
                        ORDER BY transaction_id DESC LIMIT 1
                    """, (book_id,)).fetchone()
                    
                    if not txn:
                        print(f"{Color.RED}No active borrow record found for this book!{Color.END}")
                    else:
                        return_date = input(f"Return Date (YYYY-MM-DD) [{datetime.now().strftime('%Y-%m-%d')}]: ").strip() or datetime.now().strftime('%Y-%m-%d')
                        fine = input(f"Fine amount: ").strip() or str(txn['fine'])
                        
                        conn.execute("""
                            UPDATE Transactions SET return_date=?, fine=? 
                            WHERE transaction_id=?
                        """, (return_date, float(fine), txn['transaction_id']))
                        
                        # Update book availability
                        if txn['item_type'] == 'Physical':
                            conn.execute("UPDATE Books SET available=1 WHERE book_id=?", (book_id,))
                            
                        conn.commit()
                        print(f"{Color.GREEN}✅ Book returned successfully.{Color.END}")
                        
                elif sub == '8':
                    break
                    
                input(f"\n{Color.CYAN}Press Enter to continue...{Color.END}")
                
        elif choice == '3': # View Books
            clear(); draw_header("📚 ALL BOOKS IN LIBRARY", Color.BLUE)
            rows = conn.execute("SELECT * FROM Books ORDER BY book_id").fetchall()
            display_books_full(rows)
            input(f"\n{Color.CYAN}Press Enter to continue...{Color.END}")
            
        elif choice == '4': # Feedback CRUD
            while True:
                clear(); draw_header("💬 FEEDBACK MANAGEMENT", Color.RED)
                print("1. View All Feedbacks    2. Add New Feedback")
                print("3. Update Feedback       4. Delete Feedback")
                print("5. Search Feedbacks      6. Back")
                sub = input(f"{Color.YELLOW}> {Color.END}")
                
                if sub == '1':
                    rows = conn.execute("""
                        SELECT f.*, p.name 
                        FROM Feedback f 
                        LEFT JOIN Patron p ON f.patron_id = p.patron_id 
                        ORDER BY f.feedback_date DESC
                    """).fetchall()
                    
                    if rows:
                        print(f"\n{Color.BOLD}{'ID':<4} | {'Patron':<20} | {'Date':<12} | {'Rating':<6} | {'Comment'}{Color.END}")
                        print("-" * 125)
                        for f in rows:
                            patron = f['name'] if f['name'] else "Anonymous"
                            rating = "⭐" * int(f['rating']) if f['rating'] else "No rating"
                            comment = str(f['comment'] if f['comment'] else "")[:40]
                            print(f"{f['feedback_id']:<4} | {patron:<20} | {f['feedback_date']:<12} | {rating:<6} | {comment}")
                    else:
                        print(f"{Color.YELLOW}No feedbacks found.{Color.END}")
                        
                elif sub == '2':
                    print(f"\n{Color.CYAN}--- ADD NEW FEEDBACK ---{Color.END}")
                    try:
                        patron_id = input("Patron ID (or Enter for anonymous): ").strip() or None
                        feedback_date = input("Feedback Date (YYYY-MM-DD): ").strip()
                        comment = input("Comment: ").strip()
                        rating = input("Rating (1-5): ").strip()
                        
                        if patron_id:
                            # Check if patron exists
                            patron = conn.execute("SELECT * FROM Patron WHERE patron_id=?", (patron_id,)).fetchone()
                            if not patron:
                                print(f"{Color.RED}Patron ID not found! Saving as anonymous.{Color.END}")
                                patron_id = None
                                
                        conn.execute("""
                            INSERT INTO Feedback (patron_id, feedback_date, comment, rating) 
                            VALUES (?, ?, ?, ?)
                        """, (patron_id, feedback_date, comment, int(rating)))
                        conn.commit()
                        print(f"{Color.GREEN}✅ Feedback added successfully.{Color.END}")
                        
                    except Exception as e:
                        print(f"{Color.RED}❌ FAILED: {str(e)}{Color.END}")
                        
                elif sub == '3':
                    print(f"\n{Color.CYAN}--- UPDATE FEEDBACK ---{Color.END}")
                    fid = input("Feedback ID to update: ").strip()
                    fb = conn.execute("SELECT * FROM Feedback WHERE feedback_id=?", (fid,)).fetchone()
                    
                    if not fb:
                        print(f"{Color.RED}Feedback not found!{Color.END}")
                    else:
                        comment = input(f"New Comment [{fb['comment']}]: ").strip() or fb['comment']
                        rating = input(f"New Rating (1-5) [{fb['rating']}]: ").strip() or str(fb['rating'])
                        
                        conn.execute("""
                            UPDATE Feedback SET comment=?, rating=? WHERE feedback_id=?
                        """, (comment, int(rating), fid))
                        conn.commit()
                        print(f"{Color.GREEN}✅ Feedback updated successfully.{Color.END}")
                        
                elif sub == '4':
                    print(f"\n{Color.RED}--- DELETE FEEDBACK ---{Color.END}")
                    fid = input("Feedback ID to delete: ").strip()
                    confirm = input(f"Are you sure? (y/n): ").strip().lower()
                    
                    if confirm == 'y':
                        try:
                            conn.execute("DELETE FROM Feedback WHERE feedback_id=?", (fid,))
                            conn.commit()
                            print(f"{Color.GREEN}✅ Feedback deleted successfully.{Color.END}")
                        except Exception as e:
                            print(f"{Color.RED}❌ Failed: {str(e)}{Color.END}")
                            
                elif sub == '5':
                    keyword = input("Search comment text: ").strip()
                    rows = conn.execute("""
                        SELECT f.*, p.name 
                        FROM Feedback f 
                        LEFT JOIN Patron p ON f.patron_id = p.patron_id 
                        WHERE f.comment LIKE ? 
                        ORDER BY f.feedback_date DESC
                    """, (f"%{keyword}%",)).fetchall()
                    
                    if rows:
                        print(f"\n{Color.BOLD}{'ID':<4} | {'Patron':<20} | {'Date':<12} | {'Rating':<6} | {'Comment'}{Color.END}")
                        print("-" * 125)
                        for f in rows:
                            patron = f['name'] if f['name'] else "Anonymous"
                            rating = "⭐" * int(f['rating']) if f['rating'] else "No rating"
                            comment = str(f['comment'] if f['comment'] else "")[:40]
                            print(f"{f['feedback_id']:<4} | {patron:<20} | {f['feedback_date']:<12} | {rating:<6} | {comment}")
                    else:
                        print(f"{Color.YELLOW}No feedbacks found.{Color.END}")
                        
                elif sub == '6':
                    break
                    
                input(f"\n{Color.CYAN}Press Enter to continue...{Color.END}")
                
        elif choice == '5': # Payment CRUD
            while True:
                clear(); draw_header("💰 PAYMENT MANAGEMENT", Color.RED)
                print("1. View All Payments    2. Add New Payment")
                print("3. Update Payment       4. Delete Payment")
                print("5. Search Payments      6. View Payment Summary")
                print("7. Back")
                sub = input(f"{Color.YELLOW}> {Color.END}")
                
                if sub == '1':
                    rows = conn.execute("SELECT * FROM Payments ORDER BY payment_date DESC").fetchall()
                    display_payments_full(rows)
                    
                elif sub == '2':
                    print(f"\n{Color.CYAN}--- ADD NEW PAYMENT ---{Color.END}")
                    try:
                        patron_id = input("Patron ID: ").strip()
                        amount = input("Amount: ").strip()
                        payment_date = input("Payment Date (YYYY-MM-DD): ").strip()
                        purpose = input("Purpose: ").strip()
                        
                        # Check if patron exists
                        patron = conn.execute("SELECT * FROM Patron WHERE patron_id=?", (patron_id,)).fetchone()
                        if not patron:
                            print(f"{Color.RED}Patron ID not found!{Color.END}")
                            continue
                            
                        conn.execute("""
                            INSERT INTO Payments (patron_id, amount, payment_date, purpose) 
                            VALUES (?, ?, ?, ?)
                        """, (patron_id, float(amount), payment_date, purpose))
                        conn.commit()
                        print(f"{Color.GREEN}✅ Payment added successfully.{Color.END}")
                        
                    except Exception as e:
                        print(f"{Color.RED}❌ FAILED: {str(e)}{Color.END}")
                        
                elif sub == '3':
                    print(f"\n{Color.CYAN}--- UPDATE PAYMENT ---{Color.END}")
                    pid = input("Payment ID to update: ").strip()
                    pay = conn.execute("SELECT * FROM Payments WHERE payment_id=?", (pid,)).fetchone()
                    
                    if not pay:
                        print(f"{Color.RED}Payment not found!{Color.END}")
                    else:
                        amount = input(f"New Amount [{pay['amount']}]: ").strip() or str(pay['amount'])
                        payment_date = input(f"New Date [{pay['payment_date']}]: ").strip() or pay['payment_date']
                        purpose = input(f"New Purpose [{pay['purpose']}]: ").strip() or pay['purpose']
                        
                        conn.execute("""
                            UPDATE Payments SET amount=?, payment_date=?, purpose=? WHERE payment_id=?
                        """, (float(amount), payment_date, purpose, pid))
                        conn.commit()
                        print(f"{Color.GREEN}✅ Payment updated successfully.{Color.END}")
                        
                elif sub == '4':
                    print(f"\n{Color.RED}--- DELETE PAYMENT ---{Color.END}")
                    pid = input("Payment ID to delete: ").strip()
                    confirm = input(f"Are you sure? (y/n): ").strip().lower()
                    
                    if confirm == 'y':
                        try:
                            conn.execute("DELETE FROM Payments WHERE payment_id=?", (pid,))
                            conn.commit()
                            print(f"{Color.GREEN}✅ Payment deleted successfully.{Color.END}")
                        except Exception as e:
                            print(f"{Color.RED}❌ Failed: {str(e)}{Color.END}")
                            
                elif sub == '5':
                    keyword = input("Search by patron ID or purpose: ").strip()
                    rows = conn.execute("""
                        SELECT * FROM Payments 
                        WHERE patron_id LIKE ? OR purpose LIKE ? 
                        ORDER BY payment_date DESC
                    """, (f"%{keyword}%", f"%{keyword}%")).fetchall()
                    display_payments_full(rows)
                    
                elif sub == '6':
                    print(f"\n{Color.CYAN}--- PAYMENT SUMMARY ---{Color.END}")
                    total = conn.execute("SELECT SUM(amount) as total FROM Payments").fetchone()['total'] or 0
                    count = conn.execute("SELECT COUNT(*) as count FROM Payments").fetchone()['count'] or 0
                    avg = conn.execute("SELECT AVG(amount) as avg FROM Payments").fetchone()['avg'] or 0
                    
                    print(f"Total Payments: {count}")
                    print(f"Total Amount: RM {total:.2f}")
                    print(f"Average Payment: RM {avg:.2f}")
                    
                    # Top patrons by payment
                    print(f"\n{Color.YELLOW}Top Patrons by Payment:{Color.END}")
                    rows = conn.execute("""
                        SELECT p.patron_id, p.name, SUM(pm.amount) as total_paid 
                        FROM Payments pm 
                        JOIN Patron p ON pm.patron_id = p.patron_id 
                        GROUP BY p.patron_id 
                        ORDER BY total_paid DESC 
                        LIMIT 5
                    """).fetchall()
                    
                    if rows:
                        for i, r in enumerate(rows, 1):
                            print(f"{i}. {r['name']} (ID: {r['patron_id']}) - RM {r['total_paid']:.2f}")
                    else:
                        print("No payment data available")
                        
                elif sub == '7':
                    break
                    
                input(f"\n{Color.CYAN}Press Enter to continue...{Color.END}")
                
        elif choice == '6': # System Statistics
            clear(); draw_header("📊 SYSTEM STATISTICS", Color.BLUE)
            
            # Basic stats
            total_patrons = conn.execute("SELECT COUNT(*) as count FROM Patron").fetchone()['count']
            total_books = conn.execute("SELECT COUNT(*) as count FROM Books").fetchone()['count']
            total_transactions = conn.execute("SELECT COUNT(*) as count FROM Transactions").fetchone()['count']
            total_payments = conn.execute("SELECT COUNT(*) as count FROM Payments").fetchone()['count']
            total_feedbacks = conn.execute("SELECT COUNT(*) as count FROM Feedback").fetchone()['count']
            
            # Fine stats
            total_fines = conn.execute("SELECT SUM(fine) as total FROM Transactions").fetchone()['total'] or 0
            borrowed_books = conn.execute("SELECT COUNT(*) as count FROM Books WHERE available=0").fetchone()['count']
            available_books = conn.execute("SELECT COUNT(*) as count FROM Books WHERE available=1").fetchone()['count']
            
            # Overdue books (more than 14 days)
            overdue = conn.execute("""
                SELECT COUNT(*) as count FROM Transactions 
                WHERE return_date IS NULL AND 
                julianday('now') - julianday(borrow_date) > 14
            """).fetchone()['count']
            
            print(f"{Color.CYAN}Library Statistics:{Color.END}")
            print(f"┌{'─'*60}┐")
            print(f"│ {'📚 Books:':<25} {total_books:<5} (Available: {available_books}, Borrowed: {borrowed_books}) │")
            print(f"│ {'👥 Patrons:':<25} {total_patrons:<5}                          │")
            print(f"│ {'📋 Transactions:':<25} {total_transactions:<5} (Overdue: {overdue})         │")
            print(f"│ {'💰 Payments:':<25} {total_payments:<5}                          │")
            print(f"│ {'💬 Feedbacks:':<25} {total_feedbacks:<5}                          │")
            print(f"│ {'💸 Total Fines:':<25} RM {total_fines:<8.2f}                │")
            print(f"└{'─'*60}┘")
            
            # Patron distribution
            print(f"\n{Color.CYAN}Patron Distribution:{Color.END}")
            rows = conn.execute("""
                SELECT role, COUNT(*) as count 
                FROM Patron 
                GROUP BY role 
                ORDER BY count DESC
            """).fetchall()
            
            for r in rows:
                percentage = (r['count'] / total_patrons * 100) if total_patrons > 0 else 0
                bar = "█" * int(percentage / 5)
                print(f"{r['role']:<12} {r['count']:<4} {bar:<20} ({percentage:.1f}%)")
                
            # Book type distribution
            print(f"\n{Color.CYAN}Book Type Distribution:{Color.END}")
            rows = conn.execute("""
                SELECT type, COUNT(*) as count 
                FROM Books 
                GROUP BY type 
                ORDER BY count DESC
            """).fetchall()
            
            for r in rows:
                percentage = (r['count'] / total_books * 100) if total_books > 0 else 0
                bar = "█" * int(percentage / 5)
                print(f"{r['type']:<12} {r['count']:<4} {bar:<20} ({percentage:.1f}%)")
                
            # Top borrowed books
            print(f"\n{Color.CYAN}Top 5 Most Borrowed Books:{Color.END}")
            rows = conn.execute("""
                SELECT b.title, COUNT(t.transaction_id) as borrow_count 
                FROM Books b 
                LEFT JOIN Transactions t ON b.book_id = t.book_id 
                GROUP BY b.book_id 
                ORDER BY borrow_count DESC 
                LIMIT 5
            """).fetchall()
            
            for i, r in enumerate(rows, 1):
                print(f"{i}. {r['title'][:40]:<40} - {r['borrow_count']} times")
                
            input(f"\n{Color.CYAN}Press Enter to continue...{Color.END}")
            
        elif choice == '7':
            print(f"\n{Color.GREEN}Logging out... Goodbye, {user['name']}!{Color.END}")
            input("Press Enter to return to main menu...")
            break
            
        conn.close()

# ==================== 2. LIBRARIAN PORTAL (BOOKS CRUD) ====================
def menu_librarian():
    user = login_portal("Librarian")
    if not user: return
    while True:
        clear(); draw_header("📚 LIBRARIAN BOOK MANAGEMENT", Color.BLUE)
        print(f"{Color.CYAN}Welcome, {user['name']} (Librarian){Color.END}\n")
        print("1. VIEW ALL BOOKS          2. ADD NEW BOOK")
        print("3. UPDATE BOOK DETAILS     4. DELETE BOOK")
        print("5. SEARCH BOOKS            6. VIEW BORROWED BOOKS")
        print("7. RETURN BOOK             8. BOOK STATISTICS")
        print("9. Logout")
        choice = input(f"\n{Color.YELLOW}Select Menu: {Color.END}")
        conn = get_db()
        
        if choice == '1':
            clear(); draw_header("📚 ALL BOOKS IN LIBRARY", Color.BLUE)
            rows = conn.execute("SELECT * FROM Books ORDER BY book_id").fetchall()
            display_books_full(rows)
            
        elif choice == '2':
            print(f"\n{Color.CYAN}--- ADD NEW BOOK ---{Color.END}")
            try:
                book_id = input("Book ID: ").strip()
                title = input("Title: ").strip()
                author = input("Author: ").strip()
                isbn = input("ISBN: ").strip()
                published_year = input("Published Year: ").strip()
                genre = input("Genre: ").strip()
                book_type = input("Type (Physical/E-book/Audiobook/Reference): ").strip().capitalize()
                call_number = input("Call Number: ").strip()
                shelf_location = input("Shelf Location (optional): ").strip() or ""
                
                if book_type not in ['Physical', 'E-book', 'Audiobook', 'Reference']:
                    print(f"{Color.RED}Invalid book type!{Color.END}")
                else:
                    conn.execute("""
                        INSERT INTO Books (book_id, title, author, isbn, published_year, genre, type, call_number, shelf_location, available) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                    """, (book_id, title, author, isbn, published_year, genre, book_type, call_number, shelf_location))
                    conn.commit()
                    print(f"{Color.GREEN}✅ Book added successfully.{Color.END}")
                    
            except Exception as e:
                print(f"{Color.RED}❌ FAILED: {str(e)}{Color.END}")
                
        elif choice == '3':
            print(f"\n{Color.CYAN}--- UPDATE BOOK ---{Color.END}")
            book_id = input("Book ID to update: ").strip()
            book = conn.execute("SELECT * FROM Books WHERE book_id=?", (book_id,)).fetchone()
            
            if not book:
                print(f"{Color.RED}Book not found!{Color.END}")
            else:
                print(f"\nCurrent Info: {book['title']} by {book['author']}")
                title = input(f"New Title [{book['title']}]: ").strip() or book['title']
                author = input(f"New Author [{book['author']}]: ").strip() or book['author']
                genre = input(f"New Genre [{book['genre']}]: ").strip() or book['genre']
                book_type = input(f"New Type [{book['type']}]: ").strip().capitalize() or book['type']
                call_number = input(f"New Call Number [{book['call_number']}]: ").strip() or book['call_number']
                shelf_location = input(f"New Shelf Location [{book['shelf_location']}]: ").strip() or book['shelf_location']
                available = input("Available? (1=Yes, 0=No) [1]: ").strip() or "1"
                
                conn.execute("""
                    UPDATE Books SET title=?, author=?, genre=?, type=?, call_number=?, shelf_location=?, available=? 
                    WHERE book_id=?
                """, (title, author, genre, book_type, call_number, shelf_location, int(available), book_id))
                conn.commit()
                print(f"{Color.GREEN}✅ Book updated successfully.{Color.END}")
                
        elif choice == '4':
            print(f"\n{Color.RED}--- DELETE BOOK ---{Color.END}")
            book_id = input("Book ID to delete: ").strip()
            confirm = input(f"Are you sure? This cannot be undone. (y/n): ").strip().lower()
            
            if confirm == 'y':
                try:
                    # Check if book is borrowed
                    txn = conn.execute("SELECT * FROM Transactions WHERE book_id=? AND return_date IS NULL", (book_id,)).fetchone()
                    if txn:
                        print(f"{Color.RED}Cannot delete! Book is currently borrowed.{Color.END}")
                    else:
                        conn.execute("DELETE FROM Books WHERE book_id=?", (book_id,))
                        conn.commit()
                        print(f"{Color.GREEN}✅ Book deleted successfully.{Color.END}")
                except Exception as e:
                    print(f"{Color.RED}❌ Failed: {str(e)}{Color.END}")
                    
        elif choice == '5':
            keyword = input("Search by title, author, genre or ISBN: ").strip()
            rows = conn.execute("""
                SELECT * FROM Books 
                WHERE title LIKE ? OR author LIKE ? OR genre LIKE ? OR isbn LIKE ? 
                ORDER BY book_id
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
            
            if rows:
                clear(); draw_header(f"🔍 SEARCH RESULTS FOR: {keyword}", Color.BLUE)
                display_books_full(rows)
            else:
                print(f"{Color.YELLOW}No books found matching '{keyword}'.{Color.END}")
                
        elif choice == '6':
            rows = conn.execute("""
                SELECT t.*, b.title, p.name 
                FROM Transactions t 
                JOIN Books b ON t.book_id = b.book_id 
                JOIN Patron p ON t.patron_id = p.patron_id 
                WHERE t.return_date IS NULL 
                ORDER BY t.borrow_date DESC
            """).fetchall()
            
            if rows:
                clear(); draw_header("📖 CURRENTLY BORROWED BOOKS", Color.BLUE)
                print(f"{Color.BOLD}{'Transaction':<10} | {'Patron':<20} | {'Book':<25} | {'Borrow Date':<12} | {'Days Borrowed'}{Color.END}")
                print("-" * 125)
                for r in rows:
                    try:
                        borrow_dt = datetime.strptime(r['borrow_date'], "%Y-%m-%d")
                        days = (datetime.now() - borrow_dt).days
                        overdue = f"{Color.RED}(Overdue {days-14} days){Color.END}" if days > 14 else ""
                    except:
                        days = 0
                        overdue = ""
                        
                    print(f"{r['transaction_id']:<10} | {r['name']:<20} | {r['title'][:25]:<25} | {r['borrow_date']:<12} | {days} days {overdue}")
            else:
                print(f"{Color.YELLOW}No books currently borrowed.{Color.END}")
                
        elif choice == '7':
            print(f"\n{Color.CYAN}--- RETURN BOOK ---{Color.END}")
            book_id = input("Book ID to return: ").strip()
            
            # Find active transaction for this book
            txn = conn.execute("""
                SELECT * FROM Transactions 
                WHERE book_id=? AND return_date IS NULL 
                ORDER BY transaction_id DESC LIMIT 1
            """, (book_id,)).fetchone()
            
            if not txn:
                print(f"{Color.RED}No active borrow record found for this book!{Color.END}")
            else:
                # Calculate fine based on days borrowed
                try:
                    borrow_dt = datetime.strptime(txn['borrow_date'], "%Y-%m-%d")
                    days = (datetime.now() - borrow_dt).days
                    fine = max(0, (days - 14) * 1.0)  # RM 1 per day after 14 days
                except:
                    fine = 0
                    
                print(f"\nBook: {book_id}")
                print(f"Borrowed on: {txn['borrow_date']}")
                print(f"Days borrowed: {days} days")
                print(f"Calculated fine: RM {fine:.2f}")
                
                return_date = input(f"Return Date (YYYY-MM-DD) [{datetime.now().strftime('%Y-%m-%d')}]: ").strip() or datetime.now().strftime('%Y-%m-%d')
                use_calculated = input(f"Use calculated fine? (y/n) [y]: ").strip().lower() or "y"
                final_fine = fine if use_calculated == 'y' else float(input("Enter fine amount: ").strip())
                
                conn.execute("""
                    UPDATE Transactions SET return_date=?, fine=? 
                    WHERE transaction_id=?
                """, (return_date, final_fine, txn['transaction_id']))
                
                # Update book availability
                if txn['item_type'] == 'Physical':
                    conn.execute("UPDATE Books SET available=1 WHERE book_id=?", (book_id,))
                    
                conn.commit()
                print(f"{Color.Green}✅ Book returned successfully. Fine: RM {final_fine:.2f}{Color.END}")
                
        elif choice == '8':
            clear(); draw_header("📊 LIBRARY STATISTICS", Color.BLUE)
            
            total_books = conn.execute("SELECT COUNT(*) as count FROM Books").fetchone()['count']
            borrowed_books = conn.execute("SELECT COUNT(*) as count FROM Books WHERE available=0").fetchone()['count']
            available_books = conn.execute("SELECT COUNT(*) as count FROM Books WHERE available=1").fetchone()['count']
            
            # Book type stats
            type_stats = conn.execute("""
                SELECT type, COUNT(*) as count 
                FROM Books 
                GROUP BY type 
                ORDER BY count DESC
            """).fetchall()
            
            # Genre stats
            genre_stats = conn.execute("""
                SELECT genre, COUNT(*) as count 
                FROM Books 
                GROUP BY genre 
                ORDER BY count DESC 
                LIMIT 10
            """).fetchall()
            
            print(f"{Color.CYAN}Book Statistics:{Color.END}")
            print(f"Total Books: {total_books}")
            print(f"Available: {available_books} ({available_books/total_books*100:.1f}%)")
            print(f"Borrowed: {borrowed_books} ({borrowed_books/total_books*100:.1f}%)")
            
            print(f"\n{Color.CYAN}Book Type Distribution:{Color.END}")
            for ts in type_stats:
                percentage = (ts['count'] / total_books * 100) if total_books > 0 else 0
                bar = "█" * int(percentage / 5)
                print(f"{ts['type']:<12} {ts['count']:<4} {bar:<20} ({percentage:.1f}%)")
                
            print(f"\n{Color.CYAN}Top Genres:{Color.END}")
            for gs in genre_stats:
                percentage = (gs['count'] / total_books * 100) if total_books > 0 else 0
                print(f"{gs['genre']:<15} {gs['count']:<4} ({percentage:.1f}%)")
                
        elif choice == '9':
            print(f"\n{Color.GREEN}Logging out... Goodbye, {user['name']}!{Color.END}")
            input("Press Enter to return to main menu...")
            break
            
        input(f"\n{Color.CYAN}Press Enter to continue...{Color.END}")
        conn.close()

# ==================== 3. STUDENT PORTAL ====================
def menu_student():
    clear(); draw_header("🎓 STUDENT LOGIN", Color.YELLOW)
    name = input("Enter your name: ").strip()
    conn = get_db()
    user = conn.execute("SELECT * FROM Patron WHERE name=? AND role='Student'", (name,)).fetchone()
    conn.close()
    
    if not user:
        print(f"\n{Color.RED}✘ No student found with that name.{Color.END}")
        input("Press Enter to try again...")
        return
        
    print(f"\n{Color.GREEN}✔ Welcome, {user['name']}!{Color.END}")
    input("Press Enter to continue...")
    
    while True:
        clear(); draw_header("🎓 STUDENT PORTAL", Color.GREEN)
        print(f"{Color.CYAN}Welcome, {user['name']} (Student){Color.END}\n")
        print("1. VIEW AVAILABLE BOOKS     2. BORROW BOOK")
        print("3. VIEW MY CURRENT LOANS    4. RETURN BOOK")
        print("5. VIEW BORROWING HISTORY   6. CHECK MY FINES")
        print("7. Logout")
        choice = input(f"\n{Color.YELLOW}Select Menu: {Color.END}")
        conn = get_db()
        
        if choice == '1':
            clear(); draw_header("📚 AVAILABLE BOOKS", Color.GREEN)
            rows = conn.execute("SELECT * FROM Books WHERE available=1 ORDER BY book_id").fetchall()
            display_books_full(rows)
            
        elif choice == '2':
            print(f"\n{Color.CYAN}--- BORROW BOOK ---{Color.END}")
            book_id = input("Book ID to borrow: ").strip()
            
            # Check if book exists and available
            book = conn.execute("SELECT * FROM Books WHERE book_id=?", (book_id,)).fetchone()
            if not book:
                print(f"{Color.RED}Book not found!{Color.END}")
            elif not book['available']:
                print(f"{Color.RED}Book is not available for borrowing!{Color.END}")
            else:
                # Check if student already borrowed this book
                existing = conn.execute("""
                    SELECT * FROM Transactions 
                    WHERE patron_id=? AND book_id=? AND return_date IS NULL
                """, (user['patron_id'], book_id)).fetchone()
                
                if existing:
                    print(f"{Color.RED}You have already borrowed this book!{Color.END}")
                else:
                    borrow_date = input(f"Borrow Date (YYYY-MM-DD) [{datetime.now().strftime('%Y-%m-%d')}]: ").strip() or datetime.now().strftime('%Y-%m-%d')
                    
                    conn.execute("""
                        INSERT INTO Transactions (patron_id, book_id, borrow_date, return_date, fine, item_type) 
                        VALUES (?, ?, ?, NULL, 0, ?)
                    """, (user['patron_id'], book_id, borrow_date, book['type']))
                    
                    # Update book availability if physical
                    if book['type'] == 'Physical':
                        conn.execute("UPDATE Books SET available=0 WHERE book_id=?", (book_id,))
                        
                    conn.commit()
                    print(f"{Color.GREEN}✅ Book borrowed successfully!{Color.END}")
                    
        elif choice == '3':
            clear(); draw_header("📖 MY CURRENT LOANS", Color.GREEN)
            rows = conn.execute("""
                SELECT t.*, b.title, b.author, b.type 
                FROM Transactions t 
                JOIN Books b ON t.book_id = b.book_id 
                WHERE t.patron_id=? AND t.return_date IS NULL 
                ORDER BY t.borrow_date DESC
            """, (user['patron_id'],)).fetchall()
            
            if rows:
                print(f"{Color.BOLD}{'Book ID':<7} | {'Title':<25} | {'Author':<20} | {'Borrow Date':<12} | {'Days'}{Color.END}")
                print("-" * 125)
                for r in rows:
                    try:
                        borrow_dt = datetime.strptime(r['borrow_date'], "%Y-%m-%d")
                        days = (datetime.now() - borrow_dt).days
                        overdue = f"{Color.RED}(Overdue {days-14} days){Color.END}" if days > 14 else ""
                    except:
                        days = 0
                        overdue = ""
                        
                    print(f"{r['book_id']:<7} | {r['title'][:25]:<25} | {r['author'][:20]:<20} | {r['borrow_date']:<12} | {days} days {overdue}")
            else:
                print(f"{Color.YELLOW}You have no current loans.{Color.END}")
                
        elif choice == '4':
            print(f"\n{Color.CYAN}--- RETURN BOOK ---{Color.END}")
            rows = conn.execute("""
                SELECT t.*, b.title 
                FROM Transactions t 
                JOIN Books b ON t.book_id = b.book_id 
                WHERE t.patron_id=? AND t.return_date IS NULL 
                ORDER BY t.borrow_date DESC
            """, (user['patron_id'],)).fetchall()
            
            if not rows:
                print(f"{Color.YELLOW}You have no books to return.{Color.END}")
            else:
                print(f"\n{Color.CYAN}Your borrowed books:{Color.END}")
                for i, r in enumerate(rows, 1):
                    print(f"{i}. Book ID: {r['book_id']} - {r['title']} (Borrowed: {r['borrow_date']})")
                    
                choice = input("\nEnter book number to return (or 0 to cancel): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(rows):
                    book_to_return = rows[int(choice)-1]
                    
                    # Calculate fine
                    try:
                        borrow_dt = datetime.strptime(book_to_return['borrow_date'], "%Y-%m-%d")
                        days = (datetime.now() - borrow_dt).days
                        fine = max(0, (days - 14) * 1.0)  # RM 1 per day after 14 days
                    except:
                        fine = 0
                        
                    print(f"\nReturning: {book_to_return['title']}")
                    print(f"Borrowed on: {book_to_return['borrow_date']}")
                    print(f"Days borrowed: {days} days")
                    print(f"Fine to pay: RM {fine:.2f}")
                    
                    confirm = input("\nConfirm return? (y/n): ").strip().lower()
                    if confirm == 'y':
                        return_date = datetime.now().strftime('%Y-%m-%d')
                        
                        conn.execute("""
                            UPDATE Transactions SET return_date=?, fine=? 
                            WHERE transaction_id=?
                        """, (return_date, fine, book_to_return['transaction_id']))
                        
                        # Update book availability if physical
                        if book_to_return['item_type'] == 'Physical':
                            conn.execute("UPDATE Books SET available=1 WHERE book_id=?", (book_to_return['book_id'],))
                            
                        conn.commit()
                        print(f"{Color.Green}✅ Book returned successfully! Fine: RM {fine:.2f}{Color.END}")
                        
        elif choice == '5':
            clear(); draw_header("📋 MY BORROWING HISTORY", Color.GREEN)
            rows = conn.execute("""
                SELECT t.*, b.title, b.author 
                FROM Transactions t 
                JOIN Books b ON t.book_id = b.book_id 
                WHERE t.patron_id=? 
                ORDER BY t.borrow_date DESC 
                LIMIT 20
            """, (user['patron_id'],)).fetchall()
            
            if rows:
                print(f"{Color.BOLD}{'Book':<25} | {'Borrow Date':<12} | {'Return Date':<12} | {'Fine'}{Color.END}")
                print("-" * 125)
                for r in rows:
                    status = f"{Color.GREEN}Returned{Color.END}" if r['return_date'] else f"{Color.RED}Borrowed{Color.END}"
                    fine = f"RM {float(r['fine'] or 0):.2f}"
                    print(f"{r['title'][:25]:<25} | {r['borrow_date']:<12} | {r['return_date'] or 'Not yet':<12} | {fine} {status}")
                    
                # Statistics
                total = len(rows)
                returned = len([r for r in rows if r['return_date']])
                current = total - returned
                total_fine = sum(float(r['fine'] or 0) for r in rows)
                
                print(f"\n{Color.CYAN}Summary:{Color.END}")
                print(f"Total Books Borrowed: {total}")
                print(f"Returned: {returned}")
                print(f"Currently Borrowed: {current}")
                print(f"Total Fines Paid: RM {total_fine:.2f}")
            else:
                print(f"{Color.YELLOW}No borrowing history found.{Color.END}")
                
        elif choice == '6':
            clear(); draw_header("💰 MY FINES SUMMARY", Color.GREEN)
            
            # Current fines (not returned books)
            current_fines = conn.execute("""
                SELECT SUM(fine) as total FROM Transactions 
                WHERE patron_id=? AND return_date IS NULL
            """, (user['patron_id'],)).fetchone()['total'] or 0
            
            # Total fines paid
            paid_fines = conn.execute("""
                SELECT SUM(fine) as total FROM Transactions 
                WHERE patron_id=? AND return_date IS NOT NULL
            """, (user['patron_id'],)).fetchone()['total'] or 0
            
            # Overdue books
            overdue = conn.execute("""
                SELECT COUNT(*) as count FROM Transactions 
                WHERE patron_id=? AND return_date IS NULL AND 
                julianday('now') - julianday(borrow_date) > 14
            """, (user['patron_id'],)).fetchone()['count']
            
            print(f"Current Fines Due: RM {current_fines:.2f}")
            print(f"Total Fines Paid: RM {paid_fines:.2f}")
            print(f"Overdue Books: {overdue}")
            
            if overdue > 0:
                print(f"\n{Color.RED}⚠ You have {overdue} overdue book(s)!{Color.END}")
                print("Please return them as soon as possible to avoid additional fines.")
                
        elif choice == '7':
            print(f"\n{Color.GREEN}Logging out... Goodbye, {user['name']}!{Color.END}")
            input("Press Enter to return to main menu...")
            break
            
        input(f"\n{Color.CYAN}Press Enter to continue...{Color.END}")
        conn.close()

# ==================== 4. BANK PORTAL ====================
def menu_bank():
    user = login_portal("Bank")
    if not user: return
    while True:
        clear(); draw_header("🏦 BANK PORTAL", Color.YELLOW)
        print(f"{Color.CYAN}Welcome, {user['name']} (Bank Officer){Color.END}\n")
        print("1. VIEW ALL PAYMENTS         2. RECORD NEW PAYMENT")
        print("3. UPDATE PAYMENT            4. DELETE PAYMENT")
        print("5. SEARCH PAYMENTS           6. VIEW PATRONS WITH FINES")
        print("7. PAYMENT STATISTICS        8. Logout")
        choice = input(f"\n{Color.YELLOW}Select Menu: {Color.END}")
        conn = get_db()
        
        if choice == '1':
            clear(); draw_header("💰 ALL PAYMENTS", Color.YELLOW)
            rows = conn.execute("SELECT * FROM Payments ORDER BY payment_date DESC").fetchall()
            display_payments_full(rows)
            
        elif choice == '2':
            print(f"\n{Color.CYAN}--- RECORD NEW PAYMENT ---{Color.END}")
            try:
                patron_id = input("Patron ID: ").strip()
                
                # Check patron and get their fines
                patron = conn.execute("SELECT * FROM Patron WHERE patron_id=?", (patron_id,)).fetchone()
                if not patron:
                    print(f"{Color.RED}Patron not found!{Color.END}")
                else:
                    # Get patron's outstanding fines
                    fines = conn.execute("""
                        SELECT SUM(fine) as total_fine FROM Transactions 
                        WHERE patron_id=? AND return_date IS NULL AND fine > 0
                    """, (patron_id,)).fetchone()['total_fine'] or 0
                    
                    print(f"\nPatron: {patron['name']} (ID: {patron_id})")
                    print(f"Outstanding Fines: RM {fines:.2f}")
                    
                    amount = input(f"Payment Amount (suggested: RM {fines:.2f}): ").strip()
                    payment_date = input(f"Payment Date (YYYY-MM-DD) [{datetime.now().strftime('%Y-%m-%d')}]: ").strip() or datetime.now().strftime('%Y-%m-%d')
                    purpose = input("Purpose [Fine Payment]: ").strip() or "Fine Payment"
                    
                    conn.execute("""
                        INSERT INTO Payments (patron_id, amount, payment_date, purpose) 
                        VALUES (?, ?, ?, ?)
                    """, (patron_id, float(amount), payment_date, purpose))
                    conn.commit()
                    print(f"{Color.GREEN}✅ Payment recorded successfully.{Color.END}")
                    
            except Exception as e:
                print(f"{Color.RED}❌ FAILED: {str(e)}{Color.END}")
                
        elif choice == '3':
            print(f"\n{Color.CYAN}--- UPDATE PAYMENT ---{Color.END}")
            payment_id = input("Payment ID to update: ").strip()
            payment = conn.execute("SELECT * FROM Payments WHERE payment_id=?", (payment_id,)).fetchone()
            
            if not payment:
                print(f"{Color.RED}Payment not found!{Color.END}")
            else:
                print(f"\nCurrent: Patron:{payment['patron_id']} Amount:RM {payment['amount']} Date:{payment['payment_date']}")
                amount = input(f"New Amount [{payment['amount']}]: ").strip() or str(payment['amount'])
                payment_date = input(f"New Date [{payment['payment_date']}]: ").strip() or payment['payment_date']
                purpose = input(f"New Purpose [{payment['purpose']}]: ").strip() or payment['purpose']
                
                conn.execute("""
                    UPDATE Payments SET amount=?, payment_date=?, purpose=? WHERE payment_id=?
                """, (float(amount), payment_date, purpose, payment_id))
                conn.commit()
                print(f"{Color.GREEN}✅ Payment updated successfully.{Color.END}")
                
        elif choice == '4':
            print(f"\n{Color.RED}--- DELETE PAYMENT ---{Color.END}")
            payment_id = input("Payment ID to delete: ").strip()
            confirm = input(f"Are you sure? (y/n): ").strip().lower()
            
            if confirm == 'y':
                try:
                    conn.execute("DELETE FROM Payments WHERE payment_id=?", (payment_id,))
                    conn.commit()
                    print(f"{Color.GREEN}✅ Payment deleted successfully.{Color.END}")
                except Exception as e:
                    print(f"{Color.RED}❌ Failed: {str(e)}{Color.END}")
                    
        elif choice == '5':
            keyword = input("Search by patron ID or purpose: ").strip()
            rows = conn.execute("""
                SELECT p.*, pat.name 
                FROM Payments p 
                JOIN Patron pat ON p.patron_id = pat.patron_id 
                WHERE p.patron_id LIKE ? OR p.purpose LIKE ? 
                ORDER BY p.payment_date DESC
            """, (f"%{keyword}%", f"%{keyword}%")).fetchall()
            
            if rows:
                clear(); draw_header(f"🔍 PAYMENT SEARCH: {keyword}", Color.YELLOW)
                print(f"{Color.BOLD}{'ID':<4} | {'Patron':<20} | {'Amount':<10} | {'Date':<12} | {'Purpose'}{Color.END}")
                print("-" * 125)
                for r in rows:
                    amount = f"RM {float(r['amount'] or 0):.2f}"
                    print(f"{r['payment_id']:<4} | {r['name'][:20]:<20} | {amount:<10} | {r['payment_date']:<12} | {r['purpose'][:30]}")
            else:
                print(f"{Color.YELLOW}No payments found.{Color.END}")
                
        elif choice == '6':
            clear(); draw_header("💰 PATRONS WITH OUTSTANDING FINES", Color.YELLOW)
            rows = conn.execute("""
                SELECT p.patron_id, p.name, p.role, SUM(t.fine) as total_fine, COUNT(t.transaction_id) as overdue_count
                FROM Patron p 
                JOIN Transactions t ON p.patron_id = t.patron_id 
                WHERE t.return_date IS NULL AND t.fine > 0
                GROUP BY p.patron_id 
                ORDER BY total_fine DESC
            """).fetchall()
            
            if rows:
                print(f"{Color.BOLD}{'Patron ID':<10} | {'Name':<20} | {'Role':<12} | {'Fine Due':<12} | {'Books'}{Color.END}")
                print("-" * 125)
                total_fines = 0
                for r in rows:
                    fine = f"RM {float(r['total_fine']):.2f}"
                    print(f"{r['patron_id']:<10} | {r['name'][:20]:<20} | {r['role']:<12} | {fine:<12} | {r['overdue_count']}")
                    total_fines += float(r['total_fine'])
                    
                print(f"\n{Color.CYAN}Total Outstanding Fines: RM {total_fines:.2f}{Color.END}")
                print(f"Number of Patrons with Fines: {len(rows)}")
            else:
                print(f"{Color.GREEN}✅ No patrons with outstanding fines.{Color.END}")
                
        elif choice == '7':
            clear(); draw_header("📊 PAYMENT STATISTICS", Color.YELLOW)
            
            # Basic stats
            total = conn.execute("SELECT SUM(amount) as total FROM Payments").fetchone()['total'] or 0
            count = conn.execute("SELECT COUNT(*) as count FROM Payments").fetchone()['count'] or 0
            avg = conn.execute("SELECT AVG(amount) as avg FROM Payments").fetchone()['avg'] or 0
            
            # Monthly breakdown
            monthly = conn.execute("""
                SELECT strftime('%Y-%m', payment_date) as month, 
                       SUM(amount) as total, COUNT(*) as count 
                FROM Payments 
                GROUP BY month 
                ORDER BY month DESC 
                LIMIT 6
            """).fetchall()
            
            # Top patrons
            top_patrons = conn.execute("""
                SELECT p.patron_id, p.name, SUM(pm.amount) as total_paid 
                FROM Payments pm 
                JOIN Patron p ON pm.patron_id = p.patron_id 
                GROUP BY p.patron_id 
                ORDER BY total_paid DESC 
                LIMIT 5
            """).fetchall()
            
            print(f"{Color.CYAN}Payment Overview:{Color.END}")
            print(f"Total Payments: {count}")
            print(f"Total Amount: RM {total:.2f}")
            print(f"Average Payment: RM {avg:.2f}")
            
            print(f"\n{Color.CYAN}Monthly Breakdown (Last 6 months):{Color.END}")
            for m in monthly:
                print(f"{m['month']}: {m['count']} payments, RM {m['total']:.2f}")
                
            print(f"\n{Color.CYAN}Top 5 Patrons by Payment:{Color.END}")
            for i, tp in enumerate(top_patrons, 1):
                print(f"{i}. {tp['name']} (ID: {tp['patron_id']}) - RM {tp['total_paid']:.2f}")
                
        elif choice == '8':
            print(f"\n{Color.GREEN}Logging out... Goodbye, {user['name']}!{Color.END}")
            input("Press Enter to return to main menu...")
            break
            
        input(f"\n{Color.CYAN}Press Enter to continue...{Color.END}")
        conn.close()

# ==================== 5. GUEST PORTAL ====================
def menu_guest():
    while True:
        clear(); draw_header("👥 GUEST PORTAL", Color.CYAN)
        print("1. VIEW ALL BOOKS           2. SEARCH BOOKS")
        print("3. VIEW BOOK DETAILS        4. VIEW FEEDBACKS")
        print("5. SUBMIT FEEDBACK          6. Return to Main Menu")
        choice = input(f"\n{Color.YELLOW}Select Menu: {Color.END}")
        conn = get_db()
        
        if choice == '1':
            clear(); draw_header("📚 ALL BOOKS IN LIBRARY", Color.CYAN)
            rows = conn.execute("SELECT * FROM Books ORDER BY book_id").fetchall()
            display_books_full(rows)
            
        elif choice == '2':
            keyword = input("Search by title, author, genre or ISBN: ").strip()
            rows = conn.execute("""
                SELECT * FROM Books 
                WHERE title LIKE ? OR author LIKE ? OR genre LIKE ? OR isbn LIKE ? 
                ORDER BY book_id
            """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
            
            if rows:
                clear(); draw_header(f"🔍 SEARCH RESULTS FOR: {keyword}", Color.CYAN)
                display_books_full(rows)
            else:
                print(f"{Color.YELLOW}No books found matching '{keyword}'.{Color.END}")
                
        elif choice == '3':
            book_id = input("Enter Book ID to view details: ").strip()
            book = conn.execute("SELECT * FROM Books WHERE book_id=?", (book_id,)).fetchone()
            
            if not book:
                print(f"{Color.RED}Book not found!{Color.END}")
            else:
                clear(); draw_header(f"📖 BOOK DETAILS: {book['title']}", Color.CYAN)
                print(f"{Color.BOLD}Title:{Color.END} {book['title']}")
                print(f"{Color.BOLD}Author:{Color.END} {book['author']}")
                print(f"{Color.BOLD}ISBN:{Color.END} {book['isbn']}")
                print(f"{Color.BOLD}Published Year:{Color.END} {book['published_year']}")
                print(f"{Color.BOLD}Genre:{Color.END} {book['genre']}")
                print(f"{Color.BOLD}Type:{Color.END} {book['type']}")
                print(f"{Color.BOLD}Call Number:{Color.END} {book['call_number']}")
                print(f"{Color.BOLD}Shelf Location:{Color.END} {book['shelf_location'] or 'Not specified'}")
                status = f"{Color.GREEN}Available{Color.END}" if book['available'] else f"{Color.RED}Borrowed{Color.END}"
                print(f"{Color.BOLD}Status:{Color.END} {status}")
                
        elif choice == '4':
            clear(); draw_header("💬 FEEDBACKS FROM USERS", Color.CYAN)
            rows = conn.execute("""
                SELECT f.*, p.name 
                FROM Feedback f 
                LEFT JOIN Patron p ON f.patron_id = p.patron_id 
                ORDER BY f.feedback_date DESC 
                LIMIT 20
            """).fetchall()
            
            if rows:
                for f in rows:
                    patron = f['name'] if f['name'] else "Anonymous"
                    rating = "⭐" * int(f['rating']) if f['rating'] else "No rating"
                    print(f"\n{Color.BOLD}{patron} - {f['feedback_date']} {rating}{Color.END}")
                    print(f"{f['comment']}")
                    print(f"{'-'*60}")
            else:
                print(f"{Color.YELLOW}No feedbacks yet.{Color.END}")
                
        elif choice == '5':
            print(f"\n{Color.CYAN}--- SUBMIT FEEDBACK ---{Color.END}")
            name = input("Your Name (optional): ").strip() or "Anonymous"
            feedback_date = input(f"Date (YYYY-MM-DD) [{datetime.now().strftime('%Y-%m-%d')}]: ").strip() or datetime.now().strftime('%Y-%m-%d')
            comment = input("Your Feedback: ").strip()
            rating = input("Rating (1-5): ").strip()
            
            if not comment or not rating.isdigit() or not 1 <= int(rating) <= 5:
                print(f"{Color.RED}Invalid input! Please provide feedback and rating (1-5).{Color.END}")
            else:
                # Create guest patron if name provided
                patron_id = None
                if name != "Anonymous":
                    guest = conn.execute("SELECT * FROM Patron WHERE name=? AND role='Guest'", (name,)).fetchone()
                    if not guest:
                        conn.execute("""
                            INSERT INTO Patron (name, role, email, password, login_count, is_active) 
                            VALUES (?, 'Guest', ?, 'guest123', 0, 1)
                        """, (name, f"{name.lower().replace(' ', '')}@guest.com"))
                        conn.commit()
                        guest = conn.execute("SELECT * FROM Patron WHERE name=? AND role='Guest'", (name,)).fetchone()
                    patron_id = guest['patron_id']
                
                conn.execute("""
                    INSERT INTO Feedback (patron_id, feedback_date, comment, rating) 
                    VALUES (?, ?, ?, ?)
                """, (patron_id, feedback_date, comment, int(rating)))
                conn.commit()
                print(f"{Color.GREEN}✅ Thank you for your feedback!{Color.END}")
                
        elif choice == '6':
            break
            
        input(f"\n{Color.CYAN}Press Enter to continue...{Color.END}")
        conn.close()

# ==================== MAIN MENU ====================
def main():
    while True:
        clear()
        print(f"{Color.BOLD}{Color.HEADER}{'='*125}")
        print("🌲 LIBRARY BORROWING SYSTEM".center(125))
        print(f"{'='*125}{Color.END}")
        print(f"\n{Color.BOLD}MAIN MENU:{Color.END}")
        print(f"{Color.CYAN}1. 🛡️  ADMIN PORTAL{Color.END}")
        print(f"{Color.BLUE}2. 📚 LIBRARIAN PORTAL{Color.END}")
        print(f"{Color.GREEN}3. 🎓 STUDENT PORTAL{Color.END}")
        print(f"{Color.YELLOW}4. 🏦 BANK PORTAL{Color.END}")
        print(f"{Color.CYAN}5. 👥 GUEST PORTAL{Color.END}")
        print(f"{Color.RED}6. 🚪 EXIT{Color.END}")
        
        choice = input(f"\n{Color.YELLOW}Select Portal (1-6): {Color.END}")
        
        if choice == '1':
            menu_admin()
        elif choice == '2':
            menu_librarian()
        elif choice == '3':
            menu_student()
        elif choice == '4':
            menu_bank()
        elif choice == '5':
            menu_guest()
        elif choice == '6':
            clear()
            print(f"{Color.BOLD}{Color.GREEN}{'='*125}")
            print("THANK YOU FOR USING LIBRARY BORROWING SYSTEM".center(125))
            print(f"{'='*125}{Color.END}\n")
            print("Goodbye! 👋")
            sys.exit(0)
        else:
            print(f"\n{Color.RED}Invalid choice! Please try again.{Color.END}")
            input("Press Enter to continue...")

# ==================== RUN APPLICATION ====================
if __name__ == "__main__":
    # Check if database exists
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'library.db')):
        print(f"{Color.RED}Error: Database 'library.db' not found!{Color.END}")
        print("Please run database_setup.py first to create the database.")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}Program interrupted by user.{Color.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Color.RED}Unexpected error: {str(e)}{Color.END}")
        sys.exit(1)