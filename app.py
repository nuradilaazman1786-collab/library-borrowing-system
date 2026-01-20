from flask import Flask, request, session, redirect
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)
app.secret_key = "nuradila_secret"

def get_db():
    # Guna SQLite local file
    conn = sqlite3.connect("library.db")
    return conn

# ==================== GLOBAL DESIGN ====================
style = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&display=swap');
  body { background:#1f3b1f url('https://images.unsplash.com/photo-1501785888041-af3ef285b470?q=80&w=1600&auto=format&fit=crop') center/cover no-repeat fixed;
         color:#eef7e6; font-family:'Playfair Display',serif; text-align:center; margin:0; }
  .overlay { background:rgba(23,46,23,.75); min-height:100vh; padding-bottom:60px; }
  h1 { font-size:48px; margin:30px 0 10px; } h2 { font-size:36px; margin:20px 0 10px; } h3 { font-size:26px; margin:18px 0 8px; }
  p, label { font-size:18px; }
  .btn { background:#2f6b2f; color:#eef7e6; padding:16px 28px; margin:10px; border-radius:14px; text-decoration:none; display:inline-block; font-size:20px; border:2px solid #9dd49d; transition:all .2s; }
  .btn:hover { background:#3f8f3f; color:#fff; transform:translateY(-2px); }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(350px,1fr)); gap:16px; width:92%; max-width:1200px; margin:0 auto 20px; }
  .card { background:linear-gradient(135deg, rgba(58,110,58,.82), rgba(41,79,41,.88)); border:1px solid #9dd49d; box-shadow:0 6px 18px rgba(0,0,0,.35); border-radius:16px; padding:16px 18px; text-align:left; backdrop-filter:blur(2px); }
  .card h3 { margin:0 0 10px; font-size:24px; } .card p { margin:6px 0; }
  .actions { margin-top:10px; display:flex; flex-wrap:wrap; gap:10px; }
  .pill { display:inline-block; padding:6px 12px; border-radius:999px; font-size:14px; border:1px solid #c6e8c6; background:rgba(255,255,255,.08); }
  .section { margin:16px auto; width:92%; max-width:1200px; text-align:left; }
  form.inline { display:inline-block; margin:6px 10px 0 0; }
  input, select, textarea { padding:10px 12px; border-radius:10px; border:1px solid #9dd49d; background:rgba(255,255,255,.12); color:#eaf6e1; margin:6px 8px; font-size:16px; outline:none; width:min(280px,92%); }
  input::placeholder, textarea::placeholder { color:#d6ead2; }
  .muted { color:#cfe8c8; font-size:16px; }
  .hr { height:1px; background:#9dd49d33; margin:18px 0; }
  .center { text-align:center; }
  .star-rating { color:#FFD700; font-size:20px; margin:5px 0; }
  .btn-small { padding:10px 16px; font-size:14px; }
  .btn-danger { background:#8b0000; border-color:#ff6b6b; }
  .btn-warning { background:#8a6d00; border-color:#ffd700; }
  .book-details { display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:10px; margin:15px 0; }
  .detail-item { background:rgba(255,255,255,.05); padding:10px; border-radius:8px; }
  .book-type { display:inline-block; padding:4px 10px; border-radius:6px; margin:2px; font-size:12px; }
  .type-physical { background:rgba(46, 204, 113, 0.2); border:1px solid rgba(46, 204, 113, 0.5); }
  .type-ebook { background:rgba(52, 152, 219, 0.2); border:1px solid rgba(52, 152, 219, 0.5); }
  .type-audiobook { background:rgba(155, 89, 182, 0.2); border:1px solid rgba(155, 89, 182, 0.5); }
  .type-reference { background:rgba(241, 196, 15, 0.2); border:1px solid rgba(241, 196, 15, 0.5); }
  .stat-box { background:linear-gradient(135deg, rgba(58,110,58,.9), rgba(41,79,41,.95)); border:2px solid #9dd49d; border-radius:12px; padding:15px; margin:10px; text-align:center; }
  .stat-value { font-size:32px; font-weight:bold; color:#fff; margin:5px 0; }
  .stat-label { font-size:14px; color:#cfe8c8; }
  .stats-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:15px; margin:20px auto; max-width:1200px; }
  .overdue { color:#ff6b6b; font-weight:bold; }
  .fine-due { background:rgba(255,0,0,0.1); padding:10px; border-radius:8px; border:1px solid #ff6b6b; margin:10px 0; }
  .auto-fine { background:rgba(255,255,0,0.1); padding:10px; border-radius:8px; border:1px solid #ffd700; margin:10px 0; }
</style>
<div class='overlay'>
"""
def end(): return "</div>"

@app.route("/test_db")
def test_db():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        conn.close()
        return f"DB connection OK, result: {result}"
    except Exception as e:
        return f"DB connection failed: {e}"

# ==================== HELPER FUNCTIONS ====================
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
            fine = (days_diff - 14) * 1.0  # RM 1 per day
            return round(fine, 2)
        return 0.0
    except:
        return 0.0

def get_patron_total_fine(patron_id):
    """Get total fine for a patron"""
    conn = get_db()
    result = conn.execute("SELECT SUM(fine) as total FROM Transactions WHERE patron_id = ? AND return_date IS NULL", 
                         (patron_id,)).fetchone()
    return result['total'] or 0

def get_patron_unpaid_fines(patron_id):
    """Get unpaid fines for a patron"""
    conn = get_db()
    result = conn.execute("""
        SELECT SUM(t.fine) as total_fine, 
               COUNT(t.transaction_id) as total_borrowed
        FROM Transactions t 
        WHERE t.patron_id = ? 
        AND t.return_date IS NULL 
        AND t.fine > 0
    """, (patron_id,)).fetchone()
    
    total_fine = result['total_fine'] or 0
    total_borrowed = result['total_borrowed'] or 0
    
    return {
        'total_fine': total_fine,
        'total_borrowed': total_borrowed,
        'patron_exists': True
    }

def get_patron_info(patron_id):
    """Get patron information"""
    conn = get_db()
    patron = conn.execute("SELECT * FROM Patron WHERE patron_id = ?", (patron_id,)).fetchone()
    return patron

# ==================== HOME ====================
@app.route("/")
def home():
    return style + """
      <h1>🌲 Library Borrowing System</h1>
      
      <div class='center'>
        <a class='btn' href='/login_admin'>🛡️ Admin</a>
        <a class='btn' href='/login_librarian'>📚 Librarian</a>
        <a class='btn' href='/login_student'>🎓 Student</a>
        <a class='btn' href='/guest'>👥 Guest</a>
        <a class='btn' href='/login_bank'>🏦 Bank</a>
        <a class='btn' href='/search_books'>🔍 Search books</a>
      </div>
    """ + end()

# ==================== LOGIN HELPERS ====================
def login_role_page(title, post_url):
    return style + f"""
      <h2>{title}</h2>
      <form method='POST' action='{post_url}' class='center'>
        <label>Email</label><br>
        <input name='email' placeholder='email@example.com' required><br>
        <label>Password</label><br>
        <input type='password' name='password' placeholder='••••••••' required><br>
        <button class='btn'>🔓 Login</button>
      </form>
      <div class='center'><a class='btn' href='/'>⬅️ Kembali</a></div>
    """ + end()

def login_role_submit(role, success_path):
    email = request.form.get("email","").strip()
    password = request.form.get("password","").strip()
    conn = get_db()
    user = conn.execute("SELECT * FROM Patron WHERE email=? AND password=? AND role=?", (email, password, role)).fetchone()
    if user:
        session["role"] = role
        session["patron_id"] = user["patron_id"]
        session["name"] = user["name"]
        return redirect(success_path)
    return style + "<h2>❌ Invalid credentials</h2><div class='center'><a class='btn' href='/'>⬅️ Kembali</a></div>" + end()

# ==================== LOGIN ROUTES ====================
@app.route("/login_admin", methods=["GET","POST"])
def login_admin():
    if request.method == "POST": return login_role_submit("Admin", "/admin")
    return login_role_page("🛡️ Admin login", "/login_admin")

@app.route("/login_librarian", methods=["GET","POST"])
def login_librarian():
    if request.method == "POST": return login_role_submit("Librarian", "/librarian")
    return login_role_page("📚 Librarian login", "/login_librarian")

@app.route("/login_bank", methods=["GET","POST"])
def login_bank():
    if request.method == "POST": return login_role_submit("Bank", "/bank")
    return login_role_page("🏦 Bank login", "/login_bank")

@app.route("/login_student", methods=["GET","POST"])
def login_student():
    return style + """
      <h2>🎓 Student Login</h2>
      <form method='POST' action='/student_login' class='center'>
        <label>Nama</label><br>
        <input name='name' placeholder='Nama dalam data' required><br>
        <button class='btn'>🔓 Login</button>
      </form>
      <div class='center'><a class='btn' href='/'>⬅️ Kembali</a></div>
    """ + end()

@app.route("/student_login", methods=["POST"])
def student_login():
    name = request.form.get("name","").strip()
    conn = get_db()
    user = conn.execute("SELECT * FROM Patron WHERE name=? AND role='Student'", (name,)).fetchone()
    if user:
        session["role"] = "Student"
        session["patron_id"] = user["patron_id"]
        session["name"] = user["name"]
        return redirect("/student")
    return style + "<h2>❌ Tiada data untuk nama ini</h2><div class='center'><a class='btn' href='/'>⬅️ Kembali</a></div>" + end()

# ==================== GUEST ACCESS ====================
@app.route("/guest")
def guest():
    conn = get_db()
    books = conn.execute("SELECT * FROM Books").fetchall()
    feedbacks = conn.execute("SELECT * FROM Feedback").fetchall()
    
    html = style + "<h1>👥 Guest Access</h1>"
    html += "<p class='muted center'>View books and manage feedback without login</p>"
    
    # Book Collection Section
    html += "<h2>📚 Book Collection</h2>"
    html += "<div class='section'><div class='grid'>"
    for b in books:
        status = "Available ✅" if b['available'] else "Borrowed ❌"
        type_class = f"type-{b['type'].lower().replace('-', '').replace(' ', '')}"
        html += f"""
        <div class='card'>
          <h3>{b['title'] or '-'} <span class='pill'>{status}</span></h3>
          <p><strong>Author:</strong> {b['author'] or '-'}</p>
          <p><strong>Genre:</strong> {b['genre'] or '-'} <span class='book-type {type_class}'>{b['type'] or '-'}</span></p>
          <p><strong>Call Number:</strong> {b['call_number'] or '-'}</p>
          <div class='actions'>
            <a class='btn btn-small' href='/guest_view_book/{b['book_id']}'>👁️ View Details</a>
          </div>
        </div>
        """
    html += "</div></div>"
    
    # Feedback Section
    html += "<div class='hr'></div>"
    html += "<h2>💬 All Feedback</h2>"
    
    if feedbacks:
        html += "<div class='section'><div class='grid'>"
        for f in feedbacks:
            rating_stars = "⭐" * int(f['rating']) if f['rating'] else "No rating"
            patron_name = "Anonymous"
            if f['patron_id']:
                patron = conn.execute("SELECT name FROM Patron WHERE patron_id=?", (f['patron_id'],)).fetchone()
                patron_name = patron['name'] if patron else "Anonymous"
            
            html += f"""
            <div class='card'>
              <h3>Feedback #{f['feedback_id']}</h3>
              <p><strong>From:</strong> {patron_name}</p>
              <p><strong>Date:</strong> {f['feedback_date'] or '-'}</p>
              <div class='star-rating'>{rating_stars}</div>
              <p><strong>Comment:</strong> {f['comment'][:100]}{'...' if len(f['comment']) > 100 else ''}</p>
              <div class='actions'>
                <a class='btn btn-small' href='/guest_view_feedback/{f['feedback_id']}'>👁️ View</a>
                <a class='btn btn-small btn-warning' href='/guest_edit_feedback/{f['feedback_id']}'>✏️ Edit</a>
                <form class='inline' method='POST' action='/guest_delete_feedback/{f['feedback_id']}'>
                  <button class='btn btn-small btn-danger' type='submit' onclick='return confirm("Delete this feedback?")'>🗑️ Delete</button>
                </form>
              </div>
            </div>
            """
        html += "</div></div>"
    else:
        html += "<p class='muted center'>No feedback yet. Be the first to add feedback!</p>"
    
    # Add Feedback Form
    html += """
    <div class='hr'></div>
    <div class='section'>
      <div class='card'>
        <h3>➕ Add New Feedback</h3>
        <form method='POST' action='/guest_create_feedback'>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Your Name (Optional)</label>
            <input name='name' placeholder='Enter your name'>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Feedback Date</label>
            <input type='date' name='feedback_date' value='""" + datetime.now().strftime("%Y-%m-%d") + """' required>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Rating (1-5 Stars)</label>
            <select name='rating' required>
              <option value=''>Select Rating</option>
              <option value='5'>⭐⭐⭐⭐⭐ Excellent</option>
              <option value='4'>⭐⭐⭐⭐ Very Good</option>
              <option value='3'>⭐⭐⭐ Good</option>
              <option value='2'>⭐⭐ Fair</option>
              <option value='1'>⭐ Poor</option>
            </select>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Your Comments</label>
            <textarea name='comment' placeholder='Share your thoughts...' rows='4' required></textarea>
          </div>
          <button class='btn' type='submit'>💾 Submit Feedback</button>
        </form>
      </div>
    </div>
    """
    
    html += "<div class='center'><a class='btn' href='/'>⬅️ Back to Home</a></div>"
    return html + end()

# ==================== GUEST VIEW BOOK DETAILS ====================
@app.route("/guest_view_book/<int:book_id>")
def guest_view_book(book_id):
    conn = get_db()
    b = conn.execute("SELECT * FROM Books WHERE book_id=?", (book_id,)).fetchone()
    
    if not b:
        return style + "<h3>❌ Book not found</h3><div class='center'><a class='btn' href='/guest'>⬅️ Back</a></div>" + end()
    
    status = "Available ✅" if b['available'] else "Borrowed ❌"
    type_class = f"type-{b['type'].lower().replace('-', '').replace(' ', '')}"
    
    # Get book type icon
    type_icon = {
        'Physical': '📖',
        'E-book': '💻',
        'Audiobook': '🎧',
        'Reference': '📚'
    }.get(b['type'], '📖')
    
    return style + f"""
      <h2>📖 Book Details</h2>
      <div class='card'>
        <h3>{b['title'] or '-'}</h3>
        <div class='book-details'>
          <div class='detail-item'>
            <strong>Author:</strong><br>{b['author'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>ISBN:</strong><br>{b['isbn'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Published Year:</strong><br>{b['published_year'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Genre:</strong><br>{b['genre'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Type:</strong><br>{type_icon} <span class='book-type {type_class}'>{b['type'] or '-'}</span>
          </div>
          <div class='detail-item'>
            <strong>Call Number:</strong><br>{b['call_number'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Shelf Location:</strong><br>{b['shelf_location'] or 'Not specified'}
          </div>
          <div class='detail-item'>
            <strong>Status:</strong><br>{status}
          </div>
        </div>
        <p><strong>Book ID:</strong> {b['book_id']}</p>
      </div>
      <div class='center'>
        <a class='btn' href='/guest'>⬅️ Back to Guest</a>
        <a class='btn' href='/search_books'>🔍 Search More Books</a>
      </div>
    """ + end()

# ==================== GUEST FEEDBACK CRUD ====================
@app.route("/guest_create_feedback", methods=["POST"])
def guest_create_feedback():
    name = request.form.get("name", "").strip()
    feedback_date = request.form.get("feedback_date")
    comment = request.form.get("comment")
    rating = request.form.get("rating")
    
    conn = get_db()
    
    # If name is provided, create or find guest patron
    patron_id = None
    if name:
        # Check if guest exists
        guest = conn.execute("SELECT * FROM Patron WHERE name=? AND role='Guest'", (name,)).fetchone()
        if guest:
            patron_id = guest['patron_id']
        else:
            # Create new guest
            conn.execute("INSERT INTO Patron (name, role, email, password, is_active) VALUES (?, 'Guest', ?, ?, 1)",
                        (name, f"{name.lower().replace(' ', '')}@guest.com", "guest123"))
            conn.commit()
            new_guest = conn.execute("SELECT * FROM Patron WHERE name=? AND role='Guest'", (name,)).fetchone()
            patron_id = new_guest['patron_id']
    
    # Insert feedback
    conn.execute("INSERT INTO Feedback (patron_id, feedback_date, comment, rating) VALUES (?, ?, ?, ?)",
                (patron_id, feedback_date, comment, rating))
    conn.commit()
    
    return redirect("/guest")

@app.route("/guest_view_feedback/<int:feedback_id>")
def guest_view_feedback(feedback_id):
    conn = get_db()
    f = conn.execute("SELECT * FROM Feedback WHERE feedback_id = ?", (feedback_id,)).fetchone()
    
    if not f:
        return style + "<h3>❌ Feedback not found</h3><div class='center'><a class='btn' href='/guest'>⬅️ Back</a></div>" + end()
    
    rating_stars = "⭐" * int(f['rating']) if f['rating'] else "No rating"
    patron_name = "Anonymous"
    if f['patron_id']:
        patron = conn.execute("SELECT name FROM Patron WHERE patron_id=?", (f['patron_id'],)).fetchone()
        patron_name = patron['name'] if patron else "Anonymous"
    
    return style + f"""
      <h2>📝 Feedback Details</h2>
      <div class='card'>
        <h3>Feedback #{f['feedback_id']}</h3>
        <p><strong>From:</strong> {patron_name}</p>
        <p><strong>Date:</strong> {f['feedback_date']}</p>
        <p><strong>Rating:</strong> {rating_stars} ({f['rating']}/5)</p>
        <p><strong>Comment:</strong></p>
        <div style='background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin: 10px 0;'>
          {f['comment']}
        </div>
        <div class='actions' style='justify-content: center; margin-top: 20px;'>
          <a class='btn' href='/guest_edit_feedback/{feedback_id}'>✏️ Edit Feedback</a>
          <a class='btn' href='/guest'>⬅️ Back to Guest</a>
        </div>
      </div>
    """ + end()

@app.route("/guest_edit_feedback/<int:feedback_id>", methods=["GET", "POST"])
def guest_edit_feedback(feedback_id):
    conn = get_db()
    f = conn.execute("SELECT * FROM Feedback WHERE feedback_id = ?", (feedback_id,)).fetchone()
    
    if not f:
        return style + "<h3>❌ Feedback not found</h3><div class='center'><a class='btn' href='/guest'>⬅️ Back</a></div>" + end()
    
    if request.method == "POST":
        comment = request.form.get("comment", f['comment'])
        rating = request.form.get("rating", f['rating'])
        
        conn.execute("UPDATE Feedback SET comment = ?, rating = ? WHERE feedback_id = ?",
                    (comment, rating, feedback_id))
        conn.commit()
        
        return redirect(f"/guest_view_feedback/{feedback_id}")
    
    # GET request - show edit form
    return style + f"""
      <h2>✏️ Edit Feedback #{feedback_id}</h2>
      <div class='card' style='max-width: 600px; margin: 30px auto;'>
        <form method='POST'>
          <div style='margin-bottom: 20px;'>
            <label style='display: block; margin-bottom: 8px;'>Feedback Date</label>
            <input type='date' name='feedback_date' value='{f['feedback_date']}' readonly>
            <p class='muted' style='font-size: 14px;'>Date cannot be changed</p>
          </div>
          
          <div style='margin-bottom: 20px;'>
            <label style='display: block; margin-bottom: 8px;'>Rating (1-5 Stars)</label>
            <select name='rating' required>
              <option value='1' {'selected' if f['rating'] == 1 else ''}>⭐ Poor (1)</option>
              <option value='2' {'selected' if f['rating'] == 2 else ''}>⭐⭐ Fair (2)</option>
              <option value='3' {'selected' if f['rating'] == 3 else ''}>⭐⭐⭐ Good (3)</option>
              <option value='4' {'selected' if f['rating'] == 4 else ''}>⭐⭐⭐⭐ Very Good (4)</option>
              <option value='5' {'selected' if f['rating'] == 5 else ''}>⭐⭐⭐⭐⭐ Excellent (5)</option>
            </select>
          </div>
          
          <div style='margin-bottom: 30px;'>
            <label style='display: block; margin-bottom: 8px;'>Your Comments</label>
            <textarea name='comment' rows='6' required>{f['comment']}</textarea>
          </div>
          
          <button class='btn' type='submit'>💾 Save Changes</button>
          <a class='btn' href='/guest_view_feedback/{feedback_id}'>❌ Cancel</a>
        </form>
      </div>
    """ + end()

@app.route("/guest_delete_feedback/<int:feedback_id>", methods=["POST"])
def guest_delete_feedback(feedback_id):
    conn = get_db()
    conn.execute("DELETE FROM Feedback WHERE feedback_id = ?", (feedback_id,))
    conn.commit()
    return redirect("/guest")

# ==================== ADMIN PANEL ====================
@app.route("/admin")
def admin():
    if session.get("role") != "Admin":
        return redirect("/login_admin")

    conn = get_db()
    
    # Statistics
    total_patrons = conn.execute("SELECT COUNT(*) as count FROM Patron").fetchone()["count"]
    total_books = conn.execute("SELECT COUNT(*) as count FROM Books").fetchall()[0]["count"]
    total_transactions = conn.execute("SELECT COUNT(*) as count FROM Transactions").fetchone()["count"]
    
    # Total fines calculation
    total_fines_result = conn.execute("SELECT SUM(fine) as total FROM Transactions").fetchone()
    total_fines = total_fines_result["total"] or 0
    
    # Borrowed books
    borrowed_books = conn.execute("SELECT COUNT(*) as count FROM Books WHERE available=0").fetchone()["count"]
    
    patrons = conn.execute("SELECT * FROM Patron").fetchall()
    books = conn.execute("SELECT * FROM Books").fetchall()
    txns = conn.execute("SELECT * FROM Transactions").fetchall()

    html = style + "<h2>🛡️ Admin panel</h2>"
    html += "<p class='muted center'>Manage all system data</p>"
    
    # Statistics Section
    html += """
    <div class='section'>
      <h3>📊 System Statistics</h3>
      <div class='stats-grid'>
        <div class='stat-box'>
          <div class='stat-value'>{}</div>
          <div class='stat-label'>Total Patrons</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>{}</div>
          <div class='stat-label'>Total Books</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>{}</div>
          <div class='stat-label'>Borrowed Books</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>{}</div>
          <div class='stat-label'>Total Transactions</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>RM {:.2f}</div>
          <div class='stat-label'>Total Fines</div>
        </div>
      </div>
    </div>
    """.format(total_patrons, total_books, borrowed_books, total_transactions, total_fines)
    
    html += "<div class='hr'></div>"

    # Patrons with fine information
    html += "<div class='section'><h3>👥 Patrons</h3><div class='grid'>"
    for p in patrons:
        # Calculate patron's total fine
        patron_fine = get_patron_total_fine(p['patron_id'])
        
        html += f"""
        <div class='card'>
          <h3>{p['name'] or '-'} <span class='pill'>{p['role'] or '-'}</span></h3>
          <p>Email: {p['email'] or '-'}</p>
          <p>Active: {'✅' if p['is_active'] else '❌'}</p>
          {f"<div class='fine-due'><strong>Total Fine Due:</strong> RM {patron_fine:.2f}</div>" if patron_fine > 0 else ""}
          <div class='actions'>
            <a class='btn btn-small' href='/admin/view/patron/{p['patron_id']}'>👁️ View</a>
            <form class='inline' method='POST' action='/admin/update/patron/{p['patron_id']}'>
              <input name='name' placeholder='New name'>
              <input name='email' placeholder='New email'>
              <input name='role' placeholder='New role'>
              <select name='is_active'>
                <option value=''>Select Status</option>
                <option value='1'>Active</option>
                <option value='0'>Inactive</option>
              </select>
              <button class='btn btn-small'>✏️ Update</button>
            </form>
            <form class='inline' method='POST' action='/admin/delete/patron/{p['patron_id']}'>
              <button class='btn btn-small btn-danger'>🗑️ Delete</button>
            </form>
          </div>
        </div>
        """
    html += "</div><div class='hr'></div>"
    html += """
      <div class='card'>
        <h3>➕ Add patron</h3>
        <form method='POST' action='/admin/create/patron'>
          <input name='name' placeholder='Name' required>
          <input name='email' placeholder='Email' required>
          <input name='password' placeholder='Password' required>
          <input name='role' placeholder='Role (Admin/Librarian/Student/Guest/Bank)' required>
          <button class='btn'>➕ Add</button>
        </form>
      </div>
    """

    # Books - ADMIN HANYA BOLEH VIEW SAJA
    html += "<div class='section'><h3>📚 Books (View Only)</h3><div class='grid'>"
    for b in books:
        status = "Available ✅" if (b['available'] or 0) == 1 else "Borrowed ❌"
        type_class = f"type-{b['type'].lower().replace('-', '').replace(' ', '')}"
        html += f"""
        <div class='card'>
          <h3>{b['title'] or '-'} <span class='pill'>{status}</span></h3>
          <p><strong>Author:</strong> {b['author'] or '-'}</p>
          <p><strong>Genre:</strong> {b['genre'] or '-'} <span class='book-type {type_class}'>{b['type'] or '-'}</span></p>
          <p><strong>Call #:</strong> {b['call_number'] or '-'}</p>
          <div class='actions'>
            <a class='btn btn-small' href='/admin/view/book/{b['book_id']}'>👁️ View</a>
          </div>
        </div>
        """
    html += "</div></div><div class='hr'></div>"

    # Create Transaction Form with AUTO-FINE CALCULATION
    html += """
    <div class='section'>
      <div class='card'>
        <h3>➕ Create Transaction (Auto Fine Calculation)</h3>
        <form method='POST' action='/admin/create/txn'>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Patron ID *</label>
            <input type='number' name='patron_id' id='patron_id' placeholder='Enter Patron ID' required 
                   onchange='checkPatronFine(this.value)'>
            <div id='patron_fine_info' style='margin-top:10px; display:none;'></div>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Book ID *</label>
            <input name='book_id' placeholder='Book ID' required>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Borrow Date *</label>
            <input type='date' name='borrow_date' id='borrow_date' value='""" + datetime.now().strftime("%Y-%m-%d") + """' required 
                   onchange='calculateFine()'>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Return Date (Leave empty if not returned)</label>
            <input type='date' name='return_date' id='return_date' onchange='calculateFine()'>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Item Type</label>
            <select name='item_type'>
              <option value='Physical'>Physical</option>
              <option value='E-book'>E-book</option>
              <option value='Audiobook'>Audiobook</option>
            </select>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Fine Amount (Auto-calculated)</label>
            <input type='number' name='fine' id='fine' placeholder='Auto-calculated' step='0.01' readonly style='background:rgba(255,255,255,0.05);'>
          </div>
          <div id='fine_calculation' class='auto-fine' style='display:none; margin-bottom:15px;'>
            <strong>Fine Calculation:</strong>
            <div id='calculation_details'></div>
          </div>
          <button class='btn' type='submit'>➕ Create Transaction</button>
        </form>
      </div>
    </div>
    
    <script>
    function checkPatronFine(patronId) {
        if (!patronId) return;
        
        fetch('/check_patron_fine/' + patronId)
            .then(response => response.json())
            .then(data => {
                const infoDiv = document.getElementById('patron_fine_info');
                if (data.patron_exists) {
                    if (data.total_fine > 0) {
                        infoDiv.innerHTML = `<div class='fine-due'>
                            <strong>⚠️ This patron has outstanding fines!</strong><br>
                            Total Fine Due: RM ${data.total_fine.toFixed(2)}<br>
                            Currently Borrowed: ${data.total_borrowed} books
                        </div>`;
                    } else {
                        infoDiv.innerHTML = `<div style='background:rgba(0,255,0,0.1); padding:10px; border-radius:8px;'>
                            ✅ This patron has no outstanding fines
                        </div>`;
                    }
                    infoDiv.style.display = 'block';
                } else {
                    infoDiv.innerHTML = `<div style='background:rgba(255,255,0,0.1); padding:10px; border-radius:8px;'>
                        ⚠️ Patron ID not found in system
                    </div>`;
                    infoDiv.style.display = 'block';
                }
            });
    }
    
    function calculateFine() {
        const borrowDate = document.getElementById('borrow_date').value;
        const returnDate = document.getElementById('return_date').value;
        
        if (!borrowDate) return;
        
        fetch('/calculate_fine', {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: 'borrow_date=' + encodeURIComponent(borrowDate) + 
                  '&return_date=' + encodeURIComponent(returnDate || '')
        })
        .then(response => response.json())
        .then(data => {
            const fineInput = document.getElementById('fine');
            const fineDiv = document.getElementById('fine_calculation');
            const detailsDiv = document.getElementById('calculation_details');
            
            fineInput.value = data.fine;
            
            if (data.fine > 0) {
                detailsDiv.innerHTML = `
                    Borrow Date: ${borrowDate}<br>
                    ${returnDate ? 'Return Date: ' + returnDate : 'Not Returned Yet'}<br>
                    Days Overdue: ${data.days_overdue}<br>
                    Fine Rate: RM 1.00 per day after 14 days<br>
                    Total Fine: RM ${data.fine.toFixed(2)}
                `;
                fineDiv.style.display = 'block';
            } else {
                fineDiv.style.display = 'none';
            }
        });
    }
    </script>
    """
    
    html += "<div class='hr'></div>"
    
    # Transactions list
    html += "<div class='section'><h3>🎓 Transactions</h3><div class='grid'>"
    for t in txns:
        fine = float(t['fine'] or 0)
        borrow_date = t['borrow_date'] or "-"
        return_date = t['return_date'] or "Not returned"
        
        html += f"""
        <div class='card'>
          <h3>Txn #{t['transaction_id']}</h3>
          <p>Patron: {t['patron_id'] or '-'} • Book: {t['book_id'] or '-'}</p>
          <p>Borrow: {borrow_date} • Return: {return_date}</p>
          <p>Type: {t['item_type'] or '-'}</p>
          <p>Fine: RM {fine:.2f}</p>
          <div class='actions'>
            <a class='btn btn-small' href='/admin/view/txn/{t['transaction_id']}'>👁️ View</a>
            <form class='inline' method='POST' action='/admin/update/txn/{t['transaction_id']}'>
              <input name='patron_id' placeholder='New patron ID'>
              <input name='book_id' placeholder='New book ID'>
              <input name='borrow_date' placeholder='New borrow date'>
              <input name='return_date' placeholder='New return date'>
              <input name='fine' placeholder='New fine'>
              <select name='item_type'>
                <option value=''>Select Item Type</option>
                <option value='Physical'>Physical</option>
                <option value='E-book'>E-book</option>
                <option value='Audiobook'>Audiobook</option>
              </select>
              <button class='btn btn-small'>✏️ Update</button>
            </form>
            <form class='inline' method='POST' action='/admin/delete/txn/{t['transaction_id']}'>
              <button class='btn btn-small btn-danger'>🗑️ Delete</button>
            </form>
          </div>
        </div>
        """
    html += "</div></div>"
    
    html += "<div class='center'><a class='btn' href='/'>⬅️ Kembali</a></div>"
    return html + end()

# ----- Admin API endpoints for auto-calculation -----
@app.route("/check_patron_fine/<int:patron_id>")
def check_patron_fine_api(patron_id):
    """API endpoint to check patron's fine"""
    fine_info = get_patron_unpaid_fines(patron_id)
    return fine_info

@app.route("/calculate_fine", methods=["POST"])
def calculate_fine_api():
    """API endpoint to calculate fine"""
    borrow_date = request.form.get("borrow_date")
    return_date = request.form.get("return_date")
    
    try:
        if borrow_date:
            fine = calculate_fine(borrow_date, return_date if return_date else None)
            
            # Calculate days overdue
            borrow_dt = datetime.strptime(borrow_date, "%Y-%m-%d")
            if return_date:
                return_dt = datetime.strptime(return_date, "%Y-%m-%d")
                days_diff = (return_dt - borrow_dt).days
            else:
                days_diff = (datetime.now() - borrow_dt).days
            
            days_overdue = max(0, days_diff - 14)
            
            return {
                'fine': fine,
                'days_overdue': days_overdue,
                'borrow_date': borrow_date,
                'return_date': return_date
            }
    except Exception as e:
        print(f"Error calculating fine: {e}")
    
    return {'fine': 0, 'days_overdue': 0}

# ----- Admin view detail routes -----
@app.route("/admin/view/patron/<int:id>")
def admin_view_patron(id):
    if session.get("role") != "Admin": 
        return redirect("/login_admin")
    
    conn = get_db()
    p = conn.execute("SELECT * FROM Patron WHERE patron_id=?", (id,)).fetchone()
    if not p: 
        return style + "<h3>❌ Patron not found</h3><div class='center'><a class='btn' href='/admin'>⬅️ Back</a></div>" + end()
    
    # Get patron's transactions and fines
    transactions = conn.execute("""
        SELECT t.*, b.title 
        FROM Transactions t 
        LEFT JOIN Books b ON t.book_id = b.book_id 
        WHERE t.patron_id=?
        ORDER BY t.borrow_date DESC
    """, (id,)).fetchall()
    
    total_fine = get_patron_total_fine(id)
    
    html = style + f"""
      <h2>👁️ Patron Details - {p['name']}</h2>
      <div class='card'>
        <div class='book-details'>
          <div class='detail-item'>
            <strong>Patron ID:</strong><br>{p['patron_id']}
          </div>
          <div class='detail-item'>
            <strong>Name:</strong><br>{p['name']}
          </div>
          <div class='detail-item'>
            <strong>Email:</strong><br>{p['email']}
          </div>
          <div class='detail-item'>
            <strong>Role:</strong><br>{p['role']}
          </div>
          <div class='detail-item'>
            <strong>Active:</strong><br>{'✅ Yes' if p['is_active'] else '❌ No'}
          </div>
          <div class='detail-item fine-due' style='grid-column: 1 / -1;'>
            <strong>Total Fine Due:</strong><br>RM {total_fine:.2f}
          </div>
        </div>
      </div>
    """
    
    # Show transactions
    if transactions:
        html += "<div class='section'><h3>📋 Transaction History</h3><div class='grid'>"
        for t in transactions:
            return_date = t['return_date'] or "Not returned"
            fine = float(t['fine'] or 0)
            html += f"""
            <div class='card'>
              <h3>{t['title'] or f'Book #{t['book_id']}'}</h3>
              <p><strong>Transaction ID:</strong> {t['transaction_id']}</p>
              <p><strong>Borrow Date:</strong> {t['borrow_date']}</p>
              <p><strong>Return Date:</strong> {return_date}</p>
              <p><strong>Fine:</strong> RM {fine:.2f}</p>
            </div>
            """
        html += "</div></div>"
    
    html += "<div class='center'><a class='btn' href='/admin'>⬅️ Back</a></div>"
    return html + end()

@app.route("/admin/view/book/<int:id>")
def admin_view_book(id):
    if session.get("role") != "Admin":
        return redirect("/login_admin")
    conn = get_db()
    b = conn.execute("SELECT * FROM Books WHERE book_id=?", (id,)).fetchone()
    if not b:
        return style + "<h3>❌ Book not found</h3><div class='center'><a class='btn' href='/admin'>⬅️ Back</a></div>" + end()
    
    status = "Available ✅" if (b['available'] or 0) == 1 else "Borrowed ❌"
    type_class = f"type-{b['type'].lower().replace('-', '').replace(' ', '')}"
    
    return style + f"""
      <h2>👁️ Book detail</h2>
      <div class='card'>
        <h3>{b['title'] or '-'}</h3>
        <div class='book-details'>
          <div class='detail-item'>
            <strong>Author:</strong><br>{b['author'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>ISBN:</strong><br>{b['isbn'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Published Year:</strong><br>{b['published_year'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Genre:</strong><br>{b['genre'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Type:</strong><br><span class='book-type {type_class}'>{b['type'] or '-'}</span>
          </div>
          <div class='detail-item'>
            <strong>Call Number:</strong><br>{b['call_number'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Shelf Location:</strong><br>{b['shelf_location'] or 'Not specified'}
          </div>
          <div class='detail-item'>
            <strong>Status:</strong><br>{status}
          </div>
        </div>
        <p><strong>Book ID:</strong> {b['book_id']}</p>
      </div>
      <div class='center'><a class='btn' href='/admin'>⬅️ Back</a></div>
    """ + end()

@app.route("/admin/view/txn/<int:id>")
def admin_view_txn(id):
    if session.get("role") != "Admin": 
        return redirect("/login_admin")
    
    conn = get_db()
    t = conn.execute("SELECT * FROM Transactions WHERE transaction_id=?", (id,)).fetchone()
    if not t: 
        return style + "<h3>❌ Transaction not found</h3><div class='center'><a class='btn' href='/admin'>⬅️ Back</a></div>" + end()
    
    borrow = t["borrow_date"] or "-"
    ret = t["return_date"] or "Not returned"
    fine = t["fine"] if t["fine"] is not None else 0
    
    # Get patron and book info
    patron = conn.execute("SELECT name FROM Patron WHERE patron_id=?", (t['patron_id'],)).fetchone()
    book = conn.execute("SELECT title, author FROM Books WHERE book_id=?", (t['book_id'],)).fetchone()
    
    patron_name = patron['name'] if patron else f"Patron #{t['patron_id']}"
    book_title = book['title'] if book else f"Book #{t['book_id']}"
    book_author = book['author'] if book else "Unknown"
    
    return style + f"""
      <h2>👁️ Transaction Details</h2>
      <div class='card'>
        <div class='book-details'>
          <div class='detail-item'>
            <strong>Transaction ID:</strong><br>{t['transaction_id']}
          </div>
          <div class='detail-item'>
            <strong>Patron:</strong><br>{patron_name}
          </div>
          <div class='detail-item'>
            <strong>Book:</strong><br>{book_title}<br><small>{book_author}</small>
          </div>
          <div class='detail-item'>
            <strong>Borrow Date:</strong><br>{borrow}
          </div>
          <div class='detail-item'>
            <strong>Return Date:</strong><br>{ret}
          </div>
          <div class='detail-item'>
            <strong>Item Type:</strong><br>{t['item_type'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Fine Amount:</strong><br>RM {fine:.2f}
          </div>
        </div>
      </div>
      <div class='center'><a class='btn' href='/admin'>⬅️ Back</a></div>
    """ + end()

# ----- Admin CRUD handlers -----
@app.route("/admin/create/patron", methods=["POST"])
def admin_create_patron():
    try:
        conn = get_db()
        conn.execute("INSERT INTO Patron (name, role, email, password, is_active) VALUES (?,?,?,?,1)",
                    (request.form["name"], request.form["role"], request.form["email"], request.form["password"]))
        conn.commit()
    except Exception as e:
        print(f"Error creating patron: {e}")
    return redirect("/admin")

@app.route("/admin/update/patron/<int:id>", methods=["POST"])
def admin_update_patron(id):
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        role = request.form.get("role")
        is_active = request.form.get("is_active")
        
        conn = get_db()
        updates = []
        params = []
        
        if name and name.strip():
            updates.append("name = ?")
            params.append(name.strip())
        if email and email.strip():
            updates.append("email = ?")
            params.append(email.strip())
        if role and role.strip():
            updates.append("role = ?")
            params.append(role.strip())
        if is_active and is_active.strip():
            updates.append("is_active = ?")
            params.append(int(is_active))
        
        if updates:
            params.append(id)
            query = f"UPDATE Patron SET {', '.join(updates)} WHERE patron_id = ?"
            conn.execute(query, params)
            conn.commit()
    except Exception as e:
        print(f"Error updating patron {id}: {e}")
    
    return redirect("/admin")

@app.route("/admin/delete/patron/<int:id>", methods=["POST"])
def admin_delete_patron(id):
    try:
        conn = get_db()
        conn.execute("DELETE FROM Patron WHERE patron_id=?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting patron {id}: {e}")
    return redirect("/admin")

@app.route("/admin/create/txn", methods=["POST"])
def admin_create_txn():
    try:
        conn = get_db()
        fine = request.form.get("fine", 0)
        if fine == "":
            fine = 0
        
        # Check if patron exists
        patron_id = request.form.get("patron_id")
        patron = conn.execute("SELECT * FROM Patron WHERE patron_id=?", (patron_id,)).fetchone()
        if not patron:
            return style + "<h3>❌ Patron not found</h3><div class='center'><a class='btn' href='/admin'>⬅️ Back</a></div>" + end()
        
        # Check if book exists
        book_id = request.form.get("book_id")
        book = conn.execute("SELECT * FROM Books WHERE book_id=?", (book_id,)).fetchone()
        if not book:
            return style + "<h3>❌ Book not found</h3><div class='center'><a class='btn' href='/admin'>⬅️ Back</a></div>" + end()
        
        conn.execute("INSERT INTO Transactions (patron_id, book_id, borrow_date, return_date, fine, item_type) VALUES (?,?,?,?,?,?)",
                    (patron_id, book_id, request.form.get("borrow_date"),
                     request.form.get("return_date") or None, float(fine), request.form.get("item_type", "Physical")))
        conn.commit()
    except Exception as e:
        print(f"Error creating transaction: {e}")
    return redirect("/admin")

@app.route("/admin/update/txn/<int:id>", methods=["POST"])
def admin_update_txn(id):
    try:
        patron_id = request.form.get("patron_id")
        book_id = request.form.get("book_id")
        borrow_date = request.form.get("borrow_date")
        return_date = request.form.get("return_date")
        fine = request.form.get("fine")
        item_type = request.form.get("item_type")
        
        conn = get_db()
        updates = []
        params = []
        
        if patron_id and patron_id.strip():
            updates.append("patron_id = ?")
            params.append(int(patron_id))
        if book_id and book_id.strip():
            updates.append("book_id = ?")
            params.append(int(book_id))
        if borrow_date and borrow_date.strip():
            updates.append("borrow_date = ?")
            params.append(borrow_date)
        if return_date is not None:
            updates.append("return_date = ?")
            params.append(return_date if return_date.strip() else None)
        if fine is not None and fine.strip():
            updates.append("fine = ?")
            params.append(float(fine))
        if item_type and item_type.strip():
            updates.append("item_type = ?")
            params.append(item_type)
        
        if updates:
            params.append(id)
            query = f"UPDATE Transactions SET {', '.join(updates)} WHERE transaction_id = ?"
            conn.execute(query, params)
            conn.commit()
    except Exception as e:
        print(f"Error updating transaction {id}: {e}")
    
    return redirect("/admin")

@app.route("/admin/delete/txn/<int:id>", methods=["POST"])
def admin_delete_txn(id):
    try:
        conn = get_db()
        conn.execute("DELETE FROM Transactions WHERE transaction_id=?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting transaction {id}: {e}")
    return redirect("/admin")

# ==================== LIBRARIAN ====================
@app.route("/librarian")
def librarian():
    if session.get("role") != "Librarian": 
        return redirect("/login_librarian")
    
    conn = get_db()
    
    # Statistics for Librarian
    total_books = conn.execute("SELECT COUNT(*) as count FROM Books").fetchone()["count"]
    borrowed_books = conn.execute("SELECT COUNT(*) as count FROM Books WHERE available=0").fetchone()["count"]
    available_books = conn.execute("SELECT COUNT(*) as count FROM Books WHERE available=1").fetchone()["count"]
    
    # Total fines in the system
    total_fines_result = conn.execute("SELECT SUM(fine) as total FROM Transactions").fetchone()
    total_fines = total_fines_result["total"] or 0
    
    books = conn.execute("SELECT * FROM Books").fetchall()
    
    html = style + "<h2>📚 Librarian panel</h2>"
    html += "<p class='muted center'>Full CRUD Books + Return Process</p>"
    
    # Statistics Section
    html += """
    <div class='section'>
      <h3>📊 Library Statistics</h3>
      <div class='stats-grid'>
        <div class='stat-box'>
          <div class='stat-value'>{}</div>
          <div class='stat-label'>Total Books</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>{}</div>
          <div class='stat-label'>Available</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>{}</div>
          <div class='stat-label'>Borrowed</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>RM {:.2f}</div>
          <div class='stat-label'>Total Fines</div>
        </div>
      </div>
    </div>
    """.format(total_books, available_books, borrowed_books, total_fines)
    
    html += "<div class='hr'></div>"
    
    # Add Book Form
    html += """
    <div class='section'>
      <div class='card'>
        <h3>➕ Add New Book</h3>
        <form method='POST' action='/librarian/create'>
          <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 15px;'>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Title *</label>
              <input name='title' placeholder='Book Title' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Author *</label>
              <input name='author' placeholder='Author Name' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>ISBN *</label>
              <input name='isbn' placeholder='ISBN Number' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Published Year *</label>
              <input name='published_year' placeholder='e.g., 2023' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Genre *</label>
              <input name='genre' placeholder='e.g., Fiction, Science' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Type *</label>
              <select name='type' required style='width: 100%;'>
                <option value=''>Select Type</option>
                <option value='Physical'>Physical</option>
                <option value='E-book'>E-book</option>
                <option value='Audiobook'>Audiobook</option>
                <option value='Reference'>Reference</option>
              </select>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Call Number *</label>
              <input name='call_number' placeholder='e.g., FIC-SCI-001' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Shelf Location</label>
              <input name='shelf_location' placeholder='e.g., Shelf A-5' style='width: 100%;'>
            </div>
          </div>
          <div style='text-align: center; margin-top: 20px;'>
            <button class='btn' type='submit'>➕ Add Book</button>
          </div>
        </form>
      </div>
    </div>
    <div class='hr'></div>
    """
    
    # Books List with Full CRUD
    html += "<h3>📚 All Books</h3>"
    html += "<div class='section'><div class='grid'>"
    for b in books:
        status = "Available ✅" if b['available'] else "Borrowed ❌"
        type_class = f"type-{b['type'].lower().replace('-', '').replace(' ', '')}"
        
        html += f"""
        <div class='card'>
          <h3>{b['title'] or '-'} <span class='pill'>{status}</span></h3>
          <p><strong>Author:</strong> {b['author'] or '-'}</p>
          <p><strong>Genre:</strong> {b['genre'] or '-'} <span class='book-type {type_class}'>{b['type'] or '-'}</span></p>
          <p><strong>Call #:</strong> {b['call_number'] or '-'}</p>
          <div class='actions'>
            <a class='btn btn-small' href='/librarian/view/{b['book_id']}'>👁️ View</a>
            <a class='btn btn-small' href='/librarian/edit/{b['book_id']}'>✏️ Edit</a>
            {'' if b['available'] else f"""
            <form class='inline' method='POST' action='/librarian/return_book/{b['book_id']}'>
              <button class='btn btn-small btn-warning' type='submit' onclick='return confirm("Process return for this book?")'>📖 Return Book</button>
            </form>
            """}
            <form class='inline' method='POST' action='/librarian/delete/{b['book_id']}'>
              <button class='btn btn-small btn-danger' type='submit' onclick='return confirm("Delete this book?")'>🗑️ Delete</button>
            </form>
          </div>
        </div>
        """
    html += "</div></div>"
    
    html += "<div class='center'><a class='btn' href='/'>⬅️ Kembali</a></div>"
    return html + end()

@app.route("/librarian/view/<int:id>")
def librarian_view(id):
    if session.get("role") != "Librarian": 
        return redirect("/login_librarian")
    
    conn = get_db()
    b = conn.execute("SELECT * FROM Books WHERE book_id=?", (id,)).fetchone()
    
    if not b: 
        return style + "<h3>❌ Book not found</h3><div class='center'><a class='btn' href='/librarian'>⬅️ Back</a></div>" + end()
    
    status = "Available ✅" if b['available'] else "Borrowed ❌"
    type_class = f"type-{b['type'].lower().replace('-', '').replace(' ', '')}"
    
    return style + f"""
      <h2>👁️ Book Details</h2>
      <div class='card'>
        <h3>{b['title'] or '-'}</h3>
        <div class='book-details'>
          <div class='detail-item'>
            <strong>Author:</strong><br>{b['author'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>ISBN:</strong><br>{b['isbn'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Published Year:</strong><br>{b['published_year'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Genre:</strong><br>{b['genre'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Type:</strong><br><span class='book-type {type_class}'>{b['type'] or '-'}</span>
          </div>
          <div class='detail-item'>
            <strong>Call Number:</strong><br>{b['call_number'] or '-'}
          </div>
          <div class='detail-item'>
            <strong>Shelf Location:</strong><br>{b['shelf_location'] or 'Not specified'}
          </div>
          <div class='detail-item'>
            <strong>Status:</strong><br>{status}
          </div>
        </div>
        <p><strong>Book ID:</strong> {b['book_id']}</p>
      </div>
      <div class='actions' style='justify-content: center; margin-top: 20px;'>
        <a class='btn' href='/librarian/edit/{id}'>✏️ Edit Book</a>
        {'' if b['available'] else f"""
        <form class='inline' method='POST' action='/librarian/return_book/{id}'>
          <button class='btn btn-warning' type='submit'>📖 Return Book</button>
        </form>
        """}
        <a class='btn' href='/librarian'>⬅️ Back to Librarian</a>
      </div>
    """ + end()

@app.route("/librarian/edit/<int:id>", methods=["GET", "POST"])
def librarian_edit(id):
    if session.get("role") != "Librarian": 
        return redirect("/login_librarian")
    
    conn = get_db()
    b = conn.execute("SELECT * FROM Books WHERE book_id=?", (id,)).fetchone()
    
    if not b:
        return style + "<h3>❌ Book not found</h3><div class='center'><a class='btn' href='/librarian'>⬅️ Back</a></div>" + end()
    
    if request.method == "POST":
        # Update book
        title = request.form.get("title", b['title'])
        author = request.form.get("author", b['author'])
        isbn = request.form.get("isbn", b['isbn'])
        published_year = request.form.get("published_year", b['published_year'])
        genre = request.form.get("genre", b['genre'])
        book_type = request.form.get("type", b['type'])
        call_number = request.form.get("call_number", b['call_number'])
        shelf_location = request.form.get("shelf_location", b['shelf_location'])
        available = request.form.get("available", b['available'])
        
        try:
            conn.execute("""
                UPDATE Books 
                SET title=?, author=?, isbn=?, published_year=?, genre=?, type=?, 
                    call_number=?, shelf_location=?, available=?
                WHERE book_id=?
            """, (title, author, isbn, published_year, genre, book_type, 
                 call_number, shelf_location, int(available), id))
            conn.commit()
            return redirect(f"/librarian/view/{id}")
        except Exception as e:
            error_msg = f"<p style='color:#ff6b6b;'>Error updating book: {str(e)}</p>"
    
    # GET request - show edit form
    return style + f"""
      <h2>✏️ Edit Book</h2>
      <div class='card' style='max-width: 800px; margin: 30px auto;'>
        <form method='POST'>
          <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px;'>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Title *</label>
              <input name='title' value='{b['title'] or ''}' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Author *</label>
              <input name='author' value='{b['author'] or ''}' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>ISBN *</label>
              <input name='isbn' value='{b['isbn'] or ''}' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Published Year *</label>
              <input name='published_year' value='{b['published_year'] or ''}' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Genre *</label>
              <input name='genre' value='{b['genre'] or ''}' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Type *</label>
              <select name='type' required style='width: 100%;'>
                <option value='Physical' {'selected' if b['type'] == 'Physical' else ''}>Physical</option>
                <option value='E-book' {'selected' if b['type'] == 'E-book' else ''}>E-book</option>
                <option value='Audiobook' {'selected' if b['type'] == 'Audiobook' else ''}>Audiobook</option>
                <option value='Reference' {'selected' if b['type'] == 'Reference' else ''}>Reference</option>
              </select>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Call Number *</label>
              <input name='call_number' value='{b['call_number'] or ''}' required style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Shelf Location</label>
              <input name='shelf_location' value='{b['shelf_location'] or ''}' style='width: 100%;'>
            </div>
            <div>
              <label style='display: block; margin-bottom: 8px;'>Availability *</label>
              <select name='available' required style='width: 100%;'>
                <option value='1' {'selected' if b['available'] == 1 else ''}>Available</option>
                <option value='0' {'selected' if b['available'] == 0 else ''}>Borrowed</option>
              </select>
            </div>
          </div>
          
          <div style='margin-top: 30px; text-align: center;'>
            <button class='btn' type='submit'>💾 Save Changes</button>
            <a class='btn' href='/librarian/view/{id}'>❌ Cancel</a>
          </div>
        </form>
      </div>
    """ + end()

@app.route("/librarian/create", methods=["POST"])
def librarian_create():
    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO Books (title, author, isbn, published_year, genre, type, call_number, shelf_location, available) 
            VALUES (?,?,?,?,?,?,?,?,1)
        """, (
            request.form["title"], 
            request.form["author"], 
            request.form["isbn"], 
            request.form["published_year"], 
            request.form["genre"], 
            request.form["type"],
            request.form["call_number"], 
            request.form.get("shelf_location", "")
        ))
        conn.commit()
    except Exception as e:
        print(f"Error creating book: {e}")
    return redirect("/librarian")

@app.route("/librarian/return_book/<int:book_id>", methods=["POST"])
def librarian_return_book(book_id):
    if session.get("role") != "Librarian": 
        return redirect("/login_librarian")
    
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Get the active transaction first to calculate fine
        transaction = conn.execute("""
            SELECT * FROM Transactions 
            WHERE book_id = ? AND return_date IS NULL
            ORDER BY transaction_id DESC LIMIT 1
        """, (book_id,)).fetchone()
        
        if transaction:
            # Calculate final fine
            final_fine = calculate_fine(transaction['borrow_date'], today)
            
            # Update transaction with return date and final fine
            conn.execute("""
                UPDATE Transactions 
                SET return_date = ?, fine = ?
                WHERE transaction_id = ?
            """, (today, final_fine, transaction['transaction_id']))
            
            # Update book availability (hanya untuk physical books)
            book = conn.execute("SELECT type FROM Books WHERE book_id=?", (book_id,)).fetchone()
            if book and book['type'] == 'Physical':
                conn.execute("UPDATE Books SET available=1 WHERE book_id=?", (book_id,))
            
            conn.commit()
    except Exception as e:
        print(f"Error returning book: {e}")
    
    return redirect("/librarian")

@app.route("/librarian/delete/<int:id>", methods=["POST"])
def librarian_delete(id):
    try:
        conn = get_db()
        conn.execute("DELETE FROM Books WHERE book_id=?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting book {id}: {e}")
    return redirect("/librarian")

# ==================== STUDENT ====================
@app.route("/student")
def student():
    if session.get("role") != "Student": 
        return redirect("/login_student")

    patron_id = session.get("patron_id")
    name = session.get("name")
    conn = get_db()

    # Get current loans (not returned)
    txns = conn.execute("""
        SELECT t.*, b.title, b.author, b.type
        FROM Transactions t 
        JOIN Books b ON t.book_id = b.book_id 
        WHERE t.patron_id=? AND t.return_date IS NULL
        ORDER BY t.borrow_date DESC
    """, (patron_id,)).fetchall()
    
    # Get returned loans
    returned_txns = conn.execute("""
        SELECT t.*, b.title, b.author 
        FROM Transactions t 
        JOIN Books b ON t.book_id = b.book_id 
        WHERE t.patron_id=? AND t.return_date IS NOT NULL
        ORDER BY t.return_date DESC
        LIMIT 10
    """, (patron_id,)).fetchall()
    
    # Get total fine for this student
    total_fine = get_patron_total_fine(patron_id)
    
    # Get books that are actually available (not borrowed by this student)
    borrowed_book_ids = [t['book_id'] for t in txns]
    available_books = []
    
    if borrowed_book_ids:
        # Exclude books currently borrowed by this student
        available_books = conn.execute("""
            SELECT * FROM Books 
            WHERE available=1 OR book_id NOT IN ({})
            ORDER BY title
        """.format(','.join('?' * len(borrowed_book_ids))), borrowed_book_ids).fetchall()
    else:
        available_books = conn.execute("SELECT * FROM Books WHERE available=1 ORDER BY title").fetchall()

    html = style + f"<h2>🎓 Student panel — {name}</h2>"
    
    # Student Statistics
    current_loans = len(txns)
    returned_loans = len(returned_txns)
    
    html += f"""
    <div class='section'>
      <div class='stats-grid'>
        <div class='stat-box'>
          <div class='stat-value'>{current_loans}</div>
          <div class='stat-label'>Current Loans</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>{returned_loans}</div>
          <div class='stat-label'>Returned Books</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>RM {total_fine:.2f}</div>
          <div class='stat-label'>Total Fine Due</div>
        </div>
      </div>
    </div>
    """
    
    html += "<div class='hr'></div>"

    # Current Loans with Return Button
    html += "<div class='section'><h3>📚 Current Loans</h3>"
    if txns:
        html += "<div class='grid'>"
        for t in txns:
            borrow = t["borrow_date"] or "-"
            fine = t["fine"] if t["fine"] is not None else 0
            
            # Calculate days since borrowed
            days_borrowed = 0
            try:
                borrow_dt = datetime.strptime(borrow, "%Y-%m-%d")
                days_borrowed = (datetime.now() - borrow_dt).days
            except:
                pass
            
            # Calculate overdue days
            overdue_days = max(0, days_borrowed - 14)
            
            overdue_html = ""
            if overdue_days > 0:
                overdue_html = f"<div class='fine-due'><strong>⚠️ Overdue:</strong> {overdue_days} days</div>"
            
            html += f"""
            <div class='card'>
              <h3>{t['title'] or '-'}</h3>
              <p><strong>Author:</strong> {t['author'] or '-'}</p>
              <p><strong>Type:</strong> {t['type'] or '-'}</p>
              <p><strong>Borrowed:</strong> {borrow} ({days_borrowed} days ago)</p>
              <p><strong>Fine:</strong> RM {float(fine):.2f}</p>
              {overdue_html}
              <div class='actions'>
                <form class='inline' method='POST' action='/student/return/{t['transaction_id']}'>
                  <input type='hidden' name='book_id' value='{t['book_id']}'>
                  <button class='btn btn-warning' type='submit' onclick='return confirm("Return this book?")'>📖 Return Book</button>
                </form>
              </div>
            </div>
            """
        html += "</div>"
    else:
        html += "<p class='muted center'>You have no current loans.</p>"
    html += "</div>"
    
    # TAMBAH: View My Borrow Books Button
    html += """
    <div class='section center'>
      <a class='btn' href='/student/my_borrow_books'>📚 View My Borrow Books</a>
    </div>
    <div class='hr'></div>
    """

    # Returned Loans History
    if returned_txns:
        html += "<div class='section'><h3>📋 Returned Loans History</h3>"
        html += "<div class='grid'>"
        for t in returned_txns:
            borrow = t["borrow_date"] or "-"
            ret = t["return_date"] or "-"
            fine = t["fine"] if t["fine"] is not None else 0
            html += f"""
            <div class='card'>
              <h3>{t['title'] or '-'}</h3>
              <p><strong>Author:</strong> {t['author'] or '-'}</p>
              <p><strong>Borrowed:</strong> {borrow}</p>
              <p><strong>Returned:</strong> {ret}</p>
              <p><strong>Fine Paid:</strong> RM {float(fine):.2f}</p>
            </div>
            """
        html += "</div></div>"
        html += "<div class='hr'></div>"

    # Available books for borrowing (excluding already borrowed)
    html += "<div class='section'><h3>📚 Available Books to Borrow</h3>"
    if available_books:
        html += "<div class='grid'>"
        for b in available_books:
            type_class = f"type-{b['type'].lower().replace('-', '').replace(' ', '')}"
            
            # Check if this book is already borrowed by this student
            already_borrowed = b['book_id'] in borrowed_book_ids
            
            if already_borrowed:
                # Find the transaction for this book
                current_txn = next((t for t in txns if t['book_id'] == b['book_id']), None)
                if current_txn:
                    html += f"""
                    <div class='card'>
                      <h3>{b['title'] or '-'} <span class='pill'>Already Borrowed</span></h3>
                      <p><strong>Author:</strong> {b['author'] or '-'}</p>
                      <p><strong>Genre:</strong> {b['genre'] or '-'} <span class='book-type {type_class}'>{b['type'] or '-'}</span></p>
                      <p><strong>Call #:</strong> {b['call_number'] or '-'}</p>
                      <p><strong>Borrowed on:</strong> {current_txn['borrow_date']}</p>
                      <div class='actions'>
                        <form class='inline' method='POST' action='/student/return/{current_txn['transaction_id']}'>
                          <button class='btn btn-warning' type='submit' onclick='return confirm("Return this book?")'>📖 Return First</button>
                        </form>
                      </div>
                    </div>
                    """
            else:
                # Book is available for borrowing
                html += f"""
                <div class='card'>
                  <h3>{b['title'] or '-'}</h3>
                  <p><strong>Author:</strong> {b['author'] or '-'}</p>
                  <p><strong>Genre:</strong> {b['genre'] or '-'} <span class='book-type {type_class}'>{b['type'] or '-'}</span></p>
                  <p><strong>Call #:</strong> {b['call_number'] or '-'}</p>
                  <form method='POST' action='/student/borrow' class='actions'>
                    <input type='hidden' name='book_id' value='{b['book_id']}'>
                    <label style='display:block; margin-bottom:5px;'>Borrow Date:</label>
                    <input type='date' name='borrow_date' value='""" + datetime.now().strftime("%Y-%m-%d") + """' required>
                    <button class='btn' type='submit'>📖 Borrow This Book</button>
                  </form>
                </div>
                """
        html += "</div>"
    else:
        html += "<p class='muted center'>No available books at the moment.</p>"
    html += "</div>"
    
    html += "<div class='center'><a class='btn' href='/'>⬅️ Kembali</a></div>"
    return html + end()

# TAMBAH: View My Borrow Books Page
@app.route("/student/my_borrow_books")
def student_my_borrow_books():
    if session.get("role") != "Student": 
        return redirect("/login_student")

    patron_id = session.get("patron_id")
    name = session.get("name")
    conn = get_db()

    # Get ALL loans for this student (both current and returned)
    all_loans = conn.execute("""
        SELECT t.*, b.title, b.author, b.genre, b.type, b.call_number
        FROM Transactions t 
        JOIN Books b ON t.book_id = b.book_id 
        WHERE t.patron_id=?
        ORDER BY t.borrow_date DESC
    """, (patron_id,)).fetchall()
    
    # Statistics
    total_loans = len(all_loans)
    current_loans = len([t for t in all_loans if t['return_date'] is None])
    returned_loans = total_loans - current_loans
    total_fine_paid = sum(float(t['fine'] or 0) for t in all_loans if t['return_date'] is not None)
    current_fine = sum(float(t['fine'] or 0) for t in all_loans if t['return_date'] is None)
    
    html = style + f"""
      <h2>📚 My Borrow Books — {name}</h2>
      <p class='muted center'>Complete borrowing history</p>
      
      <div class='section'>
        <div class='stats-grid'>
          <div class='stat-box'>
            <div class='stat-value'>{total_loans}</div>
            <div class='stat-label'>Total Books Borrowed</div>
          </div>
          <div class='stat-box'>
            <div class='stat-value'>{current_loans}</div>
            <div class='stat-label'>Currently Borrowed</div>
          </div>
          <div class='stat-box'>
            <div class='stat-value'>{returned_loans}</div>
            <div class='stat-label'>Returned Books</div>
          </div>
          <div class='stat-box'>
            <div class='stat-value'>RM {current_fine:.2f}</div>
            <div class='stat-label'>Current Fine Due</div>
          </div>
          <div class='stat-box'>
            <div class='stat-value'>RM {total_fine_paid:.2f}</div>
            <div class='stat-label'>Total Fine Paid</div>
          </div>
        </div>
      </div>
    """
    
    if all_loans:
        html += "<div class='section'><h3>📋 All My Borrowed Books</h3><div class='grid'>"
        for t in all_loans:
            borrow = t["borrow_date"] or "-"
            ret = t["return_date"] or "Not returned"
            fine = t["fine"] if t["fine"] is not None else 0
            status = "Returned ✅" if t['return_date'] else "Borrowed 📖"
            type_class = f"type-{t['type'].lower().replace('-', '').replace(' ', '')}"
            
            # Calculate days borrowed
            days_info = ""
            try:
                borrow_dt = datetime.strptime(borrow, "%Y-%m-%d")
                if t['return_date']:
                    return_dt = datetime.strptime(t['return_date'], "%Y-%m-%d")
                    days_borrowed = (return_dt - borrow_dt).days
                    days_info = f"<p><strong>Duration:</strong> {days_borrowed} days</p>"
                else:
                    days_borrowed = (datetime.now() - borrow_dt).days
                    days_info = f"<p><strong>Days since borrowed:</strong> {days_borrowed} days</p>"
                    
                    # Overdue warning
                    if days_borrowed > 14:
                        overdue_days = days_borrowed - 14
                        days_info += f"<div class='fine-due'><strong>⚠️ Overdue:</strong> {overdue_days} days</div>"
            except:
                pass
            
            html += f"""
            <div class='card'>
              <h3>{t['title'] or '-'} <span class='pill'>{status}</span></h3>
              <p><strong>Author:</strong> {t['author'] or '-'}</p>
              <p><strong>Genre:</strong> {t['genre'] or '-'} <span class='book-type {type_class}'>{t['type'] or '-'}</span></p>
              <p><strong>Call #:</strong> {t['call_number'] or '-'}</p>
              <p><strong>Borrow Date:</strong> {borrow}</p>
              <p><strong>Return Date:</strong> {ret}</p>
              <p><strong>Fine:</strong> RM {float(fine):.2f}</p>
              {days_info}
              {'' if t['return_date'] else f"""
              <div class='actions'>
                <form class='inline' method='POST' action='/student/return/{t['transaction_id']}'>
                  <button class='btn btn-warning' type='submit' onclick='return confirm("Return this book?")'>📖 Return Now</button>
                </form>
              </div>
              """}
            </div>
            """
        html += "</div></div>"
    else:
        html += "<p class='muted center'>You haven't borrowed any books yet.</p>"
    
    html += """
    <div class='center'>
      <a class='btn' href='/student'>⬅️ Back to Student Panel</a>
    </div>
    """
    
    return html + end()

@app.route("/student/borrow", methods=["POST"])
def student_borrow():
    if session.get("role") != "Student": 
        return redirect("/login_student")
    
    patron_id = session.get("patron_id")
    book_id = request.form["book_id"]
    borrow_date = request.form["borrow_date"]
    
    conn = get_db()
    
    # Check if student already borrowed this book
    existing_loan = conn.execute("""
        SELECT * FROM Transactions 
        WHERE patron_id=? AND book_id=? AND return_date IS NULL
    """, (patron_id, book_id)).fetchone()
    
    if existing_loan:
        return style + f"""
            <h3>❌ You already borrowed this book!</h3>
            <p>You borrowed this book on {existing_loan['borrow_date']}</p>
            <div class='center'>
                <a class='btn' href='/student'>⬅️ Back to Student Panel</a>
            </div>
        """ + end()
    
    # Check if book is available (for physical books)
    book = conn.execute("SELECT available, type FROM Books WHERE book_id=?", (book_id,)).fetchone()
    if not book:
        return style + "<h3>❌ Book not found</h3><div class='center'><a class='btn' href='/student'>⬅️ Back</a></div>" + end()
    
    try:
        item_type = book['type'] if book else 'Physical'
        
        conn.execute("""
            INSERT INTO Transactions (patron_id, book_id, borrow_date, return_date, fine, item_type) 
            VALUES (?,?,?,?,?,?)
        """, (patron_id, book_id, borrow_date, None, 0, item_type))
        
        # Only update availability for physical books
        if item_type == 'Physical':
            conn.execute("UPDATE Books SET available=0 WHERE book_id=?", (book_id,))
        
        conn.commit()
    except Exception as e:
        print(f"Error borrowing book: {e}")
        return style + f"""
            <h3>❌ Error borrowing book</h3>
            <p>{str(e)}</p>
            <div class='center'>
                <a class='btn' href='/student'>⬅️ Back to Student Panel</a>
            </div>
        """ + end()
    
    return redirect("/student")

@app.route("/student/return/<int:transaction_id>", methods=["POST"])
def student_return(transaction_id):
    if session.get("role") != "Student": 
        return redirect("/login_student")
    
    patron_id = session.get("patron_id")
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Get transaction details
        txn = conn.execute("""
            SELECT book_id, item_type, borrow_date FROM Transactions 
            WHERE transaction_id=? AND patron_id=? AND return_date IS NULL
        """, (transaction_id, patron_id)).fetchone()
        
        if txn:
            book_id = txn['book_id']
            item_type = txn['item_type']
            
            # Calculate final fine
            final_fine = calculate_fine(txn['borrow_date'], today)
            
            # Update transaction with return date and final fine
            conn.execute("""
                UPDATE Transactions 
                SET return_date = ?, fine = ?
                WHERE transaction_id = ? AND patron_id = ?
            """, (today, final_fine, transaction_id, patron_id))
            
            # Update book availability (hanya untuk physical books)
            if item_type == 'Physical':
                conn.execute("UPDATE Books SET available=1 WHERE book_id=?", (book_id,))
            
            conn.commit()
    except Exception as e:
        print(f"Error returning book: {e}")
    
    return redirect("/student")

# ==================== BANK ====================
@app.route("/bank")
def bank():
    if session.get("role") != "Bank": 
        return redirect("/login_bank")
    
    conn = get_db()
    
    # Get all payments
    payments = conn.execute("SELECT * FROM Payments ORDER BY payment_date DESC").fetchall()
    
    # Bank Statistics
    total_payments = conn.execute("SELECT COUNT(*) as count FROM Payments").fetchone()["count"]
    total_received = conn.execute("SELECT SUM(amount) as total FROM Payments").fetchone()["total"] or 0
    avg_payment = conn.execute("SELECT AVG(amount) as avg FROM Payments").fetchone()["avg"] or 0
    
    # Get patrons with outstanding fines
    patrons_with_fines = conn.execute("""
        SELECT p.patron_id, p.name, p.role, SUM(t.fine) as total_fine
        FROM Patron p
        JOIN Transactions t ON p.patron_id = t.patron_id
        WHERE t.return_date IS NULL AND t.fine > 0
        GROUP BY p.patron_id
        ORDER BY total_fine DESC
    """).fetchall()

    html = style + "<h2>🏦 Bank panel</h2>"
    html += "<p class='muted center'>Manage payments and view outstanding fines</p>"
    
    # Statistics Section
    html += """
    <div class='section'>
      <h3>💰 Bank Statistics</h3>
      <div class='stats-grid'>
        <div class='stat-box'>
          <div class='stat-value'>{}</div>
          <div class='stat-label'>Total Payments</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>RM {:.2f}</div>
          <div class='stat-label'>Total Received</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>RM {:.2f}</div>
          <div class='stat-label'>Average Payment</div>
        </div>
        <div class='stat-box'>
          <div class='stat-value'>{}</div>
          <div class='stat-label'>Patrons with Fines</div>
        </div>
      </div>
    </div>
    """.format(total_payments, total_received, avg_payment, len(patrons_with_fines))
    
    html += "<div class='hr'></div>"
    
    # Patrons with Outstanding Fines
    if patrons_with_fines:
        html += "<div class='section'><h3>📋 Patrons with Outstanding Fines</h3><div class='grid'>"
        for p in patrons_with_fines:
            html += f"""
            <div class='card'>
              <h3>{p['name']} <span class='pill'>{p['role']}</span></h3>
              <p><strong>Patron ID:</strong> {p['patron_id']}</p>
              <div class='fine-due'>
                <strong>Outstanding Fine:</strong> RM {float(p['total_fine']):.2f}
              </div>
            </div>
            """
        html += "</div></div><div class='hr'></div>"
    
    # Payment Records
    html += "<div class='section'><h3>💳 Payment Records</h3><div class='grid'>"
    for p in payments:
        amount = p["amount"] or 0
        date = p["payment_date"] or "-"
        purpose = p["purpose"] or "-"
        
        # Get patron name
        patron = conn.execute("SELECT name FROM Patron WHERE patron_id=?", (p['patron_id'],)).fetchone()
        patron_name = patron['name'] if patron else f"Patron #{p['patron_id']}"
        
        html += f"""
        <div class='card'>
          <h3>Payment #{p['payment_id']}</h3>
          <p><strong>Patron:</strong> {patron_name} (ID: {p['patron_id']})</p>
          <p><strong>Amount:</strong> RM {float(amount):.2f}</p>
          <p><strong>Date:</strong> {date}</p>
          <p><strong>Purpose:</strong> {purpose}</p>
          <div class='actions'>
            <a class='btn btn-small' href='/bank/view/{p['payment_id']}'>👁️ View</a>
            <form class='inline' method='POST' action='/bank/update/{p['payment_id']}'>
              <input name='patron_id' placeholder='New patron ID'>
              <input name='amount' placeholder='New amount'>
              <input name='payment_date' placeholder='New date'>
              <input name='purpose' placeholder='New purpose'>
              <button class='btn btn-small'>✏️ Update</button>
            </form>
            <form class='inline' method='POST' action='/bank/delete/{p['payment_id']}'>
              <button class='btn btn-small btn-danger'>🗑️ Delete</button>
            </form>
          </div>
        </div>
        """
    html += "</div></div><div class='hr'></div>"
    
    # Quick Payment Form with AUTO-FINE CALCULATION
    html += """
    <div class='section'>
      <div class='card'>
        <h3>💳 Quick Payment Entry (Auto Fine Calculation)</h3>
        <form method='POST' action='/bank/create'>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Patron ID *</label>
            <input type='number' name='patron_id' id='patron_id' placeholder='Enter Patron ID' required 
                   onchange='checkPatronFine(this.value)'>
            <div id='patron_fine_info' style='margin-top:10px; display:none;'></div>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Amount (RM) *</label>
            <input type='number' name='amount' id='amount' placeholder='Auto-filled from fine' step='0.01' required 
                   style='background:rgba(255,255,255,0.05);'>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Payment Date *</label>
            <input type='date' name='payment_date' value='""" + datetime.now().strftime("%Y-%m-%d") + """' required>
          </div>
          <div style='margin-bottom:15px;'>
            <label style='display:block; margin-bottom:5px;'>Purpose *</label>
            <input name='purpose' id='purpose' value='Fine Payment' required>
          </div>
          <button class='btn' type='submit'>💾 Record Payment</button>
        </form>
      </div>
    </div>
    
    <script>
    function checkPatronFine(patronId) {
        if (!patronId) return;
        
        fetch('/check_patron_fine/' + patronId)
            .then(response => response.json())
            .then(data => {
                const infoDiv = document.getElementById('patron_fine_info');
                const amountInput = document.getElementById('amount');
                const purposeInput = document.getElementById('purpose');
                
                if (data.patron_exists) {
                    if (data.total_fine > 0) {
                        infoDiv.innerHTML = `<div class='fine-due'>
                            <strong>⚠️ This patron has outstanding fines!</strong><br>
                            Total Fine Due: RM ${data.total_fine.toFixed(2)}<br>
                            Currently Borrowed: ${data.total_borrowed} books
                        </div>`;
                        amountInput.value = data.total_fine.toFixed(2);
                        purposeInput.value = 'Fine Payment';
                    } else {
                        infoDiv.innerHTML = `<div style='background:rgba(0,255,0,0.1); padding:10px; border-radius:8px;'>
                            ✅ This patron has no outstanding fines<br>
                            Enter payment amount manually
                        </div>`;
                        amountInput.value = '';
                        purposeInput.value = 'Other Payment';
                    }
                    infoDiv.style.display = 'block';
                } else {
                    infoDiv.innerHTML = `<div style='background:rgba(255,255,0,0.1); padding:10px; border-radius:8px;'>
                        ⚠️ Patron ID not found in system<br>
                        Enter payment manually
                    </div>`;
                    infoDiv.style.display = 'block';
                    amountInput.value = '';
                    purposeInput.value = 'Payment';
                }
            });
    }
    </script>
    """
    
    # Search Payment by Patron ID
    html += """
    <div class='section'>
      <div class='card'>
        <h3>🔍 Search Payments by Patron</h3>
        <form method='POST' action='/bank/search_payments' style='text-align: center;'>
          <input name='patron_id' placeholder='Enter Patron ID' required>
          <button class='btn' type='submit'>🔍 Search</button>
        </form>
      </div>
    </div>
    """
    
    html += "<div class='center'><a class='btn' href='/'>⬅️ Kembali</a></div>"
    return html + end()

@app.route("/bank/search_payments", methods=["POST"])
def bank_search_payments():
    if session.get("role") != "Bank": 
        return redirect("/login_bank")
    
    patron_id = request.form.get("patron_id")
    conn = get_db()
    
    # Get patron info
    patron = conn.execute("SELECT * FROM Patron WHERE patron_id=?", (patron_id,)).fetchone()
    
    if not patron:
        return style + """
            <h3>❌ Patron not found</h3>
            <div class='center'>
                <a class='btn' href='/bank'>⬅️ Back to Bank</a>
            </div>
        """ + end()
    
    # Get payments for this patron
    payments = conn.execute("SELECT * FROM Payments WHERE patron_id=? ORDER BY payment_date DESC", (patron_id,)).fetchall()
    
    # Calculate total paid
    total_paid_result = conn.execute("SELECT SUM(amount) as total FROM Payments WHERE patron_id=?", (patron_id,)).fetchone()
    total_paid = total_paid_result["total"] or 0
    
    # Calculate outstanding fines
    outstanding_fines = get_patron_total_fine(patron_id)
    
    html = style + f"""
        <h2>💰 Payment History for {patron['name']}</h2>
        <div class='card' style='max-width: 800px; margin: 20px auto;'>
            <div class='book-details'>
                <div class='detail-item'>
                    <strong>Patron ID:</strong><br>{patron['patron_id']}
                </div>
                <div class='detail-item'>
                    <strong>Name:</strong><br>{patron['name']}
                </div>
                <div class='detail-item'>
                    <strong>Role:</strong><br>{patron['role']}
                </div>
                <div class='detail-item'>
                    <strong>Email:</strong><br>{patron['email']}
                </div>
                <div class='detail-item fine-due'>
                    <strong>Outstanding Fines:</strong><br>RM {outstanding_fines:.2f}
                </div>
                <div class='detail-item' style='background: rgba(0,255,0,0.1);'>
                    <strong>Total Paid:</strong><br>RM {total_paid:.2f}
                </div>
            </div>
        </div>
    """
    
    if payments:
        html += "<div class='section'><h3>📋 Payment Records</h3><div class='grid'>"
        for p in payments:
            html += f"""
            <div class='card'>
                <h3>Payment #{p['payment_id']}</h3>
                <p><strong>Amount:</strong> RM {float(p['amount']):.2f}</p>
                <p><strong>Date:</strong> {p['payment_date']}</p>
                <p><strong>Purpose:</strong> {p['purpose']}</p>
            </div>
            """
        html += "</div></div>"
    else:
        html += "<p class='muted center'>No payment records found for this patron.</p>"
    
    html += """
    <div class='center'>
        <a class='btn' href='/bank'>⬅️ Back to Bank</a>
    </div>
    """
    
    return html + end()

@app.route("/bank/create", methods=["POST"])
def bank_create():
    try:
        conn = get_db()
        conn.execute("INSERT INTO Payments (patron_id, amount, payment_date, purpose) VALUES (?,?,?,?)",
                    (request.form["patron_id"], request.form["amount"], request.form["payment_date"], request.form["purpose"]))
        conn.commit()
    except Exception as e:
        print(f"Error creating payment: {e}")
    return redirect("/bank")

@app.route("/bank/update/<int:id>", methods=["POST"])
def bank_update(id):
    try:
        patron_id = request.form.get("patron_id")
        amount = request.form.get("amount")
        payment_date = request.form.get("payment_date")
        purpose = request.form.get("purpose")
        
        conn = get_db()
        updates = []
        params = []
        
        if patron_id and patron_id.strip():
            updates.append("patron_id = ?")
            params.append(int(patron_id))
        if amount and amount.strip():
            updates.append("amount = ?")
            params.append(float(amount))
        if payment_date and payment_date.strip():
            updates.append("payment_date = ?")
            params.append(payment_date)
        if purpose and purpose.strip():
            updates.append("purpose = ?")
            params.append(purpose)
        
        if updates:
            params.append(id)
            query = f"UPDATE Payments SET {', '.join(updates)} WHERE payment_id = ?"
            conn.execute(query, params)
            conn.commit()
    except Exception as e:
        print(f"Error updating payment {id}: {e}")
    
    return redirect("/bank")

@app.route("/bank/delete/<int:id>", methods=["POST"])
def bank_delete(id):
    try:
        conn = get_db()
        conn.execute("DELETE FROM Payments WHERE payment_id=?", (id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting payment {id}: {e}")
    return redirect("/bank")

@app.route("/bank/view/<int:id>")
def bank_view(id):
    if session.get("role") != "Bank": 
        return redirect("/login_bank")
    
    conn = get_db()
    p = conn.execute("SELECT * FROM Payments WHERE payment_id=?", (id,)).fetchone()
    if not p: 
        return style + "<h3>❌ Not found</h3><div class='center'><a class='btn' href='/bank'>⬅️ Back</a></div>" + end()
    
    amount = p["amount"] if p["amount"] is not None else 0
    
    # Get patron info
    patron = conn.execute("SELECT name, email FROM Patron WHERE patron_id=?", (p['patron_id'],)).fetchone()
    patron_name = patron['name'] if patron else f"Patron #{p['patron_id']}"
    patron_email = patron['email'] if patron else "No email"
    
    return style + f"""
      <h2>👁️ Payment Details</h2>
      <div class='card'>
        <div class='book-details'>
          <div class='detail-item'>
            <strong>Payment ID:</strong><br>{p['payment_id']}
          </div>
          <div class='detail-item'>
            <strong>Patron:</strong><br>{patron_name}
          </div>
          <div class='detail-item'>
            <strong>Patron ID:</strong><br>{p['patron_id']}
          </div>
          <div class='detail-item'>
            <strong>Amount:</strong><br>RM {float(amount):.2f}
          </div>
          <div class='detail-item'>
            <strong>Date:</strong><br>{p['payment_date']}
          </div>
          <div class='detail-item'>
            <strong>Purpose:</strong><br>{p['purpose']}
          </div>
        </div>
      </div>
      <div class='center'><a class='btn' href='/bank'>⬅️ Back</a></div>
    """ + end()

# ==================== SEARCH BOOKS ====================
@app.route("/search_books", methods=["GET","POST"])
def search_books():
    conn = get_db()
    html = style + "<h2>🔍 Search books</h2>"
    results = []
    if request.method == "POST":
        keyword = request.form["keyword"].strip()
        results = conn.execute("SELECT * FROM Books WHERE title LIKE ? OR author LIKE ? OR genre LIKE ? OR isbn LIKE ?", 
                              (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")).fetchall()
        html += f"<p class='muted center'>Keyword: {keyword}</p>"
    html += """
      <form method='POST' class='center'>
        <input name='keyword' placeholder='Search by title, author, genre or ISBN'>
        <button class='btn'>🔍 Search</button>
      </form>
    """
    if results:
        html += "<div class='section'><div class='grid'>"
        for b in results:
            status = "Available ✅" if b['available'] else "Borrowed ❌"
            type_class = f"type-{b['type'].lower().replace('-', '').replace(' ', '')}"
            html += f"""
            <div class='card'>
              <h3>{b['title'] or '-'} <span class='pill'>{status}</span></h3>
              <p><strong>Author:</strong> {b['author'] or '-'}</p>
              <p><strong>Genre:</strong> {b['genre'] or '-'} <span class='book-type {type_class}'>{b['type'] or '-'}</span></p>
              <p><strong>Call #:</strong> {b['call_number'] or '-'}</p>
              <div class='actions'><a class='btn' href='/guest_view_book/{b['book_id']}'>👁️ View Details</a></div>
            </div>
            """
        html += "</div></div>"
    elif request.method == "POST":
        html += "<p class='muted center'>❌ No books found</p>"
    html += "<div class='center'><a class='btn' href='/'>⬅️ Kembali</a></div>"
    return html + end()

# ==================== LOGOUT ====================
@app.route("/logout")
def logout():
    session.clear()
    return style + """
      <h2>👋 Logged Out</h2>
      <div class='center'>
        <a class='btn' href='/'>🏠 Return to Home</a>
      </div>
    """ + end()

# ==================== MAIN ====================
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)