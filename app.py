import os
import ast
import json
import time
import re
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI  # Use the standard OpenAI client for Groq

# =====================================================================
# 1. SETUP & CONFIGURATION
# =====================================================================
st.set_page_config(page_title="NexusGuard Enterprise Auditor", page_icon="🛡️", layout="wide")

load_dotenv()
# Changed variable to explicitly check for GROQ_API_KEY
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("⚠️ GROQ_API_KEY not found! Please create a .env file and add your key.")
    st.stop()

# Initialize the client pointing to Groq's API
ai_client = OpenAI(
    api_key=GROQ_API_KEY, 
    base_url="https://api.groq.com/openai/v1"
)

# =====================================================================
# 2. BACKEND SCANNER LOGIC 
# =====================================================================
class SecurityVisitor(ast.NodeVisitor):
    def __init__(self, filepath, code_lines):
        self.filepath = filepath
        self.code_lines = code_lines
        self.findings = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec']:
                self.findings.append({
                    "file": self.filepath,
                    "line": node.lineno,
                    "issue": f"High Risk: Dangerous function '{node.func.id}()'",
                    "bad_code": self.code_lines[node.lineno - 1].strip(),
                    "type": "Code Security"
                })
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if any(k in target.id.lower() for k in ['password', 'secret', 'api_key', 'token']):
                    self.findings.append({
                        "file": self.filepath,
                        "line": node.lineno,
                        "issue": f"Medium Risk: Hardcoded secret '{target.id}'",
                        "bad_code": self.code_lines[node.lineno - 1].strip(),
                        "type": "Code Security"
                    })
        self.generic_visit(node)

def remediate_code(issue, bad_code, max_retries=4):
    """
    SMART RETRY LOGIC: Handles Rate Limits smoothly.
    """
    prompt = f"""
    You are an AppSec Engineer. Fix this Python vulnerability.
    Issue: {issue}
    Vulnerable Code: {bad_code}
    Output ONLY valid JSON: {{"secure_code": "code here", "explanation": "why here"}}
    """
    
    for attempt in range(max_retries):
        try:
            # Updated to OpenAI/Groq chat completion format
            response = ai_client.chat.completions.create(
                model='llama-3.3-70b-versatile',
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate limit" in error_msg.lower():
                if attempt < max_retries - 1:
                    match = re.search(r'retry in ([0-9.]+)s', error_msg)
                    if match:
                        wait_time = float(match.group(1)) + 2.0  # Add 2 seconds just to be safe
                    else:
                        wait_time = (attempt + 1) * 15 # Fallback to 15s, 30s, etc.
                        
                    print(f"Rate limited on Code Fix! Retrying in {wait_time:.2f} seconds...")
                    st.toast(f"⏳ API Rate Limit Hit! Pausing for {wait_time:.0f} seconds...", icon="⏳")
                    
                    time.sleep(wait_time)
                    continue 
            
            return {"secure_code": "AI Remediation Failed", "explanation": f"API Error: {error_msg}"}

def analyze_python_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
            lines = code.splitlines()
        
        inspector = SecurityVisitor(filepath, lines)
        inspector.visit(ast.parse(code))
        
        for flaw in inspector.findings:
            fix = remediate_code(flaw["issue"], flaw["bad_code"])
            flaw["ai_fix"] = fix.get("secure_code", "")
            flaw["ai_explanation"] = fix.get("explanation", "")
            
            # Keep a baseline 4-second pause to prevent spamming the API
            time.sleep(4) 
            
        return inspector.findings
    except Exception as e:
        print(f"File analysis error: {e}")
        return []

class EthicsAuditor:
    def __init__(self):
        self.policies = ""
        try:
            with open("compliance_policies.json", 'r', encoding='utf-8') as f:
                for p in json.load(f).get("policies", []):
                    self.policies += f"- [{p['category']}] {p['rule']}\n"
        except:
            pass

    def scan_document(self, filepath, max_retries=4):
        findings = []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                doc = f.read()
            prompt = f"Policies:\n{self.policies}\nDoc:\n{doc}\nOutput JSON list of violations: [{{\"issue\": \"details\"}}]"
            
            for attempt in range(max_retries):
                try:
                    # Updated to OpenAI/Groq chat completion format and changed model to Llama
                    res = ai_client.chat.completions.create(
                        model='llama-3.3-70b-versatile',
                        messages=[{"role": "user", "content": prompt}],
                        # Groq requires the prompt to explicitly ask for JSON when using this mode, 
                        # which you already did above ("Output JSON list")
                        response_format={"type": "json_object"} 
                    )
                    
                    # Groq JSON mode returns an object, so wrap your array request in a root key if it fails, 
                    # but parsing it directly based on standard Llama behavior.
                    parsed_response = json.loads(res.choices[0].message.content)
                    
                    # Handle if the LLM returned a list directly or a dict containing a list
                    violations = parsed_response if isinstance(parsed_response, list) else parsed_response.get("violations", [parsed_response])
                    
                    for v in violations:
                        if isinstance(v, dict) and "issue" in v:
                            findings.append({
                                "file": filepath, "line": "AI Review",
                                "issue": v.get("issue"), "type": "Policy Violation"
                            })
                    break # Success! Break out of the retry loop.
                    
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "rate limit" in error_msg.lower():
                        if attempt < max_retries - 1:
                            match = re.search(r'retry in ([0-9.]+)s', error_msg)
                            wait_time = float(match.group(1)) + 2.0 if match else (attempt + 1) * 15
                            print(f"Rate limited on Document Scan! Retrying in {wait_time:.2f} seconds...")
                            
                            st.toast(f"⏳ API Rate Limit Hit! Pausing for {wait_time:.0f} seconds...", icon="⏳")
                            
                            time.sleep(wait_time)
                            continue
                    break # If it's a different error, stop retrying
                    
        except Exception as e:
            print(f"File read error: {e}")
            
        return findings

def run_enterprise_scan(directory):
    results = []
    auditor = EthicsAuditor()
    ignores = ['.git', '__pycache__', 'venv', 'env', 'node_modules']
    
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in ignores]
        for file in files:
            filepath = os.path.join(root, file)
            if file.endswith('.py') and file not in ["scanner.py", "app.py"]:
                results.extend(analyze_python_file(filepath))
            elif file.endswith(('.md', '.txt')):
                results.extend(auditor.scan_document(filepath))
                time.sleep(4) # Pause after documents too
    return results

