# CareerLens AI - High-Volume Real India Seed Data Generator
import random

COMPANIES = [
    ('TCS', 'https://www.tcs.com/careers/india', 'TCS Careers'),
    ('Infosys', 'https://www.infosys.com/careers.html', 'Infosys Careers'),
    ('Wipro', 'https://careers.wipro.com/', 'Wipro Careers'),
    ('HCLTech', 'https://www.hcltech.com/careers', 'HCLTech Careers'),
    ('Tech Mahindra', 'https://careers.techmahindra.com/', 'Tech Mahindra Careers'),
    ('Cognizant', 'https://careers.cognizant.com/in/en', 'Cognizant Careers'),
    ('Capgemini', 'https://www.capgemini.com/in-en/careers/', 'Capgemini Careers'),
    ('Accenture India', 'https://www.accenture.com/in-en/careers', 'Accenture Careers'),
    ('Google India', 'https://www.google.com/about/careers/applications/jobs/results/?location=India', 'Google Careers'),
    ('Microsoft India', 'https://careers.microsoft.com/v2/global/en/locations/india.html', 'Microsoft Careers'),
    ('Amazon India', 'https://www.amazon.jobs/en/locations/india', 'Amazon Careers'),
    ('Flipkart', 'https://www.flipkartcareers.com/', 'Flipkart Careers'),
    ('Swiggy', 'https://careers.swiggy.com/', 'Swiggy Careers'),
    ('Zomato', 'https://www.zomato.com/careers', 'Zomato Careers'),
    ('Razorpay', 'https://razorpay.com/jobs/', 'Razorpay Careers'),
    ('PhonePe', 'https://www.phonepe.com/careers/', 'PhonePe Careers'),
    ('CRED', 'https://cred.club/careers', 'CRED Careers'),
    ('Zerodha', 'https://zerodha.tech/careers', 'Zerodha Careers'),
    ('Paytm', 'https://paytm.com/careers', 'Paytm Careers'),
    ('LTIMindtree', 'https://www.ltimindtree.com/careers/', 'LTIMindtree Careers'),
    ('Deloitte India', 'https://www2.deloitte.com/in/en/careers/life-at-deloitte.html', 'Deloitte Careers'),
    ('PwC India', 'https://www.pwc.in/careers.html', 'PwC Careers'),
    ('EY India', 'https://www.ey.com/en_in/careers', 'EY Careers'),
    ('KPMG India', 'https://kpmg.com/in/en/home/careers.html', 'KPMG Careers'),
    ('Jio Platforms', 'https://careers.jio.com/', 'Jio Careers'),
    ('Airtel', 'https://www.airtel.in/careers/', 'Airtel Careers'),
    ('Ola Cabs', 'https://www.olacabs.com/careers', 'Ola Careers'),
    ('Meesho', 'https://meesho.io/careers', 'Meesho Careers'),
    ('InMobi', 'https://www.inmobi.com/company/careers/', 'InMobi Careers'),
    ('Zoho Corporation', 'https://www.zoho.com/careers/', 'Zoho Careers'),
    ('Freshworks', 'https://www.freshworks.com/company/careers/', 'Freshworks Careers'),
    ('Postman', 'https://www.postman.com/careers/', 'Postman Careers'),
    ('BrowserStack', 'https://www.browserstack.com/careers', 'BrowserStack Careers'),
    ('Pine Labs', 'https://www.pinelabs.com/careers', 'Pine Labs Careers'),
    ('MakeMyTrip', 'https://careers.makemytrip.com/', 'MakeMyTrip Careers')
]

LOCATIONS = [
    'Bangalore, Karnataka',
    'Hyderabad, Telangana',
    'Pune, Maharashtra',
    'Mumbai, Maharashtra',
    'Chennai, Tamil Nadu',
    'Gurgaon, Haryana (Delhi NCR)',
    'Noida, Uttar Pradesh (Delhi NCR)',
    'Remote (India)',
    'Kolkata, West Bengal',
    'Ahmedabad, Gujarat',
    'Kochi, Kerala',
    'Coimbatore, Tamil Nadu'
]

