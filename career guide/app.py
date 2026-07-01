from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'career_pathway_2026_secure_mongo'

# ==========================================
# MONGODB SETUP
# ==========================================
# Local MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['career_pathway_db']

# Collections
users_collection = db['users']
assessments_collection = db['assessments']
feedback_collection = db['feedbacks']

# Ensure unique usernames
users_collection.create_index("username", unique=True)

# ==========================================
# PAGE ROUTES
# ==========================================
@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/auth')
def auth(): 
    return render_template('auth.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session: 
        return redirect(url_for('auth'))
    return render_template('dashboard.html', username=session['username'])

# ==========================================
# AUTHENTICATION ROUTES
# ==========================================
@app.route('/register', methods=['POST'])
def register():
    # HTML Form se data request.form mein aata hai
    username = request.form.get('username')
    password = generate_password_hash(request.form.get('password'))
    
    try:
        users_collection.insert_one({
            "username": username,
            "password": password,
            "joined_at": datetime.now()
        })
        return redirect(url_for('auth'))
    except DuplicateKeyError:
        return "Bhai, yeh username pehle se hai! Kuch naya try karo.", 400

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = users_collection.find_one({"username": username})
    
    if user and check_password_hash(user['password'], password):
        session['username'] = user['username']
        return redirect(url_for('dashboard'))
    
    return "Invalid Credentials. Login fail ho gaya!", 401

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



@app.route('/api/assessment', methods=['POST'])
def assessment():
    try:
        data = request.get_json()
        scores = data.get('scores', {})
        t = scores.get('technical', 0)
        c = scores.get('creative', 0)
        a = scores.get('analytical', 0)

        # 1. Sare Roles ke Specific Video Links yahan dalo
        links = {
            "Backend Architect": "https://youtu.be/0IciwnJ6PJI",  
            "UI/UX Designer": "https://youtu.be/h87xnT004Aw",     
            "Data Scientist": "https://www.youtube.com/watch?v=ua-CiDNNj30",
            "Cybersecurity Expert": "https://youtu.be/LIOeHVzeLUA", 
            "Product Manager": "https://youtu.be/0p5YPBl_uBI",      
            "Full Stack Engineer": "https://youtu.be/LzMnsfqjzkA"   
        }

        # 2. Score ke basis par Role decide karo
        # Logic: Jo score sabse zyada hoga, wahi role milega
        if t > 15 and a > 10:
            role = "Cybersecurity Expert"
            reason = "Your technical and analytical mindset is perfect for security."
        elif t >= max(c, a): 
            role = "Backend Architect"
            reason = "Your logic and systems architecture mindset is amazing."
        elif c >= max(t, a): 
            role = "UI/UX Designer"
            reason = "You balance aesthetics and user psychology perfectly."
        elif a > 15 and c > 5:
            role = "Product Manager"
            reason = "You manage both analysis and creativity with ease."
        elif a >= max(t, c): 
            role = "Data Scientist"
            reason = "You have no match when it comes to patterns and data analysis."
        else: 
            role = "Full Stack Engineer"
            reason = "You are versatile; you can handle both frontend and backend with ease."


        yt = links.get(role, "https://www.youtube.com")
        
        # MongoDB Save Logic (Same rahega)
        # ...
        if 'username' in session:
            try:
                assessments_collection.insert_one({
                    "username": session['username'],
                    "role": role,
                    "reason": reason,
                    "yt_link": yt,
                    "date": datetime.now()
                })
            except Exception as db_err:
                print(f"Database Error: {db_err}")



        return jsonify({"role": role, "reason": reason, "yt_link": yt})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/roadmap', methods=['POST'])
def generate_roadmap():
    try:
        data = request.get_json()
        # Topic ko clean aur lowercase karein taaki dictionary se match ho sake
        topic = data.get('topic', '').strip().lower()
        
        # 1. Topic-wise Specific Video Library (Updated & Working Links)
        topic_videos = {
            "python": "https://www.youtube.com/watch?v=rfscVS0vtbw",
            "javascript": "https://www.youtube.com/watch?v=VlPiVmYuoqw",
            "react": "https://www.youtube.com/watch?v=RGKi6LSPDLU",
            "node": "https://www.youtube.com/watch?v=tlH_0H0-xU8",  
            "html": "https://www.youtube.com/watch?v=kUMe1FH4CHE",
            "css": "https://www.youtube.com/watch?v=OXGznpKZ_sA",
            "sql": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
            "cloud": "https://www.youtube.com/watch?v=M9muev-P6-Q", 
            "c": "https://www.youtube.com/watch?v=irqbmMNs2Bo",      
            "c++": "https://www.youtube.com/watch?v=8jLOx1hD3_o",
            "typescript" :"https://youtu.be/30LWjhZzg50",
            "swift": "https://youtu.be/8Xg7E9shq0U",
            "kotlin" : "https://youtu.be/EExSSotojVI",
            "java"  : "https://youtu.be/A74TOX803D0",
            "rust" : "https://youtu.be/qP7LzZqGh30",
            "dsa" : "https://youtu.be/xwI5OBEnsZU",
            "powerpoint" : "https://youtu.be/OekrBhNybP0",
            "excel" : "https://youtu.be/FtQk_tPnD4I",
            "powerbi" : "https://youtu.be/KdC5R7oPCAI",
            "android development" : "https://youtu.be/u64gyCdqawU",
            "ai" : "https://youtu.be/mEsleV16qdo",
            "ms word" :"https://youtu.be/YHSLkNzLuqc",
            "adobe" : "https://youtu.be/90Zaa8dH4SU",
            "editing" :"https://youtu.be/e_dv7GBHka8",
            "canva" : "https://youtu.be/rXLvN1FEkOE",
            "ethical hacking" : "https://youtu.be/2eLJNBroFrg",
            "Data engineer" : "https://youtu.be/PHsC_t0j1dU",
            "AI Prompt Engineer" : "https://youtu.be/_ZvnD73m40o",
            "cyber security" : "https://youtu.be/v3iUx2SNspY",
            "Cloud Architect" : "https://youtu.be/ZfZ_ManKnlM",
            "SaaS": "https://youtu.be/XUkNR-JfHwo"
        }

        # Check karein ki topic dictionary mein hai ya nahi
        if topic in topic_videos:
            yt_link = topic_videos[topic]
        else:
            # Agar dictionary mein nahi hai, toh search query banayein
            yt_link = f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+roadmap"

        # 2. Roadmap Content Logic
        # Yahan humne 'topic' variable use kiya hai (t_lower ki jagah)
        # 2. Highly Detailed Roadmap Content Logic
        # --- NEW DEDICATED PLAN FOR C LANGUAGE ---
        if topic == 'c':
            res = {
                "d1": "Days 1-15: Master C syntax, Data Types, and Operators. Understand the compilation process and set up GCC. Focus on control flow (If-Else, Switch) and complex Loops.",
                "d2": "Days 16-30: Deep dive into Functions and Scope. Master Arrays (1D & 2D) and String manipulation using standard libraries. Build a basic Calculator or Unit Converter.",
                "d3": "Days 31-45: The 'Pointers' Phase. Understand Memory Addresses, Pointer Arithmetic, and Dynamic Memory Allocation (malloc, calloc, free). This is the core of C mastery.",
                "d4": "Days 46-60: Structure & File I/O. Learn to group data using Structures and Unions. Master reading/writing to files (.txt, .bin) to build persistent CLI applications.",
                "d5": "Days 61-75: Data Structures in C. Implement Linked Lists, Stacks, or Queues from scratch. Final Project: A 'Library Management System' or 'Bank Account Simulator' using CLI."
            }
        # --- NEW DEDICATED PLAN FOR DSA ---
        elif topic == 'dsa':
            res = {
                "d1": "Days 1-15: Time/Space Complexity (Big O) and fundamental structures. Master Arrays, Strings, and core algorithms like Two Pointers and Sliding Window.",
                "d2": "Days 16-30: Linear Data Structures and Hashing. Deep dive into Linked Lists, Stacks, Queues, and Hash Maps. Focus on detecting cycles and evaluating expressions.",
                "d3": "Days 31-45: Non-Linear Structures. Master Trees (Binary, BST, AVL), Tries, and Heaps (Priority Queues). Focus on traversals (Inorder, Preorder, Postorder) and depth/breadth tracking.",
                "d4": "Days 46-60: Graph Theory and Advanced Logic. Learn Recursion, Backtracking (N-Queens, Sudoku), and core Graph algorithms (BFS, DFS, Topological Sort).",
                "d5": "Days 61-75: Dynamic Programming & Shortest Paths. Master 1D/2D DP (Knapsack, LCS) and algorithms like Dijkstra's. Final Capstone: Complete a 50-problem LeetCode/HackerRank gauntlet."
            }

        # --- NEW DEDICATED PLAN FOR CYBERSECURITY / HACKING ---
        elif any(x in topic for x in ['cyber', 'security', 'ethical hacking']):
            res = {
                "d1": "Days 1-15: Network Fundamentals & OS. Master TCP/IP, OSI Models, Subnetting, and Linux CLI operations. Understand how data packets travel and basic firewall rules.",
                "d2": "Days 16-30: Reconnaissance & OSINT. Learn active/passive information gathering using Nmap, Wireshark, and Shodan. Master vulnerability scanning and footprinting.",
                "d3": "Days 31-45: Web Application Penetration Testing. Deep dive into the OWASP Top 10. Exploit SQL Injections, XSS, and CSRF vulnerabilities using Burp Suite and Metasploit.",
                "d4": "Days 46-60: Privilege Escalation & Cryptography. Learn to bypass antivirus, crack passwords (Hashcat/John the Ripper), and exploit Windows/Linux misconfigurations to gain root access.",
                "d5": "Days 61-75: Defensive Security & Reporting. Focus on Blue Teaming, incident response, creating professional penetration test reports. Final Capstone: Hack a complete CTF (Capture The Flag) machine."
            }

        # --- NEW DEDICATED PLAN FOR CLOUD COMPUTING ---
        elif any(x in topic for x in ['cloud', 'cloud architect']):
            res = {
                "d1": "Days 1-15: Cloud Fundamentals & IAM. Understand IaaS, PaaS, SaaS. Master Identity and Access Management (IAM), billing, and basic cloud security principles on AWS/Azure/GCP.",
                "d2": "Days 16-30: Compute & Networking. Learn to deploy Virtual Machines (EC2), manage Load Balancers, Auto-Scaling groups, and design secure Virtual Private Clouds (VPCs) with subnets.",
                "d3": "Days 31-45: Storage & Database Solutions. Implement Object Storage (S3), block storage, and manage managed databases (RDS, DynamoDB). Understand CDN integration for speed.",
                "d4": "Days 46-60: Serverless & Containers. Architect event-driven applications using Serverless functions (Lambda). Learn container orchestration basics using ECS or Kubernetes (EKS).",
                "d5": "Days 61-75: Infrastructure as Code (IaC) & Optimization. Automate deployments using Terraform or CloudFormation. Final Capstone: Architect and deploy a highly-available, fault-tolerant web application."
            }

        # --- NEW DEDICATED PLAN FOR DATA ENGINEERING ---
        elif topic == 'data engineer':
            res = {
                "d1": "Days 1-15: Advanced SQL & Data Warehousing. Master complex queries and understand OLTP vs. OLAP. Learn warehouse architectures using Snowflake, BigQuery, or Redshift.",
                "d2": "Days 16-30: Python for Data Engineering. Use Python to write extraction scripts, handle diverse file formats (JSON, Parquet, Avro), and interact with cloud APIs.",
                "d3": "Days 31-45: Big Data Processing. Learn distributed computing concepts using Apache Spark or Hadoop. Process massive datasets efficiently using PySpark.",
                "d4": "Days 46-60: Data Pipelines & Orchestration. Build and schedule ETL/ELT pipelines using Apache Airflow or Prefect. Ensure data quality and handle pipeline failures.",
                "d5": "Days 61-75: Streaming & Cloud Architecture. Implement real-time data streaming using Apache Kafka. Final Capstone: Build an end-to-end automated data pipeline deployed on the cloud."
            }

        # --- NEW DEDICATED PLAN FOR PROMPT ENGINEERING ---
        elif topic == 'ai prompt engineer':
            res = {
                "d1": "Days 1-15: LLM Mechanics & Zero-Shot Prompting. Understand tokenization, context windows, and model behavior. Master basic task framing, zero-shot, and few-shot prompting techniques.",
                "d2": "Days 16-30: Advanced Prompt Structures. Learn Chain-of-Thought (CoT), ReAct, and Tree of Thoughts prompting to force AI into logical reasoning and math-based problem-solving.",
                "d3": "Days 31-45: System Prompts & Guardrails. Design robust system instructions to enforce persona, tone, and formatting. Learn techniques to prevent AI hallucinations and jailbreaks.",
                "d4": "Days 46-60: API Integration & Automation. Use Python to connect to OpenAI/Anthropic APIs. Automate prompt testing, handle API rate limits, and tweak temperature/top_p parameters.",
                "d5": "Days 61-75: RAG & Fine-Tuning Basics. Understand Retrieval-Augmented Generation (RAG) to feed AI external data. Final Capstone: Build a highly-specialized, automated customer support AI agent."
            }

        # --- NEW DEDICATED PLAN FOR DESIGN / EDITING ---
        elif any(x in topic for x in ['adobe', 'editing', 'canva']):
            res = {
                "d1": "Days 1-15: Design/Video Fundamentals. Master the core principles: Color Theory, Typography, Composition, Rule of Thirds, and understanding pacing/cuts in video.",
                "d2": "Days 16-30: Workspace & Tools Mastery. Deep dive into your primary software (Premiere, Photoshop, or Canva). Master layers, masking, timelines, and essential shortcuts.",
                "d3": "Days 31-45: Advanced Techniques. Learn color grading (Lumetri), keyframing animations, audio mixing (for video), and advanced vector/photo manipulation (for design).",
                "d4": "Days 46-60: Workflow & Asset Management. Optimize your render settings, use motion graphics templates (MOGRTs), create reusable brand kits, and manage large project files efficiently.",
                "d5": "Days 61-75: Professional Output & Portfolio. Learn client communication, version control, and export formats. Final Capstone: Produce a cinematic short film or a complete corporate brand identity package."
            }

        # --- NEW DEDICATED PLAN FOR SAAS / PRODUCT ---
        elif topic == 'saas':
            res = {
                "d1": "Days 1-15: SaaS Business Models & Metrics. Understand MRR, ARR, CAC (Customer Acquisition Cost), Churn, and LTV. Identify market gaps and validate a B2B/B2C software idea.",
                "d2": "Days 16-30: MVP & UI/UX Wireframing. Define the Minimum Viable Product. Map out user journeys and build high-fidelity wireframes using Figma to visualize the core solution.",
                "d3": "Days 31-45: Pricing Strategies & Go-To-Market. Design tiered pricing models (Freemium, Pro, Enterprise). Plan the launch strategy (Product Hunt, Cold Emailing, SEO).",
                "d4": "Days 46-60: Analytics & User Onboarding. Design frictionless onboarding funnels. Integrate product analytics (Mixpanel, Google Analytics) to track feature usage and drop-offs.",
                "d5": "Days 61-75: Scaling & Customer Success. Build feedback loops, establish customer support protocols, and plan technical scaling. Final Capstone: A comprehensive 50-page SaaS Pitch Deck and Launch Plan."
            }

        # --- NEW DEDICATED PLAN FOR OFFICE/PRODUCTIVITY ---
        elif any(x in topic for x in ['powerpoint', 'ms word', 'word']):
            res = {
                "d1": "Days 1-15: Interface & Document Structuring. Master templates, styles, ribbon customization, and proper layout formatting (margins, headers/footers, master slides).",
                "d2": "Days 16-30: Visual Communication. Learn to embed high-quality graphics, utilize SmartArt effectively, design custom tables, and create complex multi-level lists without breaking formatting.",
                "d3": "Days 31-45: Advanced Data Integration. Master Mail Merge for mass communication. Link live Excel data/charts into your documents and presentations for automated updates.",
                "d4": "Days 46-60: Professional Polish & Animations. (For PPT): Master seamless slide transitions, trigger animations, and timings. (For Word): Master table of contents, citations, and indexing.",
                "d5": "Days 61-75: Protection, Macros & Delivery. Learn basic Macros to automate repetitive tasks, protect documents with passwords/permissions, and practice presentation delivery. Final Capstone: A Corporate Annual Report/Pitch."
            }
        # --- NEW DEDICATED PLAN FOR SQL (DATABASE) ---
        elif topic == 'sql':
            res = {
                "d1": "Days 1-15: Introduction to Relational Databases (RDBMS). Master Basic CRUD operations (CREATE, READ, UPDATE, DELETE) and filtering data using WHERE, LIKE, and BETWEEN.",
                "d2": "Days 16-30: Mastering JOINS and Set Operations. Learn to connect multiple tables using Inner, Left, Right, and Full Joins. Understand Primary Keys vs Foreign Keys.",
                "d3": "Days 31-45: Data Aggregation & Grouping. Master functions like COUNT, SUM, AVG, and the HAVING clause. Understand Database Normalization (1NF, 2NF, 3NF) for clean design.",
                "d4": "Days 46-60: Advanced SQL Techniques. Learn Subqueries, Common Table Expressions (CTEs), and Window Functions (RANK, ROW_NUMBER). Focus on writing high-performance queries.",
                "d5": "Days 61-75: Database Administration & Optimization. Learn about Indexing, Views, Stored Procedures, and Transactions (ACID properties). Final Project: Designing a 'E-commerce Database Schema'."
            }
        elif any(x in topic for x in ['python',  'c++', 'java', 'backend', 'node', 'rust']):
            res = {
                "d1": "Days 1-15: Master core language fundamentals (Variables, OOPs, Data Structures) and set up a robust development environment. Learn Git/GitHub for version control and team collaboration.",
                "d2": "Days 16-30: Dive into backend frameworks (Express.js, Django, Spring Boot) and understand MVC architecture. Build RESTful APIs, handle dynamic routing, and use Postman for endpoint testing.",
                "d3": "Days 31-45: Master database management by integrating Relational (MySQL/PostgreSQL) and NoSQL (MongoDB) databases. Learn ORM/ODM, complex queries, and implement caching mechanisms like Redis.",
                "d4": "Days 46-60: Secure your applications by implementing Authentication & Authorization (JWT, OAuth2). Apply strict security best practices (CORS, hashing, rate limiting) and write custom middleware.",
                "d5": "Days 61-75: Focus on DevOps and deployment. Learn Docker for containerization, set up CI/CD pipelines for automated testing, and deploy your scalable backend to cloud platforms like AWS or Azure."
            }
        elif any(x in topic for x in ['html', 'css', 'react', 'frontend', 'typescript', 'javascript']):
            res = {
                "d1": "Days 1-15: Build a strong UI foundation. Master Semantic HTML5 for web accessibility, advanced CSS3 techniques (Flexbox, CSS Grid, Animations), and rapid responsive design using Tailwind CSS or Bootstrap.",
                "d2": "Days 16-30: Achieve deep JavaScript mastery. Understand ES6+ syntax, complex DOM manipulation, Event Loops, Closures, Async/Await, and interacting with external third-party APIs using Fetch API.",
                "d3": "Days 31-45: Transition into modern UI frameworks (React, Vue). Understand component-based architecture, prop drilling, component lifecycles, functional programming, and creating custom Hooks.",
                "d4": "Days 46-60: Tackle complex application states using State Management tools (Redux Toolkit, Context API). Implement advanced client-side routing, secure form handling, and real-time data validation.",
                "d5": "Days 61-75: Polish for production. Focus on web performance optimization (lazy loading, code splitting), write comprehensive unit tests (Jest), and deploy your high-performance portfolio on Vercel or Netlify."
            }
        elif any(x in topic for x in ['powerbi', 'excel',  'ai', 'data']):
            res = {
                "d1": "Days 1-15: Establish strong foundational knowledge in Statistics and Probability. Master data manipulation in Excel (Pivot Tables, VLOOKUP, Power Query) to understand raw data cleaning and organization.",
                "d2": "Days 16-30: Gain expertise in Relational Databases and SQL. Write complex nested queries, master SQL Joins, window functions, and data aggregations to extract meaningful insights from large datasets.",
                "d3": "Days 31-45: Focus on Data Storytelling and Visualization. Build interactive, dynamic dashboards using PowerBI or Tableau. Learn to communicate analytical findings clearly to business stakeholders.",
                "d4": "Days 46-60: Program for Data Science using Python. Master essential libraries like Pandas for heavy data wrangling, NumPy for numerical computing, and Matplotlib/Seaborn for programmatic data visualization.",
                "d5": "Days 61-75: Step into Artificial Intelligence. Learn Machine Learning basics (Regression, Classification), perform deep Exploratory Data Analysis (EDA), and train predictive models for a real-world capstone."
            }
        elif any(x in topic for x in ['android', 'swift', 'kotlin', 'app', 'flutter']):
            res = {
                "d1": "Days 1-15: Understand Mobile App Architecture and UI/UX paradigms. Master fundamental layouts, navigation components, and responsive design systems specific to mobile screens (Material Design/HIG).",
                "d2": "Days 16-30: Deep dive into your primary mobile language (Kotlin, Swift, or Dart). Understand memory management, asynchronous programming techniques, and native SDK ecosystem integrations.",
                "d3": "Days 31-45: Connect the app to hardware and local storage. Learn to handle device sensors, GPS, Camera APIs, and implement robust offline data persistence using local databases like SQLite or Room.",
                "d4": "Days 46-60: Make your app dynamic by integrating RESTful APIs. Handle JSON parsing, background threading, Push Notifications, and efficient state management within the mobile ecosystem.",
                "d5": "Days 61-75: Prepare for global launch. Focus on App Store Optimization (ASO), write UI tests, integrate crash analytics (Firebase), and navigate the developer consoles to publish on the Play Store or App Store."
            }
        else:
            res = {
                "d1": f"Days 1-15: Core Setup & Fundamentals. Establish a solid grounding in the core syntax, concepts, and primary tools associated with {topic.title()}. Set up your professional development environment.",
                "d2": "Days 16-30: Intermediate concepts and practical application. Move beyond the basics by building small, modular mini-projects and understanding the standard conventions and best practices of the ecosystem.",
                "d3": "Days 31-45: Advanced Tooling & Architecture. Dive into advanced features, explore the broader framework ecosystem, and learn how to structure larger, more complex projects efficiently.",
                "d4": "Days 46-60: Real-world Integrations & Problem Solving. Focus on debugging techniques, integrating third-party libraries/APIs, and simulating real-world industry scenarios and architectural challenges.",
                "d5": "Days 61-75: Final Capstone & Deployment. Bring everything together by developing a comprehensive, production-ready capstone project, writing technical documentation, and deploying it live for your portfolio."
            }
            
        # Link ko final response mein add karein
        res["yt_link"] = yt_link
        return jsonify(res)

    except Exception as e:
        print(f"Roadmap Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'username' not in session:
        return jsonify({"error": "login_required"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    msg = data.get('feedback_text')
    stars = data.get('rating', 5) # Default 5 agar rating na aaye
    
    if msg:
        try:
            feedback_collection.insert_one({
                "username": session['username'],
                "message": msg,
                "rating": int(stars), # Make sure rating is a number
                "date": datetime.now().strftime("%d %b %Y, %I:%M %p")
            })
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Message is empty"}), 400

# ==========================================
# ADMIN DASHBOARD
# ==========================================
@app.route('/admin')
def admin_dashboard():
    if 'username' not in session or session['username'] != 'admin':
        return "Access Denied! Admin access required.", 403

    try:
        users = list(users_collection.find({}, {"_id": 0}))
        assessments = list(assessments_collection.find({}, {"_id": 0}))
        all_feedbacks = list(feedback_collection.find({}, {"_id": 0}).sort("_id", -1))

        return render_template('admin.html', 
                               users=users, 
                               assessments=assessments, 
                               feedbacks=all_feedbacks, 
                               total_users=len(users), 
                               total_tests=len(assessments))
    except Exception as e:
        return f"Database Error: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)