import os
import ast
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv() 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERROR: Could not find GEMINI_API_KEY. Please make sure you have a .env file!")
    exit(1)

# Initialize the global Gemini Client
ai_client = genai.Client(api_key=GEMINI_API_KEY)

# =====================================================================
# PART 1: THE AST ANALYSIS ENGINE & AUTO-REMEDIATION (Phase 3)
# =====================================================================
class SecurityVisitor(ast.NodeVisitor):
    def __init__(self, filepath, code_lines):
        self.filepath = filepath
        self.code_lines = code_lines # We need the actual lines of code to send to the AI
        self.findings = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            function_name = node.func.id
            if function_name in ['eval', 'exec']:
                # Extract the exact line of bad code
                bad_code = self.code_lines[node.lineno - 1].strip()
                self.findings.append({
                    "file": self.filepath,
                    "line": node.lineno,
                    "issue": f"High Risk: Dangerous function '{function_name}()' allows arbitrary code execution.",
                    "bad_code": bad_code
                })
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                variable_name = target.id.lower()
                risky_keywords = ['password', 'secret', 'api_key', 'token']
                if any(keyword in variable_name for keyword in risky_keywords):
                    bad_code = self.code_lines[node.lineno - 1].strip()
                    self.findings.append({
                        "file": self.filepath,
                        "line": node.lineno,
                        "issue": f"Medium Risk: Potential hardcoded secret in variable named '{target.id}'.",
                        "bad_code": bad_code
                    })
        self.generic_visit(node)

def remediate_code(issue_description, bad_code):
    """
    NEW: This function asks Gemini to fix the vulnerable code.
    """
    print(f"  -> Asking AI to fix code: '{bad_code}'")
    
    prompt = f"""
    You are a Senior Application Security Engineer. 
    A static analysis tool found this security vulnerability:
    Issue: {issue_description}
    Vulnerable Code: {bad_code}
    
    Provide a secure, rewritten version of this code. 
    For hardcoded secrets, suggest using environment variables (os.getenv).
    For dangerous functions like eval(), suggest a safe alternative.
    
    Output ONLY a valid JSON object exactly like this:
    {{
      "secure_code": "api_key = os.getenv('API_KEY')",
      "explanation": "Hardcoded secrets should be moved to environment variables to prevent accidental exposure."
    }}
    """
    
    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        return {"secure_code": "AI Fix Failed", "explanation": str(e)}

def analyze_python_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            code_content = file.read()
            code_lines = code_content.splitlines() # Split the file into a list of lines
            
        tree = ast.parse(code_content)
        inspector = SecurityVisitor(filepath, code_lines) # Pass the lines to the inspector
        inspector.visit(tree)
        
        # NEW: For every flaw found, ask the AI to generate a fix
        for flaw in inspector.findings:
            if "bad_code" in flaw:
                fix_data = remediate_code(flaw["issue"], flaw["bad_code"])
                flaw["ai_fix"] = fix_data.get("secure_code")
                flaw["ai_explanation"] = fix_data.get("explanation")
                
        return inspector.findings
        
    except SyntaxError:
        print(f"Skipping {filepath} - It contains invalid Python syntax.")
        return []
    except Exception as e:
        print(f"Could not read {filepath}: {e}")
        return []

# =====================================================================
# PART 2: THE DOCUMENT & ETHICS PARSER 
# =====================================================================
class EthicsAuditor:
    def __init__(self, policy_filepath="compliance_policies.json"):
        self.policies_text = ""
        try:
            with open(policy_filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for p in data.get("policies", []):
                    self.policies_text += f"- [{p['category']}] {p['rule']}\n"
        except Exception:
            pass

    def scan_document(self, filepath):
        findings = []
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                document_content = file.read()
                
            print(f"Asking AI to review document: {filepath}...")
            prompt = f"""
            You are an strict Enterprise Risk and Ethics Auditor.
            Company policies:
            {self.policies_text}
            
            Document Content:
            {document_content}
            
            Output ONLY a JSON list of violations. Example: [{{"issue": "description"}}]
            """
            
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            for v in json.loads(response.text):
                findings.append({
                    "file": filepath,
                    "line": "AI Review",
                    "issue": v.get("issue", "Unknown compliance risk")
                })
        except Exception:
            pass
        return findings

# =====================================================================
# PART 3: THE ROUTER & CRAWLER (The Folder Explorer)
# =====================================================================
def scan_directory(directory_path):
    all_vulnerabilities = []
    auditor = EthicsAuditor() 
    ignore_folders = ['.git', '__pycache__', 'venv', 'env', 'node_modules']

    print(f"\n--- Starting AI Security Scan in: {directory_path} ---\n")

    for root_folder, folders, files in os.walk(directory_path):
        folders[:] = [f for f in folders if f not in ignore_folders]

        for file in files:
            filepath = os.path.join(root_folder, file)
            if file.endswith('.py') and file != "scanner.py":
                print(f"Scanning Code: {filepath}")
                all_vulnerabilities.extend(analyze_python_file(filepath))
            elif file.endswith(('.md', '.txt')):
                all_vulnerabilities.extend(auditor.scan_document(filepath))

    return all_vulnerabilities



# =====================================================================
# PART 4: RUNNING THE SCRIPT
# =====================================================================
if __name__ == "__main__":
    results = scan_directory(".")
    
    print("\n" + "="*70)
    print("                ENTERPRISE AUDIT REPORT")
    print("="*70)
    
    if len(results) == 0:
        print("[OK] All systems secure. No vulnerabilities found!")
    else:
        print(f"[ALERT] Found {len(results)} issues requiring attention:\n")
        for flaw in results:
            print(f"[FILE]   {flaw['file']} (Line: {flaw['line']})")
            print(f"[ISSUE]  {flaw['issue']}")
            
            # Print the AI Fix if it exists
            if "ai_fix" in flaw:
                print(f"[BAD]    {flaw['bad_code']}")
                print(f"[FIX]    {flaw['ai_fix']}")
                print(f"[WHY]    {flaw['ai_explanation']}")
                
            print("-" * 70)