ENTRY_ROLES = [
    ('Graduate Trainee Engineer (GTE)', 'Internship', 'INR 3.5L - 5.0L PA', 'Python, Java, C++, SQL, Data Structures, Algorithms', 'Participate in engineering bootcamps, assist in module development, write unit tests, and resolve software bugs.'),
    ('Associate Software Engineer', 'Full-time', 'INR 4.5L - 7.0L PA', 'Java, Spring Boot, MySQL, REST APIs, Git', 'Entry-level full-time role for fresh engineering graduates. Work on scalable web services and backend APIs.'),
    ('Frontend Developer Intern', 'Internship', 'INR 25k - 45k/month', 'HTML, CSS, JavaScript, React, TailwindCSS', '6-month internship focused on building responsive web UIs, component libraries, and frontend state management.'),
    ('Data Analyst Trainee', 'Full-time', 'INR 4.0L - 6.5L PA', 'SQL, Python, Excel, Power BI, Tableau', 'Analyze business metrics, build executive dashboards, write optimized SQL queries, and generate data reports.'),
    ('SDE Intern - Summer 2026', 'Internship', 'INR 35k - 75k/month', 'C++, Java, Python, Problem Solving, Computer Science Fundamentals', 'Summer internship for pre-final and final year B.Tech/M.Tech students. Work with senior mentors on production code.'),
    ('Junior QA / Automation Engineer', 'Full-time', 'INR 3.8L - 5.5L PA', 'Selenium, Python, Java, Manual Testing, Postman', 'Execute test plans, write automated test scripts, perform API testing, and report software defects.'),
    ('DevOps Trainee', 'Full-time', 'INR 4.5L - 6.8L PA', 'Linux, Bash, Docker, Git, CI/CD, AWS Basics', 'Learn and assist in continuous integration, containerization, cloud infrastructure monitoring, and shell scripting.'),
    ('AI / ML Research Intern', 'Internship', 'INR 30k - 60k/month', 'Python, PyTorch, TensorFlow, Scikit-learn, Pandas', 'Work alongside AI scientists on NLP models, LLM fine-tuning, computer vision, and data preprocessing pipelines.'),
    ('System Engineer - Freshers 2025/2026', 'Full-time', 'INR 3.6L - 5.2L PA', 'Java, C#, SQL, Networking, Linux', 'Role for CS/IT/EC graduates. Core software engineering, application maintenance, and client project delivery.'),
    ('Cloud Operations Associate', 'Full-time', 'INR 4.2L - 6.0L PA', 'AWS, Azure, Linux, Python, Networking, Monitoring', 'Monitor cloud infrastructure health, manage user permissions, automate deployment scripts, and assist in cloud migration.')
]

MID_ROLES = [
    ('Software Development Engineer I (SDE-1)', 'Full-time', 'INR 8.0L - 14.0L PA', 'Java, Spring Boot, Microservices, PostgreSQL, Kafka', '1-3 years experience. Design and implement high-throughput REST APIs, write clean code, and participate in code reviews.'),
    ('Full Stack Engineer (React + Node)', 'Full-time', 'INR 9.0L - 16.0L PA', 'React, Node.js, TypeScript, MongoDB, Express, AWS', '2-4 years experience. Own end-to-end feature delivery from React frontend to Node.js microservices and database schemas.'),
    ('Data Engineer (PySpark & Airflow)', 'Full-time', 'INR 10.0L - 18.0L PA', 'Python, PySpark, SQL, Apache Airflow, Snowflake, AWS S3', '2-5 years experience. Build and maintain scalable ETL/ELT data pipelines, data lake architecture, and data warehousing.'),
    ('DevOps Engineer (Kubernetes & Terraform)', 'Full-time', 'INR 11.0L - 19.0L PA', 'Docker, Kubernetes, Terraform, AWS, Jenkins, Prometheus', '2-4 years experience. Automate infrastructure provisioning, manage K8s clusters, and optimize CI/CD pipelines.'),
    ('Backend Engineer (Go / Python)', 'Full-time', 'INR 12.0L - 20.0L PA', 'Go, Python, Redis, PostgreSQL, gRPC, Distributed Systems', '2-5 years experience. Build high-concurrency backend services, optimize database queries, and implement caching strategies.'),
    ('Mobile Developer (React Native / Flutter)', 'Full-time', 'INR 8.5L - 15.0L PA', 'React Native, Flutter, Dart, JavaScript, iOS, Android', '1-4 years experience. Build cross-platform iOS and Android applications with smooth UI animations and offline sync.')
]

SENIOR_ROLES = [
    ('Senior Software Engineer (SDE-2)', 'Full-time', 'INR 18.0L - 32.0L PA', 'Java, Microservices, System Design, Kafka, Distributed Caching', '4-7 years experience. Architect scalable distributed systems, mentor junior engineers, and drive technical roadmap.'),
    ('Lead ML Engineer (LLMs & MLOps)', 'Full-time', 'INR 22.0L - 40.0L PA', 'Python, PyTorch, LangChain, MLflow, Docker, CUDA, Ray', '4-8 years experience. Lead the deployment of Generative AI and LLM applications into production environments.')
]

def generate_opportunities(total_count=350):
    random.seed(42)
    jobs = []
    for i in range(total_count):
        company_name, company_url, source_name = COMPANIES[i % len(COMPANIES)]
        loc = LOCATIONS[i % len(LOCATIONS)]
        
        r = random.random()
        if r < 0.55:
            title, jtype, salary, skills, desc = ENTRY_ROLES[i % len(ENTRY_ROLES)]
        elif r < 0.90:
            title, jtype, salary, skills, desc = MID_ROLES[i % len(MID_ROLES)]
        else:
            title, jtype, salary, skills, desc = SENIOR_ROLES[i % len(SENIOR_ROLES)]
            
        full_title = f"{title} - {company_name}" if ("Freshers" in title or "Trainee" in title) else title
        req_id = 100000 + i
        apply_link = f"{company_url}?req_id={req_id}"
        
        jobs.append({
            "title": full_title,
            "company": company_name,
            "location": loc,
            "job_type": jtype,
            "description": f"{desc} Join {company_name} in {loc}. We offer competitive compensation, health benefits, structured career progression, and flexible work arrangements.",
            "primary_source": source_name,
            "salary_range": salary,
            "apply_url": apply_link,
            "required_skills": skills
        })
    return jobs

OPPORTUNITIES = generate_opportunities(350)
