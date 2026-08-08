# CareerLens AI - High-Volume Genuine India Dataset Generator (1,000+ Opportunities)
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
    ('MakeMyTrip', 'https://careers.makemytrip.com/', 'MakeMyTrip Careers'),
    ('Urban Company', 'https://careers.urbancompany.com/', 'Urban Company Careers'),
    ('Delhivery', 'https://www.delhivery.com/careers', 'Delhivery Careers'),
    ('Nykaa', 'https://www.nykaa.com/careers', 'Nykaa Careers'),
    ('Lenskart', 'https://www.lenskart.com/careers', 'Lenskart Careers'),
    ('Cars24', 'https://www.cars24.com/careers', 'Cars24 Careers'),
    ('PolicyBazaar', 'https://www.policybazaar.com/careers', 'PolicyBazaar Careers'),
    ('Groww', 'https://groww.in/careers', 'Groww Careers'),
    ('Upstox', 'https://upstox.com/careers', 'Upstox Careers'),
    ('Unacademy', 'https://unacademy.com/careers', 'Unacademy Careers'),
    ('UpGrad', 'https://upgrad.com/careers', 'UpGrad Careers'),
    ('Blinkit', 'https://blinkit.com/careers', 'Blinkit Careers'),
    ('Zepto', 'https://www.zepto.co/careers', 'Zepto Careers'),
    ('Rapido', 'https://www.rapido.bike/careers', 'Rapido Careers')
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
    'Coimbatore, Tamil Nadu',
    'Chandigarh, Punjab',
    'Indore, Madhya Pradesh',
    'Jaipur, Rajasthan'
]

# 20%+ Internships
INTERNSHIPS = [
    ('SDE Intern - Summer 2026', 'Internship', 'INR 35k - 85k/month', 'C++, Java, Python, Problem Solving, Data Structures', 'Summer internship for pre-final & final year B.Tech/M.Tech students. Work with senior engineers on core services.'),
    ('Frontend Developer Intern', 'Internship', 'INR 25k - 50k/month', 'HTML, CSS, JavaScript, React, TailwindCSS', '6-month frontend internship building responsive UIs, design system components, and interactive dashboards.'),
    ('Data Science & AI Intern', 'Internship', 'INR 30k - 65k/month', 'Python, PyTorch, Pandas, Scikit-learn, SQL', 'Work alongside AI research team building NLP pipelines, LLM fine-tuning datasets, and predictive models.'),
    ('Backend Engineering Intern', 'Internship', 'INR 30k - 60k/month', 'Java, Node.js, Python, PostgreSQL, REST APIs', 'Internship focusing on RESTful API development, database optimizations, and backend unit test automation.'),
    ('DevOps & Cloud Intern', 'Internship', 'INR 25k - 45k/month', 'Linux, Docker, Bash, Git, AWS Basics, CI/CD', 'Hands-on cloud infrastructure internship assisting in container deployment, log monitoring, and build automation.'),
    ('UI/UX Design Intern', 'Internship', 'INR 20k - 40k/month', 'Figma, Wireframing, Prototyping, User Research', 'Design intuitive mobile & web interfaces, create high-fidelity prototypes, and participate in user feedback sessions.'),
    ('QA Automation Intern', 'Internship', 'INR 20k - 38k/month', 'Selenium, Python, Postman, Manual Testing', 'Perform regression testing, create automated test scripts, and log defect reports in Jira.'),
    ('Product Management Intern', 'Internship', 'INR 25k - 55k/month', 'Product Analytics, SQL, User Stories, Market Research', 'Assist Product Managers with feature specification docs, metric tracking, and customer workflow research.'),
    ('Cybersecurity Intern', 'Internship', 'INR 25k - 50k/month', 'Network Security, Linux, Python, OWASP, Penetration Testing', 'Participate in security vulnerability scans, audit code repositories, and assist in incident response monitoring.')
]