# =====================================================================
# 3. FRONTEND UI (The Impressive Dashboard)
# =====================================================================
st.title("🛡️ NexusGuard: Enterprise Security & Ethics Auditor")
st.markdown("Automated Static Analysis and Generative AI Remediation Pipeline.")
st.divider()

target_dir = st.text_input("📁 Enter Repository Path to Scan:", value=".")
scan_button = st.button("🚀 Run Enterprise Scan", type="primary")

if scan_button:
    with st.spinner("Analyzing Codebase & Auditing Documents (This may take a few minutes if API rate limits are hit)..."):
        time.sleep(1) 
        all_results = run_enterprise_scan(target_dir)
        
    st.success("✅ Scan Complete!")
    
    security_flaws = [r for r in all_results if r["type"] == "Code Security"]
    policy_flaws = [r for r in all_results if r["type"] == "Policy Violation"]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Files Scanned", "Complete")
    col2.metric("Technical Vulnerabilities", len(security_flaws), delta="-Action Required", delta_color="inverse")
    col3.metric("Ethics/Policy Violations", len(policy_flaws), delta="-Action Required", delta_color="inverse")
    
    st.divider()

    tab1, tab2 = st.tabs(["🛡️ Technical Security Flaws", "📜 Policy & Ethics Violations"])

    with tab1:
        if not security_flaws:
            st.info("No technical vulnerabilities found! Code is clean.")
        
        for idx, flaw in enumerate(security_flaws):
            with st.expander(f"🚨 {flaw['file']} (Line {flaw['line']}) - {flaw['issue']}", expanded=True):
                code_col1, code_col2 = st.columns(2)
                
                with code_col1:
                    st.error("❌ Vulnerable Code")
                    st.code(flaw['bad_code'], language='python')
                    
                with code_col2:
                    st.success("✅ AI Secure Patch")
                    st.code(flaw['ai_fix'], language='python')
                
                st.info(f"💡 **AI Remediation Rationale:** {flaw['ai_explanation']}")

    with tab2:
        if not policy_flaws:
            st.info("No policy violations found! Documentation is compliant.")
            
        for flaw in policy_flaws:
            st.warning(f"📄 **Document:** `{flaw['file']}`\n\n**Violation found:** {flaw['issue']}")