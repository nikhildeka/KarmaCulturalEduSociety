from flask import Flask, render_template_string, url_for, request, redirect, flash
import threading, smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = "supersecretkey" # needed for flash messages

# ✅ Email Config
EMAIL = os.getenv("MAIL_USERNAME")
PASSWORD = os.getenv("MAIL_PASSWORD")
TO_EMAIL = "karmaculturaledusociety@gmail.com"

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

def send_affiliation_email(institution, email, phone, address, owner):
    """Send affiliation request email"""
    try:
        subject = "New Affiliation Request"
        body = f"""
        📌 New Affiliation Request:

        Institution: {institution}
        Email: {email}
        Phone: {phone}
        Address: {address}
        Owner: {owner}
        """
        
        print(f"📧 Starting email process...")
        print(f"From: {EMAIL}, To: {TO_EMAIL}")
        
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = TO_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
        server.quit()
        print("✅ Email sent successfully in background")
        return True
    except Exception as e:
        print("❌ Error sending email:", e)
        import traceback
        traceback.print_exc()
        return False

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
        
        # Start email thread
        threading.Thread(
            target=send_affiliation_email, 
            args=(institution, email, phone, address, owner)
        ).start()
        
        flash("✅ Affiliation request submitted successfully!", "success")
        return redirect(url_for("home"))

    # ✅ Carousel
    photo1 = url_for('static', filename='photo1.jpg')
    photo2 = url_for('static', filename='photo2.png')
    photo3 = url_for('static', filename='photo3.png')

    # ✅ Home Page Content
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
    content = """
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
    </div>
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
            <p>Address: Salbari, Guwahati, Assam</p>
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)