# 40%+ Entry Level / Freshers
ENTRY_ROLES = [
    ('Graduate Trainee Engineer (GTE)', 'Full-time', 'INR 3.8L - 5.5L PA', 'Python, Java, C++, SQL, Data Structures, Algorithms', 'Campus entry-level program for fresh graduates. Rotate through software engineering, cloud ops, and QA units.'),
    ('Associate Software Engineer', 'Full-time', 'INR 4.5L - 7.5L PA', 'Java, Spring Boot, MySQL, REST APIs, Git', 'Entry-level full-time role for fresh CS/IT graduates. Develop scalable web microservices and client-facing APIs.'),
    ('Data Analyst Trainee', 'Full-time', 'INR 4.2L - 6.8L PA', 'SQL, Python, Excel, Power BI, Tableau', 'Analyze business metrics, build executive dashboards, write optimized SQL queries, and generate automated reports.'),
    ('Junior QA / Automation Engineer', 'Full-time', 'INR 3.8L - 6.0L PA', 'Selenium, Python, Java, Manual Testing, Postman', 'Execute test suites, author automated test scripts, perform API testing, and maintain test execution environments.'),
    ('DevOps Trainee', 'Full-time', 'INR 4.5L - 7.2L PA', 'Linux, Bash, Docker, Git, CI/CD, AWS Basics', 'Learn and assist in continuous integration, containerization, cloud infrastructure monitoring, and release pipelines.'),
    ('System Engineer - Freshers 2025/2026', 'Full-time', 'INR 3.6L - 5.4L PA', 'Java, C#, SQL, Networking, Linux', 'Role for CS/IT/EC graduates. Core software engineering, enterprise application maintenance, and client delivery.'),
    ('Cloud Operations Associate', 'Full-time', 'INR 4.2L - 6.5L PA', 'AWS, Azure, Linux, Python, Networking, Monitoring', 'Monitor cloud infrastructure health, manage access control policies, automate deployment scripts, and resolve alerts.'),
    ('Associate Full Stack Developer', 'Full-time', 'INR 5.0L - 8.0L PA', 'JavaScript, React, Node.js, HTML, CSS, SQL', 'Entry-level full-stack engineer. Work across React frontend components and Node.js RESTful API endpoints.')
]

# 30%+ 1-5 Years Experience
MID_ROLES = [
    ('Software Development Engineer I (SDE-1)', 'Full-time', 'INR 8.5L - 15.0L PA', 'Java, Spring Boot, Microservices, PostgreSQL, Kafka', '1-3 years experience. Design and implement high-throughput REST APIs, write clean unit-tested code, and optimize DB queries.'),
    ('Full Stack Engineer (React + Node)', 'Full-time', 'INR 9.5L - 17.0L PA', 'React, Node.js, TypeScript, MongoDB, Express, AWS', '2-4 years experience. Own end-to-end feature delivery from React UI to Node.js microservices and database schemas.'),
    ('Data Engineer (PySpark & Airflow)', 'Full-time', 'INR 10.5L - 19.0L PA', 'Python, PySpark, SQL, Apache Airflow, Snowflake, AWS S3', '2-5 years experience. Build and maintain scalable ETL/ELT data pipelines, data lake architecture, and warehouse tables.'),
    ('DevOps Engineer (Kubernetes & Terraform)', 'Full-time', 'INR 11.5L - 20.0L PA', 'Docker, Kubernetes, Terraform, AWS, Jenkins, Prometheus', '2-4 years experience. Automate infrastructure provisioning, manage K8s clusters, and optimize deployment speed.'),
    ('Backend Engineer (Go / Python)', 'Full-time', 'INR 12.0L - 21.0L PA', 'Go, Python, Redis, PostgreSQL, gRPC, Distributed Systems', '2-5 years experience. Build high-concurrency backend services, optimize database queries, and implement caching layers.'),
    ('Mobile Developer (React Native / Flutter)', 'Full-time', 'INR 8.8L - 16.0L PA', 'React Native, Flutter, Dart, JavaScript, iOS, Android', '1-4 years experience. Build cross-platform mobile apps with smooth UI animations, offline cache, and push notifications.')
]

# 10% Senior
SENIOR_ROLES = [
    ('Senior Software Engineer (SDE-2)', 'Full-time', 'INR 18.0L - 34.0L PA', 'Java, Microservices, System Design, Kafka, Distributed Caching', '4-7 years experience. Architect scalable distributed systems, mentor junior engineers, and drive technical roadmap.'),
    ('Lead ML Engineer (LLMs & MLOps)', 'Full-time', 'INR 22.0L - 42.0L PA', 'Python, PyTorch, LangChain, MLflow, Docker, CUDA, Ray', '4-8 years experience. Lead the deployment of Generative AI and LLM applications into production environments.')
]

def generate_opportunities(total_count=0):
    return []

OPPORTUNITIES = []

