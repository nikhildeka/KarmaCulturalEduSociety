from flask import Flask, render_template_string, url_for, request, redirect, flash, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_FILE = "submissions.db"

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "karma")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "changeme")


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institution TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            owner TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_submission(institution, email, phone, address, owner):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO submissions (institution, email, phone, address, owner)
        VALUES (?, ?, ?, ?, ?)
    """, (institution, email, phone, address, owner))
    conn.commit()
    conn.close()

# ✅ Function to get all submissions
def get_submissions():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row # This allows us to access columns by name
    c = conn.cursor()
    c.execute("SELECT * FROM submissions ORDER BY submitted_at DESC")
    submissions = c.fetchall()
    conn.close()
    return submissions

# ✅ Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            flash("Logged in successfully!", "success")
            return redirect(url_for("admin"))
        else:
            flash("Invalid credentials. Please try again.", "error")
            return redirect(url_for("login"))
    
    # Login page HTML
    content = """
    <div style="max-width:400px; margin:50px auto; padding:20px; background:white; border-radius:10px; box-shadow:0 4px 8px rgba(0,0,0,0.1);">
        <h2 style="text-align:center; color:#4169e1;">Admin Login</h2>
        <form method="POST">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" required style="width:100%; padding:10px; margin-bottom:15px; border:1px solid #ccc; border-radius:5px;">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" required style="width:100%; padding:10px; margin-bottom:20px; border:1px solid #ccc; border-radius:5px;">
            <button type="submit" style="width:100%; padding:12px; background:#4169e1; color:white; border:none; border-radius:5px; cursor:pointer;">Login</button>
        </form>
    </div>
    """
    return render_template_string(base_template, title="Login", content=content)

# ✅ Admin Dashboard Route
@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        flash("You need to log in to view this page.", "error")
        return redirect(url_for("login"))

    submissions = get_submissions()
    
    table_rows = ""
    if submissions:
        for sub in submissions:
            table_rows += f"""
            <tr>
                <td>{sub['id']}</td>
                <td>{sub['institution']}</td>
                <td>{sub['email']}</td>
                <td>{sub['phone']}</td>
                <td>{sub['address']}</td>
                <td>{sub['owner']}</td>
                <td>{sub['submitted_at']}</td>
            </tr>
            """
    else:
        table_rows = """
            <tr>
                <td colspan="7">No submissions yet.</td>
            </tr>
        """
        
    content = f"""
    <div style="padding:20px;">
        <h1 style="color:#4169e1;">Admin Dashboard</h1>
        <p>Welcome, Admin! Here are the submitted requests.</p>

        <!-- ✅ Search bar -->
        <input type="text" id="searchInput" onkeyup="searchTable()" 
               placeholder="Search by any field..." 
               style="width:100%; padding:10px; margin:15px 0; border:1px solid #ccc; border-radius:5px;">

        <div style="overflow-x:auto;">
            <table id="submissionsTable" style="width:100%; border-collapse: collapse; margin-top:10px;">
                <thead>
                    <tr style="background-color:#4169e1; color:white;">
                        <th style="padding:12px; text-align:left;">ID</th>
                        <th style="padding:12px; text-align:left;">Institution</th>
                        <th style="padding:12px; text-align:left;">Email</th>
                        <th style="padding:12px; text-align:left;">Phone</th>
                        <th style="padding:12px; text-align:left;">Address</th>
                        <th style="padding:12px; text-align:left;">Owner</th>
                        <th style="padding:12px; text-align:left;">Submitted At</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
    </div>

    <!-- ✅ Search Script -->
    <script>
    function searchTable() {{
        var input = document.getElementById("searchInput");
        var filter = input.value.toLowerCase();
        var table = document.getElementById("submissionsTable");
        var trs = table.getElementsByTagName("tr");

        for (var i = 1; i < trs.length; i++) {{
            var tds = trs[i].getElementsByTagName("td");
            var show = false;
            for (var j = 0; j < tds.length; j++) {{
                if (tds[j] && tds[j].innerText.toLowerCase().indexOf(filter) > -1) {{
                    show = true;
                    break;
                }}
            }}
            trs[i].style.display = show ? "" : "none";
        }}
    }}
    </script>
    """
    return render_template_string(base_template, title="Admin Dashboard", content=content)


# ✅ Logout Route
@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# The rest of your code remains the same...
base_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
    html {
        scroll-behavior: smooth;
    }
    body {
        font-family: Arial, sans-serif;
        margin: 0;
        padding: 0;
        background: #f4f4f4;
        min-height: 100vh;
    }
    
    *, *::before, *::after {
        box-sizing: border-box;
    }
    
    html, body {
        overflow-x: hidden;
    }

    main {
        flex: 1;
        display: flex;
        flex-direction: column;
    }

    /* ✅ DEFAULT (MOBILE-FIRST) STYLES */
    header {
        background-color: #4169e1;
        color: white;
        padding: 20px;
        font-weight: bold;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    header div {
        font-size: 20px;
        text-align: center;
        margin-bottom: 10px;
    }

    nav {
        display: flex;
        flex-direction: row;
        justify-content: space-around;
        width: 100%;
    }

    nav a {
        color: white;
        text-decoration: none;
        padding: 10px;
        font-size: 16px;
        transition: color 0.3s;
    }
    nav a:hover {
        color: #ffcc00;
    }

    .notice-container {
        width: 100%;
        overflow: hidden;
        background: #ffcc00;
        padding: 8px 0;
        white-space: nowrap;
        position: relative;
    }
    .notice {
        display: inline-block;
        position: relative;
        animation: scroll-left 25s linear infinite;
        font-size: 18px;
        font-weight: bold;
        color: black;
    }
    /* ✅ FIXED ANIMATION FOR MOBILE */
    @keyframes scroll-left {
        0% {
            left: 100%;
        }
        100% {
            left: -100%;
        }
    }

    .carousel {
        position: relative;
        margin: 50px auto 20px auto;
        width: 100%;
        max-width: 900px;
        aspect-ratio: 16/9;
        overflow: hidden;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        background: #000;
    }
    
    .carousel-images img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        background-color: #000;
        border-radius: 10px;
        flex-shrink: 0;
    }

    .carousel-images {
        display: flex;
        transition: transform 0.5s ease-in-out;
    }
    
    .arrow {
        position: absolute;
        top: 50%;
        transform: translateY(-50%);
        font-size: 30px;
        color: white;
        background: rgba(0,0,0,0.5);
        border: none;
        padding: 10px;
        cursor: pointer;
        border-radius: 50%;
    }
    .arrow.left {
        left: 10px;
    }
    .arrow.right {
        right: 10px;
    }

    .main-section {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 30px;
        padding: 40px;
    }
    .left-column {
        width: 50%;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    .welcome-message, .faq-section, .affiliation-form, .why-karma {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    .welcome-message h2,
    .affiliation-form h2,
    .faq-section h2,
    .why-karma h2 {
        color: #4169e1;
    }
    .welcome-message p,
    .why-karma p {
        font-size: 18px;
        line-height: 1.6;
    }

    .affiliation-form {
        width: 50%;
    }
    .affiliation-form label {
        display: block;
        margin-bottom: 5px;
        font-weight: bold;
    }
    .affiliation-form input,
    .affiliation-form textarea {
        width: 100%;
        padding: 10px;
        margin-bottom: 15px;
        border: 1px solid #ccc;
        border-radius: 6px;
        font-size: 16px;
    }
    .affiliation-form button {
        background: #4169e1;
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        font-size: 16px;
    }
    .affiliation-form button:hover {
        background: #3154b3;
    }

    .flash {
        margin: 20px auto;
        padding: 15px;
        width: 90%;
        max-width: 600px;
        border-radius: 8px;
        text-align: center;
        font-size: 18px;
    }
    .success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }

    /* FAQ Section */
    .faq-question {
        padding: 12px;
        font-weight: bold;
        cursor: pointer;
        background: #f9f9f9;
        transition: background 0.1s;
    }
    .faq-question:hover {
        background: #efefef;
    }
    .faq-answer {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.1s ease;
        padding: 0 12px;
        font-size: 14px;
        line-height: 1.4;
    }
    .faq.active .faq-answer {
        max-height: 1000px;
        padding: 10px;
    }

    /* ✅ Footer */
    footer {
        background: #4169e1;
        color: #ddd;
        text-align: center;
        padding: 20px;
        margin-top: auto;
    }
    footer a {
        color: #ffcc00;
        margin: 0 10px;
        text-decoration: none;
    }
    footer a:hover {
        color: white;
    }
    
    /* ✅ DESKTOP STYLES */
    @media (min-width: 769px) {
        header {
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            padding: 20px 40px;
        }
        
        header div {
            font-size: 24px;
            margin-bottom: 0;
        }

        nav {
            display: flex;
            flex-direction: row;
            align-items: center;
            width: auto;
            margin-top: 0;
        }

        nav a {
            margin-left: 20px;
            padding: 0;
        }
    }

    /* ✅ MOBILE STYLES */
    @media (max-width: 768px) {
        .main-section {
            flex-direction: column;
            align-items: stretch;
            padding: 20px;
            gap: 20px;
        }
        .left-column,
        .affiliation-form {
            width: 100%;
        }
        .welcome-message,
        .why-karma,
        .faq-section,
        .affiliation-form {
            margin-bottom: 0;
        }
    }
    </style>
</head>
<body>
    <header>
        <div>Karma Cultural Educational Society</div>
        <nav>
            <a href="{{ url_for('home') }}">Home</a>
            <a href="{{ url_for('about') }}">About Us</a>
            <a href="{{ url_for('contact') }}">Contact Us</a>
            
            {% if session.get("logged_in") %}
                <a href="{{ url_for('admin') }}">Dashboard</a>
                <a href="{{ url_for('logout') }}">Logout</a>
            {% else %}
                <a href="{{ url_for('login') }}">Admin Login</a>
            {% endif %}
        </nav>
    </header>
    <div class="notice-container">
        <div class="notice">📢 Latest Notice: Registrations Open for 2025 | Limited-Time Free Registration | Apply Now! </div>
    </div>
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="flash {{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <main>
        {{ content|safe }}
    </main>

    <footer>
        <p>Follow us on 
            <a href="https://m.facebook.com/p/Karma-Cultural-Educational-Society-61576585804349/" target="_blank">Facebook</a> | 
            <a href="https://www.instagram.com/karmaculturaledusociety/" target="_blank">Instagram</a>
        </p>
        <p>&copy; 2025 Karma Cultural Educational Society. All rights reserved.</p>
        <p>
            <a href="{{ url_for('home') }}">Home</a> | 
            <a href="{{ url_for('about') }}">About Us</a> | 
            <a href="{{ url_for('contact') }}">Contact Us</a>
        </p>
    </footer>

    <script>
        let index = 0, autoSlide;
        function showSlide(step) {
            const slides = document.querySelectorAll('.carousel-images img');
            index += step;
            if (index < 0) index = slides.length - 1;
            if (index >= slides.length) index = 0;
            document.querySelector('.carousel-images').style.transform = 'translateX(' + (-index * 100) + '%)';
        }
        function startAutoSlide() { autoSlide = setInterval(() => { showSlide(1); }, 4000); }
        function stopAutoSlide() { clearInterval(autoSlide); }
        
        showSlide(0); 
        startAutoSlide();

        // FAQ accordion
        document.addEventListener("DOMContentLoaded", () => {
            document.querySelectorAll(".faq-question").forEach(q => {
                q.addEventListener("click", () => {
                    q.parentElement.classList.toggle("active");
                });
            });
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        institution = request.form["institution"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        owner = request.form["owner"]
        
        # Validation
        if not phone.isdigit() or len(phone) != 10:
            flash("❌ Please enter a valid 10-digit phone number.", "error")
            return redirect(url_for("home"))
            
        save_submission(institution, email, phone, address, owner)
        
        flash("✅ Affiliation request submitted successfully!", "success")
        return redirect(url_for("home"))

    photo1 = url_for('static', filename='photo1.jpg')
    photo2 = url_for('static', filename='photo2.png')
    photo3 = url_for('static', filename='photo3.png')

    content = f"""
    <div class="carousel" onmouseover="stopAutoSlide()" onmouseout="startAutoSlide()">
        <div class="carousel-images">
            <img src="{photo1}" alt="Photo 1">
            <img src="{photo2}" alt="Photo 2">
            <img src="{photo3}" alt="Photo 3">
        </div>
        <button class="arrow left" onclick="showSlide(-1)">&#10094;</button>
        <button class="arrow right" onclick="showSlide(1)">&#10095;</button>
    </div>

    <div class="why-karma" style="margin:30px auto; width:90%;">
        <h2>Why Karma?</h2>
        <p>
            At Karma Cultural Educational Society, we believe in holistic development through culture and education. 
            We provide a structured and recognized platform for students and institutions, blending tradition with modern learning. 
            By choosing Karma, you ensure quality guidance, nationwide recognition, and a strong cultural foundation.
        </p>
    </div>

    <div class="main-section">
        <div class="left-column">
            <div class="welcome-message">
                <h2>Welcome to Karma Cultural Educational Society</h2>
                <p>We are dedicated to promoting education, culture, and values through various initiatives 
                    and community activities. Join us in our mission to empower individuals and enrich society 
                    with knowledge and cultural heritage.</p>
            </div>
            <div class="faq-section">
                <h2>Frequently Asked Questions</h2>
                <div class="faq">
                    <div class="faq-question">Which courses or disciplines do you cover?</div>
                    <div class="faq-answer">Karma Cultural Education Society covers Music, Dance, Visual Arts, and Yoga, both classical and contemporary.</div>
                </div>
                <div class="faq">
                    <div class="faq-question">Who can apply for affiliation with KCES?</div>
                    <div class="faq-answer">Any registered institution, academy, cultural center, or school teaching Music, Dance, Art, or Yoga.</div>
                </div>
                <div class="faq">
                    <div class="faq-question">How can an institution apply for affiliation?</div>
                    <div class="faq-answer">Institutions can apply by filling the Affiliation Application Form online or at our office, with required documents and fees.</div>
                </div>
                <div class="faq">
                    <div class="faq-question">What documents are required for affiliation?</div>
                    <div class="faq-answer">• Registration certificate<br>• Address proof<br>• Faculty details<br>• ID of Head/Proprietor<br>• Institution photos</div>
                </div>
                <div class="faq">
                    <div class="faq-question">What are the benefits of being affiliated with KCES?</div>
                    <div class="faq-answer">Recognition, structured curriculum, exams & certification, event guidance, and national networking.</div>
                </div>
            </div>
        </div>
        <div class="affiliation-form">
            <h2>Get Affiliated</h2>
            <form method="POST">
                <label for="institution">Institution Name *</label>
                <input type="text" id="institution" name="institution" required>
                <label for="email">Email * </label>
                <input type="email" id="email" name="email" required>
                <label for="phone">Phone Number * </label>
                <input type="text" id="phone" name="phone" placeholder="Enter 10-digit number" required>
                <label for="address">Address of Institution * </label>
                <textarea id="address" name="address" rows="3" required></textarea>
                <label for="owner">Name of Owner/Proprietor * </label>
                <input type="text" id="owner" name="owner" required>
                <button type="submit">Submit</button>
            </form>
        </div>
    </div>
    """
    return render_template_string(base_template, title="Home", content=content)

@app.route("/about")
def about():
    nikhil_img = url_for('static', filename='nikhil.jpg')
    shruti_img = url_for('static', filename='shrutidhara.jpg')

    content = f"""
    <div class="content" style="padding:40px; background:white; border-radius:10px; box-shadow:0px 4px 10px rgba(0,0,0,0.1);">
        <h1 style="color:#4169e1;">About Us</h1>
        
        <h2 style="margin-top:20px; color:#333;">Who We Are</h2>
        <p>Karma Cultural Education Society (KCES) is a registered organization dedicated to promoting and preserving India’s rich cultural heritage. 
        We nurture talent in Music, Dance, Visual Arts, and Yoga, creating a platform where tradition meets creativity.</p>
        
        <h2 style="margin-top:20px; color:#333;">Our Mission</h2>
        <p>Our mission is to provide structured learning opportunities and standardized certification through affiliated institutions across India. 
        By offering academic guidance, examinations, and recognition, we ensure quality education and authentic practices in cultural studies.</p>
        
        <h2 style="margin-top:20px; color:#333;">Our Philosophy</h2>
        <p>At KCES, we believe that art and culture are deeply connected to life and the environment. 
        Every rhythm, movement, and expression reflects nature’s harmony. 
        Through our programs, we encourage students and institutions to celebrate this connection while fostering discipline, creativity, and holistic growth.</p>
        
        <h2 style="margin-top:20px; color:#333;">Our Commitment</h2>
        <p>With a growing network of affiliated academies, Karma Cultural Education Society is committed to empowering individuals and institutions 
        to carry forward the legacy of Indian art and culture with pride and excellence.</p>

        <!-- ✅ Team Section -->
        <div class="team-section">
            <div class="team-member left">
                <img src="{nikhil_img}" alt="Nikhil Deka">
                <h3 style="color:#4169e1;">Nikhil Deka</h3>
                <p>President</p>
            </div>
            <div class="team-member right">
                <img src="{shruti_img}" alt="Shrutidhara Saikia">
                <h3 style="color:#4169e1;">Shrutidhara Saikia</h3>
                <p>General Secretary</p>
            </div>
        </div>
    </div>

    <style>
        .team-section {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-top: 40px;
            flex-wrap: wrap;
        }}
        .team-member {{
            text-align: center;
            width: 45%;
        }}
        .team-member img {{
            width: 100%;
            max-width: 250px;
            height: auto;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        }}
        .team-member h3 {{
            margin-top: 12px;
        }}
        .team-member p {{
            margin-top: 4px;
            font-size: 16px;
            color: #555;
        }}

        /* ✅ Mobile */
        @media (max-width: 768px) {{
            .team-member {{
                width: 100%;
                margin-bottom: 20px;
            }}
        }}
    </style>
    """
    return render_template_string(base_template, title="About Us", content=content)


@app.route("/contact")
def contact():
    content = """
    <div class="contact-section">
        <h1>Contact Us</h1>
        
        <div class="contact-item">
            <img src="https://img.icons8.com/ios-filled/50/4169e1/new-post.png">
            <p>Email: <a href="mailto:KarmaCulturalEduSociety@gmail.com">KarmaCulturalEduSociety@gmail.com</a></p>
        </div>
        
        <div class="contact-item">
            <img src="https://img.icons8.com/ios-filled/50/4169e1/phone.png">
            <p>Phone: 
                <a href="tel:+918399058514">+91 8399058514</a> | 
                <a href="tel:+919954765926">+91 9954765926</a>
            </p>
        </div>
        
        <div class="contact-item">
            <img src="https://img.icons8.com/ios-filled/50/4169e1/marker.png">
            <p>Address: Salbari, Noonmati, Guwahati, Assam</p>
        </div>
        
        <h2>Follow Us</h2>
        <div class="social-icons">
            <a href="https://m.facebook.com/p/Karma-Cultural-Educational-Society-61576585804349/" target="_blank">
                <img src="https://img.icons8.com/ios-filled/50/4169e1/facebook-new.png">
            </a>
            <a href="https://www.instagram.com/karmaculturaledusociety/" target="_blank">
                <img src="https://img.icons8.com/ios-filled/50/4169e1/instagram-new.png">
            </a>
        </div>
    </div>

    <style>
        .contact-section {
            padding: 50px 20px;
            background: white;
            min-height: 70vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
        .contact-section h1 {
            color: #4169e1;
            margin-bottom: 30px;
        }
        .contact-item {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            max-width: 600px;
            width: 100%;
            justify-content: center;
        }
        .contact-item img {
            width: 28px;
            margin-right: 12px;
        }
        .contact-item p {
            margin: 0;
            font-size: 18px;
        }
        .contact-item a {
            color: #4169e1;
            text-decoration: none;
        }
        .contact-item a:hover {
            text-decoration: underline;
        }
        .social-icons {
            display: flex;
            gap: 25px;
            margin-top: 15px;
        }
        .social-icons img {
            width: 40px;
        }

        /* ✅ Mobile styles */
        @media (max-width: 768px) {
            .contact-item {
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            .contact-item img {
                margin-bottom: 8px;
                margin-right: 0;
            }
            .contact-item p {
                font-size: 16px;
            }
        }
    </style>
    """
    return render_template_string(base_template, title="Contact Us", content=content)


if __name__ == "__main__":
    init_db()  
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
