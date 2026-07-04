🛡️ NexusGuard: Enterprise Security & Ethics Auditor

NexusGuard is an automated, AI-powered DevSecOps pipeline and compliance auditing tool. It bridges the gap between technical engineering (code security) and corporate governance (legal and ethics policies) into a single, unified dashboard.

Unlike traditional static analysis tools that only flag vulnerabilities, NexusGuard utilizes Generative AI to actively remediate issues, significantly reducing the Mean Time to Remediation (MTTR) for development teams.

✨ Key Features

1. 🛡️ Automated Static Application Security Testing (SAST)

Utilizes Python's Abstract Syntax Tree (ast) to perform deep codebase scanning without executing the code.

Automatically detects high-risk vulnerabilities like Remote Code Execution vectors (e.g., eval()) and hardcoded secrets/API keys.

2. 📜 Policy & Ethics Compliance Auditing

Ingests corporate policy documents (via compliance_policies.json).

Scans internal documentation, project proposals, and readmes to detect violations of Data Privacy (PII handling), AI Transparency, and other internal governance rules.

3. 🤖 Generative AI Remediation Engine

Integrated with the blazing-fast Groq API (LLaMA-3.3-70b-versatile).

Does not just report bugs—it generates secure, drop-in replacement code patches.

Provides clear, educational "Remediation Rationales" explaining why the patch is secure.

Implements Enterprise-Grade Rate Limiting (Exponential Backoff with RegEx parsing) to gracefully handle API throttling.

4. 📊 Interactive Executive Dashboard

Built with Streamlit to provide a clean, side-by-side comparison of "Vulnerable Code" vs "AI Secure Patch."

Separates Technical Security Flaws and Policy/Ethics Violations into an easy-to-read, manager-friendly UI.

🛠️ Architecture & Tech Stack

Language: Python 3.x

Static Analysis: Native Python ast module

Generative AI: Groq API (OpenAI-compatible endpoints)

Frontend UI: Streamlit

Environment Management: python-dotenv

🚀 Installation & Setup

Prerequisites

Python 3.8 or higher installed on your machine.

A free Groq API Key.

1. Clone the Repository

git clone [https://github.com/ShivaliSenthil/NexusGuard.git](https://github.com/ShivaliSenthil/NexusGuard.git)
cd NexusGuard


2. Install Dependencies

pip install openai streamlit python-dotenv


3. Configure Environment Variables

Create a file named .env in the root directory of the project and add your Groq API key:

GROQ_API_KEY=gsk_YourGroqAPIKeyHere...


(Note: Ensure .env is added to your .gitignore file to prevent leaking secrets!)

4. Run the Dashboard

streamlit run app.py


The application will launch automatically in your default web browser at http://localhost:8501.

📂 How It Works

Target Selection: Enter the path to the repository or directory you wish to scan.

Execution: NexusGuard traverses the directory structure (ignoring standard environments like node_modules and .venv).

Dual-Pipeline Analysis:

.py files are routed to the AST Security Scanner.

.md and .txt files are routed to the Ethics Auditor.

AI Generation: Vulnerabilities are batched and sent to the LLM to generate targeted fixes.

Review: Developers and Compliance Officers can review the dashboard to approve AI-generated patches.

🧪 Customization & Example Files

To help you test the pipeline immediately, this repository includes intentional sample files. You should modify these to fit your organization's needs.

🧪 Built-In Vulnerability Test Suite

To demonstrate the power and versatility of the NexusGuard AST Scanner and AI Remediation engine, this repository includes a suite of intentionally vulnerable files designed to trigger the system's defenses.[Test with your own files]

1. Independent Security Flaws

These files test the pipeline's ability to detect isolated, high-risk security anti-patterns:

data_processor.py: Contains an eval() vulnerability simulating arbitrary code execution via a mathematical input parser. (Demonstrates context-aware AI patching by recommending the secure numexpr library).

api_client.py: Contains heavily exposed, hardcoded secrets (Stripe API keys, GitHub tokens).

legacy_runner.py: Features the highly dangerous exec() function for dynamic script execution alongside hardcoded database and JWT secrets.

bad_code.py: A general testing script combining basic eval() inputs and plaintext passwords.

2. Interconnected OOP Architectures

These files demonstrate NexusGuard's ability to seamlessly scan complex, Object-Oriented code structures:

db_connector.py & user_manager.py: A multi-file OOP structure where user_manager.py imports a DatabaseConnection class. The AST scanner successfully detects hardcoded secrets hidden inside the __init__ constructor and eval() payloads embedded deep within class methods.

3. Policy & Compliance Documents

compliance_policies.json: The core ruleset for the Ethics Auditor. Easily customizable for your organization's specific data privacy and AI fairness requirements.

project_proposal.txt: A sample business document designed to violate the Data Minimization policy, proving the pipeline's ability to audit plain English text against JSON compliance rules.

📸 Screenshots
Here is a look at the NexusGuard Enterprise Dashboard in action:


The main dashboard identifying vulnerabilities and generating AI-powered code patches in real-time.


The compliance auditor flagging a text document for violating internal corporate governance rules.



<img width="1898" height="957" alt="image" src="https://github.com/user-attachments/assets/a1b5b71d-1f84-4d65-896b-236bc55c7df2" />

<img width="1888" height="952" alt="image" src="https://github.com/user-attachments/assets/b0d98520-cdf0-43d9-aaf4-d0baf76a534a" />

<img width="1893" height="965" alt="image" src="https://github.com/user-attachments/assets/453022e5-19d0-49f4-bd11-f5d0ba3d0780" />

<img width="1893" height="950" alt="image" src="https://github.com/user-attachments/assets/43229cb3-45bb-4f61-a81a-0fcf0a0aa89a" />

<img width="1895" height="947" alt="image" src="https://github.com/user-attachments/assets/7df8a98d-2134-44c7-9bbe-01942a6c39fd" />

<img width="1845" height="951" alt="image" src="https://github.com/user-attachments/assets/25cc3ddd-6f6b-48e5-a0a2-2afe11d9c3f6" />

<img width="1882" height="927" alt="image" src="https://github.com/user-attachments/assets/5a0dcee2-8f0e-41c7-9754-308fbb7a75d3" />

<img width="1885" height="877" alt="image" src="https://github.com/user-attachments/assets/88c60d95-9492-43f3-bdff-e137895577b2" />

<img width="1890" height="845" alt="image" src="https://github.com/user-attachments/assets/99106857-4f28-492e-ba75-5e135ededb08" />







