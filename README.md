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

📸 Screenshots

<img width="940" height="408" alt="image" src="https://github.com/user-attachments/assets/9a0e6963-91a1-464a-b79f-91e102427324" />

<img width="940" height="432" alt="image" src="https://github.com/user-attachments/assets/b737effb-f415-4d4f-bfb1-7fcfca9756d4" />

<img width="940" height="434" alt="image" src="https://github.com/user-attachments/assets/a6f32471-224f-4d06-90b3-a38edca4dae4" />

<img width="940" height="376" alt="image" src="https://github.com/user-attachments/assets/550e3012-aa97-4fff-aba8-2c81c4d88b33" />



