import logging
from sqlalchemy.orm import Session
from . import models

logger = logging.getLogger(__name__)

# List of 30 career roles with description, skills, and 3-tiered roadmaps
ROLES_DATA = {
    "Software Engineer (Generalist)": {
        "description": "Designs, develops, and maintains software systems across diverse domains, applying computer science principles to build reliable and scalable software applications.",
        "required_skills": ["Python", "Java", "SQL", "Git", "Data Structures", "Algorithms", "System Design", "Testing"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Fundamentals of Programming", "duration": "4 Weeks", "description": "Learn syntax, control flows, data structures in Python or Java.", "skills_learned": ["Python", "Java"]},
            {"step_number": 2, "topic": "Version Control & Command Line", "duration": "2 Weeks", "description": "Master Git basics, branching, commits, and shell navigation.", "skills_learned": ["Git"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Object-Oriented Programming & Databases", "duration": "4 Weeks", "description": "Understand OOP design principles and relational SQL databases.", "skills_learned": ["SQL", "Data Structures"]},
            {"step_number": 2, "topic": "Testing & Debugging Foundations", "duration": "3 Weeks", "description": "Write unit tests, integrate debugging strategies, and mock data.", "skills_learned": ["Testing"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "System Design & Architecture", "duration": "6 Weeks", "description": "Design distributed architectures, handle caching, load balancing, scaling.", "skills_learned": ["System Design"]},
            {"step_number": 2, "topic": "Algorithms Optimization", "duration": "4 Weeks", "description": "Study complex algorithms, dynamic programming, and complexity tuning.", "skills_learned": ["Algorithms"]}
        ]
    },
    "Frontend Developer": {
        "description": "Creates highly interactive and visually responsive web interfaces, optimizing user experiences across browsers and devices.",
        "required_skills": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Git", "REST APIs", "Tailwind CSS"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Web Layouts with HTML & CSS", "duration": "3 Weeks", "description": "Master document structure, semantic markup, and responsive layouts (Flexbox, Grid).", "skills_learned": ["HTML", "CSS"]},
            {"step_number": 2, "topic": "JavaScript Programming", "duration": "4 Weeks", "description": "Learn variables, DOM manipulation, asynchronous programming, and event handling.", "skills_learned": ["JavaScript"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "React Framework Essentials", "duration": "4 Weeks", "description": "Understand components lifecycle, React Hooks (state, effect), and routing.", "skills_learned": ["React"]},
            {"step_number": 2, "topic": "TypeScript & Styles styling", "duration": "3 Weeks", "description": "Integrate type checks with TypeScript and styling systems like Tailwind CSS.", "skills_learned": ["TypeScript", "Tailwind CSS"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "State Management & Performance", "duration": "5 Weeks", "description": "Manage global state (Redux/Zustand), implement code-splitting, lazy loading.", "skills_learned": ["React", "TypeScript"]},
            {"step_number": 2, "topic": "Server-Side Rendering (Next.js)", "duration": "4 Weeks", "description": "Master Next.js, static site generation, and server actions.", "skills_learned": ["REST APIs"]}
        ]
    },
    "Backend Developer": {
        "description": "Constructs logic, databases, servers, and APIs that power application services from behind the scenes.",
        "required_skills": ["Python", "FastAPI", "SQL", "PostgreSQL", "Docker", "Git", "REST APIs", "System Design"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Backend Programming Syntax", "duration": "3 Weeks", "description": "Learn Python backend frameworks structures and basics of relational databases.", "skills_learned": ["Python", "SQL"]},
            {"step_number": 2, "topic": "API basics with FastAPI", "duration": "3 Weeks", "description": "Build simple RESTful routes, path parameters, and request validation.", "skills_learned": ["FastAPI", "REST APIs"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Databases Integration & ORM", "duration": "4 Weeks", "description": "Integrate PostgreSQL database with FastAPI using SQLAlchemy models.", "skills_learned": ["SQL", "PostgreSQL"]},
            {"step_number": 2, "topic": "Containerization & Deployment", "duration": "3 Weeks", "description": "Build container environments using Docker and docker-compose configurations.", "skills_learned": ["Docker", "Git"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Distributed Architectures & Cache", "duration": "5 Weeks", "description": "Implement microservices architectures, configure Redis cache and message brokers.", "skills_learned": ["System Design"]},
            {"step_number": 2, "topic": "API Security & Logging", "duration": "4 Weeks", "description": "Setup JWT-based authentication, CORS, rate limiting, and elastic log stacks.", "skills_learned": ["REST APIs", "Docker"]}
        ]
    },
    "Full Stack Developer": {
        "description": "Bridges frontend and backend developers by building and maintaining end-to-end user interfaces, server logic, and database operations.",
        "required_skills": ["React", "Node.js", "JavaScript", "TypeScript", "SQL", "Git", "REST APIs", "Docker", "HTML", "CSS"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Web Basics: HTML, CSS & JavaScript", "duration": "4 Weeks", "description": "Learn layout styling and essential programming scripts.", "skills_learned": ["HTML", "CSS", "JavaScript"]},
            {"step_number": 2, "topic": "SQL & Git Foundations", "duration": "3 Weeks", "description": "Understand basic query commands and push/pull version flow.", "skills_learned": ["SQL", "Git"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "React Frontends & Node Backends", "duration": "5 Weeks", "description": "Build single page applications that fetch REST resources from Node server.", "skills_learned": ["React", "Node.js", "REST APIs"]},
            {"step_number": 2, "topic": "Typescript migration", "duration": "3 Weeks", "description": "Refactor APIs and interfaces to utilize static typing.", "skills_learned": ["TypeScript"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "CI/CD & Cloud Orchestrations", "duration": "5 Weeks", "description": "Write Docker build configs, publish images, and deploy automatically to cloud.", "skills_learned": ["Docker", "Git"]},
            {"step_number": 2, "topic": "Architecting Scalable Apps", "duration": "4 Weeks", "description": "Configure system queues, load balancers, and relational query optimizations.", "skills_learned": ["System Design", "SQL"]}
        ]
    },
    "Mobile App Developer (iOS/Android)": {
        "description": "Develops native and cross-platform applications optimized for smartphones, tablets, and wearables.",
        "required_skills": ["Swift", "Kotlin", "Flutter", "Git", "REST APIs", "Mobile Design", "SQLite", "Testing"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Native Languages Foundations", "duration": "4 Weeks", "description": "Learn Swift syntax for iOS or Kotlin syntax for Android.", "skills_learned": ["Swift", "Kotlin"]},
            {"step_number": 2, "topic": "Mobile Layouts & UI Components", "duration": "3 Weeks", "description": "Design layouts using SwiftUI or Jetpack Compose principles.", "skills_learned": ["Mobile Design"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Data Fetching & APIs", "duration": "4 Weeks", "description": "Connect mobile apps to remote RESTful endpoints, parse JSON data dynamically.", "skills_learned": ["REST APIs", "Git"]},
            {"step_number": 2, "topic": "Local Storage & Preferences", "duration": "3 Weeks", "description": "Implement local persistence using SQLite database integrations.", "skills_learned": ["SQLite"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "State Management & Performance Tuning", "duration": "5 Weeks", "description": "Optimize memory allocations, asset loading, background task threads.", "skills_learned": ["Testing"]},
            {"step_number": 2, "topic": "App Stores Deployments", "duration": "3 Weeks", "description": "Configure profiles, handle application signs, test flight distributions.", "skills_learned": ["Git"]}
        ]
    },
    "DevOps Engineer": {
        "description": "Facilitates deployment operations, builds CI/CD pipelines, and manages system automation to bridge development and IT.",
        "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Git", "Terraform", "Python"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Linux Systems & Bash Scripts", "duration": "3 Weeks", "description": "Understand operating system structures, directory operations, shell scripting.", "skills_learned": ["Linux"]},
            {"step_number": 2, "topic": "Git Versioning & Workflows", "duration": "2 Weeks", "description": "Learn git commits, branch merges, pull requests, hooks.", "skills_learned": ["Git"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Docker Containerization", "duration": "4 Weeks", "description": "Write standard Dockerfiles and set up multi-container orchestrations.", "skills_learned": ["Docker"]},
            {"step_number": 2, "topic": "CI/CD Automation", "duration": "3 Weeks", "description": "Write pipeline workflows using Github Actions or Jenkins.", "skills_learned": ["CI/CD", "Python"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Infrastructure as Code & Cloud", "duration": "5 Weeks", "description": "Provision cloud systems on AWS using Terraform configuration templates.", "skills_learned": ["Terraform", "AWS"]},
            {"step_number": 2, "topic": "Kubernetes Clusters Orchestration", "duration": "5 Weeks", "description": "Configure cluster management, pods distributions, service routing.", "skills_learned": ["Kubernetes"]}
        ]
    },
    "Site Reliability Engineer (SRE)": {
        "description": "Applies software engineering practices to system administration, ensuring infrastructure is highly available, scalable, and self-healing.",
        "required_skills": ["Python", "Linux", "Kubernetes", "AWS", "CI/CD", "Prometheus", "System Design", "Networking"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Networking & Operating Systems", "duration": "4 Weeks", "description": "Master TCP/IP protocols, DNS configurations, ports routing, Linux operations.", "skills_learned": ["Networking", "Linux"]},
            {"step_number": 2, "topic": "Automation Scripting", "duration": "3 Weeks", "description": "Write system maintenance automation scripts using Python.", "skills_learned": ["Python"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Containers & Cloud Services", "duration": "4 Weeks", "description": "Manage virtual container instances on AWS configurations.", "skills_learned": ["AWS", "Kubernetes"]},
            {"step_number": 2, "topic": "CI/CD Orchestrations", "duration": "3 Weeks", "description": "Configure deployment pipelines with automated health checks.", "skills_learned": ["CI/CD"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Observability & Alerting Systems", "duration": "5 Weeks", "description": "Build monitoring dashboards with Prometheus, Grafana, alerts triggers.", "skills_learned": ["Prometheus", "System Design"]},
            {"step_number": 2, "topic": "Disaster Recovery Protocols", "duration": "4 Weeks", "description": "Architect self-healing nodes, backups schedules, traffic routing.", "skills_learned": ["System Design"]}
        ]
    },
    "Data Scientist": {
        "description": "Analyzes complex patterns in big data and builds predictive machine learning structures to derive valuable business metrics.",
        "required_skills": ["Python", "SQL", "Machine Learning", "Pandas", "NumPy", "Scikit-Learn", "Statistics", "Data Visualization"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Python Data Structures & SQL", "duration": "4 Weeks", "description": "Master SQL querying, aggregation, filtering alongside core Python scripts.", "skills_learned": ["Python", "SQL"]},
            {"step_number": 2, "topic": "Math & Applied Statistics", "duration": "3 Weeks", "description": "Study probability distributions, statistical test models, metrics distributions.", "skills_learned": ["Statistics"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Data Wrangling & Analysis", "duration": "4 Weeks", "description": "Load, manipulate, clean, and pre-process datasets using Pandas and NumPy.", "skills_learned": ["Pandas", "NumPy"]},
            {"step_number": 2, "topic": "Machine Learning Foundations", "duration": "5 Weeks", "description": "Learn regression, clustering, classification methods using Scikit-Learn.", "skills_learned": ["Machine Learning", "Scikit-Learn"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Advanced Feature Engineering", "duration": "4 Weeks", "description": "Transform data variables, resolve imbalances, select optimal features.", "skills_learned": ["Machine Learning"]},
            {"step_number": 2, "topic": "Deep Learning & Model Tuning", "duration": "5 Weeks", "description": "Tune hyperparameters, study neural models, deploy predictive endpoints.", "skills_learned": ["Data Visualization", "Statistics"]}
        ]
    },
    "Data Analyst": {
        "description": "Gathers, organizes, cleans, and translates raw database numbers into beautiful visualizations and reports to support decision making.",
        "required_skills": ["SQL", "Excel", "Tableau", "Python", "Data Visualization", "Statistics", "Git", "Pandas"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Excel & Spreadsheet Modeling", "duration": "3 Weeks", "description": "Master advanced formulas, pivot summaries, and chart formatting.", "skills_learned": ["Excel"]},
            {"step_number": 2, "topic": "SQL Query Basics", "duration": "3 Weeks", "description": "Learn SELECT statements, JOIN logic, sorting, filtering databases.", "skills_learned": ["SQL"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "BI Dashboards with Tableau", "duration": "4 Weeks", "description": "Design user dashboards, connect databases, create interactive graphs.", "skills_learned": ["Tableau", "Data Visualization"]},
            {"step_number": 2, "topic": "Basic Python Scripting", "duration": "3 Weeks", "description": "Learn variables, files input, basic data wrangling libraries.", "skills_learned": ["Python", "Pandas"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Applied Statistical Evaluations", "duration": "4 Weeks", "description": "Conduct hypothesis testing, identify correlation ratios, perform trend analyses.", "skills_learned": ["Statistics"]},
            {"step_number": 2, "topic": "Reports Automations", "duration": "3 Weeks", "description": "Write automated scheduled queries that refresh sheets automatically.", "skills_learned": ["Git"]}
        ]
    },
    "Data Engineer": {
        "description": "Constructs scalable data pipelines, data warehouses, and distributed systems to route big data streams reliably.",
        "required_skills": ["Python", "SQL", "Spark", "AWS", "Airflow", "Kafka", "Data Warehousing", "Git"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Database Foundations & Python", "duration": "4 Weeks", "description": "Write complex SQL analytical queries, set indexes, optimize structures.", "skills_learned": ["SQL", "Python"]},
            {"step_number": 2, "topic": "Version Control & Linux Environments", "duration": "2 Weeks", "description": "Configure development machines, write basic cron configurations.", "skills_learned": ["Git"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "ELT/ETL Pipelines with Airflow", "duration": "4 Weeks", "description": "Orchestrate recurring pipeline dependencies using Apache Airflow DAGs.", "skills_learned": ["Airflow", "Data Warehousing"]},
            {"step_number": 2, "topic": "Cloud Storage & Warehouses", "duration": "3 Weeks", "description": "Load structured streams into AWS Redshift or S3 target buckets.", "skills_learned": ["AWS"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Big Data Engines with Spark", "duration": "5 Weeks", "description": "Deploy distributed batch operations across memory clusters with PySpark.", "skills_learned": ["Spark"]},
            {"step_number": 2, "topic": "Streaming Data Pipelines", "duration": "4 Weeks", "description": "Implement event streams and queuing layers using Apache Kafka systems.", "skills_learned": ["Kafka"]}
        ]
    },
    "Machine Learning Engineer": {
        "description": "Researches, builds, and deploys scalable production models, optimizing AI applications for speed and prediction accuracy.",
        "required_skills": ["Python", "Machine Learning", "TensorFlow", "PyTorch", "Git", "Docker", "SQL", "System Design"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Data Wrangling & Core Math", "duration": "4 Weeks", "description": "Learn matrix operations, calculus basics, and python plotting.", "skills_learned": ["Python", "SQL"]},
            {"step_number": 2, "topic": "Predictive Models with Scikit-Learn", "duration": "4 Weeks", "description": "Master standard supervised learning algorithms execution.", "skills_learned": ["Machine Learning"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Deep Learning Foundations", "duration": "5 Weeks", "description": "Build multi-layer artificial networks using TensorFlow and PyTorch.", "skills_learned": ["TensorFlow", "PyTorch"]},
            {"step_number": 2, "topic": "Version Control & Containerization", "duration": "3 Weeks", "description": "Package prediction systems into predictable local containers.", "skills_learned": ["Git", "Docker"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Model Deployment & System Design", "duration": "5 Weeks", "description": "Deploy prediction models as highly performant microservice REST endpoints.", "skills_learned": ["System Design"]},
            {"step_number": 2, "topic": "MLOps & Pipelines Monitoring", "duration": "4 Weeks", "description": "Setup auto-retraining workflows, model drift monitors.", "skills_learned": ["Docker"]}
        ]
    },
    "Deep Learning Engineer": {
        "description": "Specializes in training artificial neural networks (CNNs, RNNs, Transformers) for parsing high-dimensional unstructured media.",
        "required_skills": ["Python", "Deep Learning", "PyTorch", "TensorFlow", "GPU Programming", "Git", "Math", "System Design"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Advanced Linear Algebra & Python", "duration": "4 Weeks", "description": "Understand vector spaces, eigenvalue decompositions, tensor shapes.", "skills_learned": ["Python", "Math"]},
            {"step_number": 2, "topic": "Neural Network Basics", "duration": "3 Weeks", "description": "Implement simple feedforward layers, backpropagations formulas.", "skills_learned": ["Deep Learning"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "PyTorch Deep Framework", "duration": "5 Weeks", "description": "Write custom dataset pipelines, custom neural layers in PyTorch.", "skills_learned": ["PyTorch", "Git"]},
            {"step_number": 2, "topic": "CNNs & Image Classifications", "duration": "4 Weeks", "description": "Train convolutional models for parsing structural grid inputs.", "skills_learned": ["TensorFlow"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Transformers & Attention Networks", "duration": "5 Weeks", "description": "Understand transformer weights architectures, self-attention calculations.", "skills_learned": ["System Design"]},
            {"step_number": 2, "topic": "GPU optimizations", "duration": "4 Weeks", "description": "Implement CUDA memory checks, batch parallelisms, mixed-precision trainings.", "skills_learned": ["GPU Programming"]}
        ]
    },
    "NLP Engineer": {
        "description": "Builds algorithmic models to understand, analyze, translate, and generate human written languages and conversational streams.",
        "required_skills": ["Python", "NLP", "PyTorch", "Hugging Face", "Transformers", "Git", "SQL", "Tokenization"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "String Processing & Regex", "duration": "3 Weeks", "description": "Learn pattern parsing, regex libraries, string cleaning methods.", "skills_learned": ["Python", "Tokenization"]},
            {"step_number": 2, "topic": "Basic Text Vectorization", "duration": "3 Weeks", "description": "Implement TF-IDF algorithms, bag-of-words classifications.", "skills_learned": ["NLP"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Word Embeddings & RNNs", "duration": "4 Weeks", "description": "Implement Word2Vec algorithms, sequence parsing with LSTM cells.", "skills_learned": ["NLP", "PyTorch"]},
            {"step_number": 2, "topic": "Text Processing at Scale", "duration": "3 Weeks", "description": "Analyze text using NLTK, Spacy libraries, tokenization APIs.", "skills_learned": ["Git", "SQL"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Transformer models & Hugging Face", "duration": "5 Weeks", "description": "Fine-tune pretrained BERT/GPT models using Hugging Face pipelines.", "skills_learned": ["Transformers", "Hugging Face"]},
            {"step_number": 2, "topic": "Large Language Models Fine-Tuning", "duration": "4 Weeks", "description": "Implement LoRA, QLoRA methods, sequence token generation configurations.", "skills_learned": ["Transformers"]}
        ]
    },
    "Computer Vision Engineer": {
        "description": "Applies image processing algorithms and neural networks to enable computers to extract structured metadata from visual inputs.",
        "required_skills": ["Python", "OpenCV", "PyTorch", "Deep Learning", "Computer Vision", "Git", "Math", "C++"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Image Coordinates & Matrix Math", "duration": "3 Weeks", "description": "Understand digital colors, image matrices, kernel transformations.", "skills_learned": ["Python", "Math"]},
            {"step_number": 2, "topic": "Traditional CV with OpenCV", "duration": "3 Weeks", "description": "Implement edge detection filters, contours tracking, morphings.", "skills_learned": ["OpenCV"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Object Detection Networks", "duration": "4 Weeks", "description": "Train YOLO, SSD architectures to predict boundary box dimensions.", "skills_learned": ["Computer Vision", "PyTorch"]},
            {"step_number": 2, "topic": "Image Segmentations", "duration": "4 Weeks", "description": "Implement pixel-wise masks matching with U-Net structures.", "skills_learned": ["Deep Learning", "Git"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "CV in C++", "duration": "5 Weeks", "description": "Re-write python visual models to highly optimized C++ classes.", "skills_learned": ["C++"]},
            {"step_number": 2, "topic": "Edge Deployments", "duration": "4 Weeks", "description": "Optimize deep vision models using TensorRT for embedded microchips.", "skills_learned": ["Computer Vision"]}
        ]
    },
    "Cloud Architect": {
        "description": "Designs cloud environments, migration routes, and security architectures to support enterprise applications deployment.",
        "required_skills": ["AWS", "Azure", "Linux", "Terraform", "Cloud Security", "Networking", "Git", "System Design"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Cloud Basics & Platforms", "duration": "4 Weeks", "description": "Learn storage layers, compute nodes, billing models on AWS.", "skills_learned": ["AWS", "Azure"]},
            {"step_number": 2, "topic": "Systems Networking", "duration": "3 Weeks", "description": "Understand subnets configuration, route tables, DNS, SSH connections.", "skills_learned": ["Networking", "Linux"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Infrastructure as Code", "duration": "4 Weeks", "description": "Provision modular cloud resources using Terraform modules.", "skills_learned": ["Terraform", "Git"]},
            {"step_number": 2, "topic": "Cloud Security Policies", "duration": "3 Weeks", "description": "Configure IAM structures, directory services, VPN tunnels.", "skills_learned": ["Cloud Security"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Architecting Hybrid systems", "duration": "5 Weeks", "description": "Design failover paths, scale-outs load balancers, multi-region replication.", "skills_learned": ["System Design"]},
            {"step_number": 2, "topic": "Cost Optimization Policies", "duration": "3 Weeks", "description": "Analyze spending metrics, resource lifetimes, reserved nodes options.", "skills_learned": ["System Design"]}
        ]
    },
    "Cybersecurity Analyst": {
        "description": "Monitors network activities, identifies vulnerabilities, configures firewalls, and mitigates security threats.",
        "required_skills": ["Networking", "Linux", "SIEM Tools", "Security Auditing", "Python", "Cryptography", "Firewalls", "Wireshark"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Networking Foundations", "duration": "4 Weeks", "description": "Study OSI layers, IP schemas, UDP/TCP protocols, network headers.", "skills_learned": ["Networking"]},
            {"step_number": 2, "topic": "Linux Systems Administration", "duration": "3 Weeks", "description": "Manage user permissions, groups, configuration files, system processes.", "skills_learned": ["Linux"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Traffic Analysis & Wireshark", "duration": "4 Weeks", "description": "Capture packets, inspect packet parameters, trace suspicious requests.", "skills_learned": ["Wireshark", "Networking"]},
            {"step_number": 2, "topic": "Scripting Security automations", "duration": "3 Weeks", "description": "Write log-parsing scripts and port scans scripts using Python.", "skills_learned": ["Python", "Linux"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "SIEM Deployments", "duration": "5 Weeks", "description": "Deploy Splunk/ELK stack log analysis models, define alert triggers.", "skills_learned": ["SIEM Tools", "Security Auditing"]},
            {"step_number": 2, "topic": "Threat mitigations & cryptographic policies", "duration": "4 Weeks", "description": "Implement public key configurations, firewall policies configurations.", "skills_learned": ["Cryptography", "Firewalls"]}
        ]
    },
    "Penetration Tester": {
        "description": "Performs authorized simulated attacks against applications, networks, and computer systems to expose weak access pathways.",
        "required_skills": ["Linux", "Metasploit", "Python", "Networking", "Web Application Hacking", "Nmap", "Burp Suite", "Git"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Scanning Networks with Nmap", "duration": "3 Weeks", "description": "Discover open ports, active services, version specs, operating systems.", "skills_learned": ["Nmap", "Networking"]},
            {"step_number": 2, "topic": "Kali Linux Basics", "duration": "3 Weeks", "description": "Familiarize yourself with pentesting tools catalogs, script paths.", "skills_learned": ["Linux"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Web Hacking with Burp Suite", "duration": "4 Weeks", "description": "Intercept request payloads, test injection headers, perform brute-forcing.", "skills_learned": ["Burp Suite", "Web Application Hacking"]},
            {"step_number": 2, "topic": "Exploit frameworks", "duration": "4 Weeks", "description": "Configure targets, deploy payloads using Metasploit framework.", "skills_learned": ["Metasploit", "Git"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Custom Exploit writing", "duration": "5 Weeks", "description": "Write custom port scans, customized injection payloads in Python.", "skills_learned": ["Python"]},
            {"step_number": 2, "topic": "Privilege Escalations", "duration": "4 Weeks", "description": "Identify configuration oversights, kernel bugs, hijack active tokens.", "skills_learned": ["Linux"]}
        ]
    },
    "Database Administrator (DBA)": {
        "description": "Manages, backs up, secures, and tunes relational and non-relational database engines for continuous uptime.",
        "required_skills": ["SQL", "PostgreSQL", "MySQL", "Database Administration", "Backup & Recovery", "Linux", "Git", "Security"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "SQL Query Syntax", "duration": "3 Weeks", "description": "Master table creation, filtering commands, aggregation triggers.", "skills_learned": ["SQL"]},
            {"step_number": 2, "topic": "Relational Theories", "duration": "3 Weeks", "description": "Understand key schemas, foreign constraints, normalization normalization rules.", "skills_learned": ["Database Administration"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Engine Installations & Configs", "duration": "4 Weeks", "description": "Install PostgreSQL on Linux servers, customize configs.", "skills_learned": ["PostgreSQL", "Linux"]},
            {"step_number": 2, "topic": "Backup Plans & Recovery Procedures", "duration": "3 Weeks", "description": "Setup daily dump schedules, test tables recoveries procedures.", "skills_learned": ["Backup & Recovery", "Git"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Performance Index optimization", "duration": "5 Weeks", "description": "Analyze slow queries log, build optimal composite indices.", "skills_learned": ["SQL", "MySQL"]},
            {"step_number": 2, "topic": "High Availability Clusters", "duration": "4 Weeks", "description": "Deploy write-ahead logging replication, configure master-slave configurations.", "skills_learned": ["Security"]}
        ]
    },
    "Product Manager": {
        "description": "Defines product strategies, roadmaps, and requirements, coordinating with engineering and design to launch high-impact features.",
        "required_skills": ["Project Management", "Agile", "Scrum", "User Research", "Analytics", "SQL", "Product Roadmaps", "Communication"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Agile framework principles", "duration": "3 Weeks", "description": "Understand sprint cycles, backlog creation, user story formats.", "skills_learned": ["Agile", "Scrum"]},
            {"step_number": 2, "topic": "Active user research methods", "duration": "3 Weeks", "description": "Prepare surveys, perform interview queries, document user problems.", "skills_learned": ["User Research"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Defining Product Metrics", "duration": "4 Weeks", "description": "Configure product funnel analytics, measure churn ratios.", "skills_learned": ["Analytics", "Project Management"]},
            {"step_number": 2, "topic": "SQL query filters", "duration": "3 Weeks", "description": "Write database metrics checks without relying on engineering.", "skills_learned": ["SQL"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Strategic Roadmaps construction", "duration": "4 Weeks", "description": "Prioritize deliverables using RICE, map feature dependencies timelines.", "skills_learned": ["Product Roadmaps"]},
            {"step_number": 2, "topic": "Stakeholders Alignments", "duration": "3 Weeks", "description": "Negotiate timelines, compile business justification pitches.", "skills_learned": ["Communication"]}
        ]
    },
    "Project Manager": {
        "description": "Orchestrates timelines, resources, and stakeholder communications to deliver projects on time and within scope constraints.",
        "required_skills": ["Project Management", "Agile", "Scrum", "Risk Management", "Jira", "Budgeting", "Communication", "Documentation"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Project Lifecycles", "duration": "3 Weeks", "description": "Study timeline planning, project kickoffs, deliverables definition.", "skills_learned": ["Project Management"]},
            {"step_number": 2, "topic": "Agile & Scrum basics", "duration": "3 Weeks", "description": "Learn story points, review sprints, organize standup schedules.", "skills_learned": ["Agile", "Scrum"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Jira Project Tracking", "duration": "3 Weeks", "description": "Manage boards configuration, build custom filters, tracking graphs.", "skills_learned": ["Jira"]},
            {"step_number": 2, "topic": "Budgeting & Resources plans", "duration": "4 Weeks", "description": "Calculate expenditures, estimate labor allocation limits.", "skills_learned": ["Budgeting", "Risk Management"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Strategic Risk Mitigation plans", "duration": "4 Weeks", "description": "Identify bottlenecks, plan backup allocations, write contingency plans.", "skills_learned": ["Risk Management"]},
            {"step_number": 2, "topic": "Stakeholder reporting structures", "duration": "3 Weeks", "description": "Design status dashboards, lead milestone review alignments.", "skills_learned": ["Communication", "Documentation"]}
        ]
    },
    "UI/UX Designer": {
        "description": "Researches user needs, builds wireframes, and designs high-fidelity interactive user interfaces.",
        "required_skills": ["Figma", "UI/UX Design", "Wireframing", "Prototyping", "User Research", "HTML", "CSS", "User Testing"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Figma layout vector tools", "duration": "3 Weeks", "description": "Master design coordinates, paths, grid templates, fonts layout.", "skills_learned": ["Figma"]},
            {"step_number": 2, "topic": "Design layout principles", "duration": "3 Weeks", "description": "Understand typography sizes, color theories, spacing balance.", "skills_learned": ["UI/UX Design"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Wireframes & Interactive Prototypes", "duration": "4 Weeks", "description": "Create clickable low-fidelity flows, build transition animations.", "skills_learned": ["Wireframing", "Prototyping"]},
            {"step_number": 2, "topic": "Web Styling constraints", "duration": "3 Weeks", "description": "Learn HTML grid structures, responsive layout constraints.", "skills_learned": ["HTML", "CSS"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "User testing methodologies", "duration": "4 Weeks", "description": "Perform task analysis, review click counts, adjust layouts.", "skills_learned": ["User Research", "User Testing"]},
            {"step_number": 2, "topic": "Design System management", "duration": "4 Weeks", "description": "Construct component libraries, style tokens, variants configurations.", "skills_learned": ["Figma"]}
        ]
    },
    "QA Automation Engineer": {
        "description": "Writes automated test scripts to validate software quality, performance, and API reliability.",
        "required_skills": ["Python", "Selenium", "Testing", "Git", "Playwright", "CI/CD", "SQL", "REST APIs"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Python Programming", "duration": "3 Weeks", "description": "Master variables, loops, writing functions, list structures.", "skills_learned": ["Python", "Git"]},
            {"step_number": 2, "topic": "Test cases writing", "duration": "3 Weeks", "description": "Write clear assertions, edge conditions specifications.", "skills_learned": ["Testing"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Web Automations with Selenium", "duration": "4 Weeks", "description": "Locate HTML nodes, simulate clicks, assert UI text states.", "skills_learned": ["Selenium", "Playwright"]},
            {"step_number": 2, "topic": "API Testing", "duration": "3 Weeks", "description": "Validate REST response status, headers schemas using Python.", "skills_learned": ["REST APIs", "SQL"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Automation Pipeline integration", "duration": "4 Weeks", "description": "Integrate test suites with Github Actions to trigger automatically on code updates.", "skills_learned": ["CI/CD"]},
            {"step_number": 2, "topic": "Test Frameworks development", "duration": "5 Weeks", "description": "Build reusable fixtures, reports automation generators.", "skills_learned": ["Testing"]}
        ]
    },
    "QA Manual Tester": {
        "description": "Performs exploratory and regression testing, writing clear bug reports to verify application features work.",
        "required_skills": ["Testing", "Bug Tracking", "Documentation", "Excel", "Jira", "SQL", "Git", "Test Case Design"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Test Cases Design", "duration": "3 Weeks", "description": "Write pre-conditions steps, execution steps, expected outcomes.", "skills_learned": ["Test Case Design"]},
            {"step_number": 2, "topic": "Bug report parameters", "duration": "3 Weeks", "description": "Document steps to reproduce, prioritize impact classifications.", "skills_learned": ["Bug Tracking"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Jira Defect Management", "duration": "3 Weeks", "description": "Link bug tickets to developmental stories, monitor status pipelines.", "skills_learned": ["Jira", "Testing"]},
            {"step_number": 2, "topic": "Excel data models", "duration": "3 Weeks", "description": "Manage custom matrices for keeping track of test layouts.", "skills_learned": ["Excel"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Exploratory & Database testing", "duration": "4 Weeks", "description": "Perform query evaluations to verify data persistency backend.", "skills_learned": ["SQL"]},
            {"step_number": 2, "topic": "Test Plans construction", "duration": "4 Weeks", "description": "Scope testing bounds, allocate schedules across regression cycles.", "skills_learned": ["Documentation", "Git"]}
        ]
    },
    "Solutions Architect": {
        "description": "Translates business requirements into reliable technical configurations, ensuring successful system integration.",
        "required_skills": ["System Design", "Cloud Infrastructure", "System Integration", "Security", "Networking", "Git", "AWS", "Communication"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Cloud Infrastructure Concepts", "duration": "4 Weeks", "description": "Learn storage layers, virtual networks, compute instances on AWS.", "skills_learned": ["AWS", "Cloud Infrastructure"]},
            {"step_number": 2, "topic": "Systems Networking", "duration": "3 Weeks", "description": "Study DNS configurations, VPN boundaries, TCP connections.", "skills_learned": ["Networking"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Integration Architectures", "duration": "4 Weeks", "description": "Design REST services, queue pipelines, files transfers configurations.", "skills_learned": ["System Integration", "Git"]},
            {"step_number": 2, "topic": "Cloud Security Frameworks", "duration": "3 Weeks", "description": "Configure directories services, access policies, encryption protocols.", "skills_learned": ["Security"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "System Design & Pitching", "duration": "5 Weeks", "description": "Draft high-level diagram templates, pitch structures to stakeholders.", "skills_learned": ["System Design", "Communication"]},
            {"step_number": 2, "topic": "Scalability & Failover Auditing", "duration": "4 Weeks", "description": "Audit system designs for single point of failure bottlenecks.", "skills_learned": ["System Design"]}
        ]
    },
    "Embedded Systems Engineer": {
        "description": "Develops low-level firmware and device drivers, optimizing code performance for microcontrollers and specialized hardware.",
        "required_skills": ["C", "C++", "Microcontrollers", "Debugging", "RTOS", "Electronics", "Git", "Hardware Design"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "C programming syntax", "duration": "4 Weeks", "description": "Master pointers concepts, memory registers, structure layouts in C.", "skills_learned": ["C"]},
            {"step_number": 2, "topic": "Hardware Basics", "duration": "3 Weeks", "description": "Read schematic drawings, understand voltages, logic gates.", "skills_learned": ["Electronics"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Microcontrollers peripheral config", "duration": "5 Weeks", "description": "Write drivers for I2C, SPI, UART communication buses.", "skills_learned": ["Microcontrollers", "Git"]},
            {"step_number": 2, "topic": "Debugging with Oscilloscopes", "duration": "3 Weeks", "description": "Locate signaling issues, trace logic states, measure latency.", "skills_learned": ["Debugging"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Real-Time Operating Systems (RTOS)", "duration": "5 Weeks", "description": "Create task threads, configure semaphores, manage task prioritization.", "skills_learned": ["RTOS"]},
            {"step_number": 2, "topic": "Firmware Optimizations", "duration": "4 Weeks", "description": "Reduce flash utilization, configure deep sleep battery modes.", "skills_learned": ["C++", "Hardware Design"]}
        ]
    },
    "IoT Engineer": {
        "description": "Bridges embedded hardware sensors with cloud processing layers, establishing connected device networks.",
        "required_skills": ["Python", "C++", "MQTT", "AWS IoT", "Raspberry Pi", "Networking", "Electronics", "Git"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Raspberry Pi & Python Basics", "duration": "4 Weeks", "description": "Access GPIO pins, write sensor reading scripts in Python.", "skills_learned": ["Python", "Raspberry Pi"]},
            {"step_number": 2, "topic": "Electronics Foundations", "duration": "3 Weeks", "description": "Construct circuit layouts using breadboards, measure signals.", "skills_learned": ["Electronics"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "IoT Communications (MQTT)", "duration": "4 Weeks", "description": "Publish sensor updates to local brokers using MQTT protocol.", "skills_learned": ["MQTT", "Networking"]},
            {"step_number": 2, "topic": "Microcontroller C++ firmware", "duration": "4 Weeks", "description": "Configure ESP32 Wi-Fi routines, parse target JSON templates.", "skills_learned": ["C++", "Git"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "AWS IoT Cloud configuration", "duration": "5 Weeks", "description": "Connect devices to AWS Core registry, write SQL routing rules.", "skills_learned": ["AWS IoT"]},
            {"step_number": 2, "topic": "Fleet management & OTA updates", "duration": "4 Weeks", "description": "Design firmware signing, rollout updates safely across node groups.", "skills_learned": ["AWS IoT"]}
        ]
    },
    "Game Developer": {
        "description": "Engineers interactive gameplay systems, mechanics, physics engines, and graphics workflows for digital entertainment products.",
        "required_skills": ["C#", "Unity", "C++", "Unreal Engine", "Linear Algebra", "Physics", "Git", "3D Math"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "C# Programming & Unity", "duration": "4 Weeks", "description": "Understand scripts compilation, loops, objects instantiation.", "skills_learned": ["C#", "Unity"]},
            {"step_number": 2, "topic": "Linear Algebra & Vectors", "duration": "3 Weeks", "description": "Understand 3D coordinate transformations, dot products.", "skills_learned": ["Linear Algebra", "3D Math"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Gameplay Mechanics Design", "duration": "4 Weeks", "description": "Configure movement triggers, physics layers collisions.", "skills_learned": ["Physics", "Git"]},
            {"step_number": 2, "topic": "Unreal C++ Framework", "duration": "5 Weeks", "description": "Learn actors architecture, memory management in Unreal Engine.", "skills_learned": ["C++", "Unreal Engine"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Shaders & Graphics Pipelines", "duration": "5 Weeks", "description": "Write custom render passes, optimize polygon draw call counts.", "skills_learned": ["3D Math"]},
            {"step_number": 2, "topic": "Networking Gameplay", "duration": "5 Weeks", "description": "Implement client predictions models, lag compensations setups.", "skills_learned": ["Unity"]}
        ]
    },
    "Blockchain Developer": {
        "description": "Designs decentralized architectures, writes secure smart contracts, and deploys decentralized applications (dApps).",
        "required_skills": ["Solidity", "Cryptography", "JavaScript", "TypeScript", "Ethereum", "Smart Contracts", "Git", "Go"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Web3 & JavaScript basics", "duration": "3 Weeks", "description": "Learn asynchronous JavaScript script, connecting to wallets.", "skills_learned": ["JavaScript", "Git"]},
            {"step_number": 2, "topic": "Cryptographic Foundations", "duration": "3 Weeks", "description": "Understand hashes functions, asymmetric signatures keys.", "skills_learned": ["Cryptography"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Solidity Smart Contracts writing", "duration": "5 Weeks", "description": "Write secure contracts, manage state variables, handle gas optimization.", "skills_learned": ["Solidity", "Smart Contracts"]},
            {"step_number": 2, "topic": "DApps development integration", "duration": "4 Weeks", "description": "Build interfaces that communicate with contract functions via ethers.js.", "skills_learned": ["Ethereum", "TypeScript"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Smart Contracts Security Audits", "duration": "5 Weeks", "description": "Expose reentrancy vectors, use auditing tools like Slither.", "skills_learned": ["Smart Contracts"]},
            {"step_number": 2, "topic": "Layer 2 scaling & Go chains", "duration": "4 Weeks", "description": "Configure custom EVM execution layers, write Go clients.", "skills_learned": ["Go"]}
        ]
    },
    "Technical Writer": {
        "description": "Translates complex system engineering designs into clear, developer-friendly documentation manuals and API references.",
        "required_skills": ["Documentation", "Markdown", "Git", "Technical Writing", "API Documentation", "HTML", "CSS", "Research"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Markdown & Styling formats", "duration": "3 Weeks", "description": "Master headings layouts, table syntax, syntax highlighting code formatting.", "skills_learned": ["Markdown"]},
            {"step_number": 2, "topic": "Git docs repositories", "duration": "3 Weeks", "description": "Learn git commits, resolving documentation review conflicts.", "skills_learned": ["Git"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "OpenAPI/Swagger specs writer", "duration": "4 Weeks", "description": "Document request formats, response bodies schemas using YAML formats.", "skills_learned": ["API Documentation", "Research"]},
            {"step_number": 2, "topic": "CSS styles layouts", "duration": "3 Weeks", "description": "Customize custom stylesheet guides templates, build site themes.", "skills_learned": ["HTML", "CSS"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Docs as Code automation pipelines", "duration": "4 Weeks", "description": "Auto-deploy static docs pages using MkDocs, Github Actions.", "skills_learned": ["Git", "Technical Writing"]},
            {"step_number": 2, "topic": "API Reference testing", "duration": "4 Weeks", "description": "Execute CURL requests, verify endpoints output details before publishing.", "skills_learned": ["Documentation"]}
        ]
    },
    "Scrum Master": {
        "description": "Facilitates sprint cycles, resolves workflow blockers, and champions Agile methodologies across product teams.",
        "required_skills": ["Agile", "Scrum", "Jira", "Conflict Resolution", "Communication", "Facilitation", "Documentation", "Project Management"],
        "beginner_roadmap": [
            {"step_number": 1, "topic": "Scrum guide framework", "duration": "3 Weeks", "description": "Familiarize yourself with scrum roles, events cycles, artifact definitions.", "skills_learned": ["Scrum"]},
            {"step_number": 2, "topic": "Agile philosophies", "duration": "3 Weeks", "description": "Master collaborative values, adaptive feedback cycles, self-organizing teams.", "skills_learned": ["Agile"]}
        ],
        "intermediate_roadmap": [
            {"step_number": 1, "topic": "Jira Board configs", "duration": "3 Weeks", "description": "Customize backlog boards, sprint metrics trackers, velocity charts.", "skills_learned": ["Jira", "Project Management"]},
            {"step_number": 2, "topic": "Facilitating Sprint reviews", "duration": "4 Weeks", "description": "Organize retrospectives, run card collections, group feedback.", "skills_learned": ["Facilitation", "Communication"]}
        ],
        "advanced_roadmap": [
            {"step_number": 1, "topic": "Resolving workflow blockers", "duration": "4 Weeks", "description": "Detect cross-team constraints dependencies, negotiate blocker solutions.", "skills_learned": ["Conflict Resolution"]},
            {"step_number": 2, "topic": "Agile adoption policies", "duration": "4 Weeks", "description": "Establish agile metrics models across larger organization teams.", "skills_learned": ["Agile", "Documentation"]}
        ]
    }
}

def seed_roles(db: Session):
    """
    Check if the database contains the 30 career roles. 
    If not, seed them into the database from the ROLES_DATA dictionary.
    """
    try:
        count = db.query(models.CareerRole).count()
        if count >= 30:
            logger.info("Roles database already seeded with %d roles.", count)
            return

        logger.info("Seeding career roles into SQLite database...")
        for role_name, data in ROLES_DATA.items():
            # Check if this specific role is present
            role_record = db.query(models.CareerRole).filter(models.CareerRole.name == role_name).first()
            if not role_record:
                db_role = models.CareerRole(
                    name=role_name,
                    description=data["description"],
                    required_skills=data["required_skills"],
                    beginner_roadmap=data["beginner_roadmap"],
                    intermediate_roadmap=data["intermediate_roadmap"],
                    advanced_roadmap=data["advanced_roadmap"]
                )
                db.add(db_role)
        
        db.commit()
        logger.info("Successfully seeded all 30 career roles.")
    except Exception as e:
        db.rollback()
        logger.error("Error seeding career roles: %s", str(e))
