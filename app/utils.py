import os
import json
import requests
import yaml
import streamlit as st

ARF_URL = "https://github.com/lockfale/OSINT-Framework/raw/refs/heads/master/public/arf.json"
CACHE_DIR = "config"
ARF_PATH = os.path.join(CACHE_DIR, "arf.json")
TOOLS_YAML_PATH = os.path.join(CACHE_DIR, "tools.yaml")

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["username"] == "admin" and st.session_state["password"] == "osint":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

def fetch_and_cache_arf():
    """Fetches arf.json if not present locally."""
    if not os.path.exists(ARF_PATH):
        try:
            response = requests.get(ARF_URL)
            response.raise_for_status()
            with open(ARF_PATH, 'w', encoding='utf-8') as f:
                f.write(response.text)
        except Exception as e:
            st.error(f"Failed to fetch ARF data: {e}")

def generate_tools_yaml():
    """Parses arf.json and generates tools.yaml based on rules."""
    if os.path.exists(TOOLS_YAML_PATH):
        return

    fetch_and_cache_arf()
    if not os.path.exists(ARF_PATH):
        return

    with open(ARF_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    tools = {}
    categories = {
        "username": ["username"],
        "email": ["email"],
        "domain/ip": ["domain", "ip"],
        "image": ["image"],
        "geolocation": ["location", "geo"],
        "phone": ["phone"],
        "social": ["social"],
        "breaches": ["breach", "leak"]
    }

    # Recursive function to extract tools from nested ARF structure
    def extract_tools(node):
        found_tools = []
        if isinstance(node, dict):
            if node.get('type') == 'url' and node.get('pricing') == 'free' and node.get('status') == 'live' and not node.get('localInstall'):
                found_tools.append(node)
            elif 'children' in node:
                found_tools.extend(extract_tools(node['children']))
        elif isinstance(node, list):
            for item in node:
                found_tools.extend(extract_tools(item))
        return found_tools

    raw_tools = extract_tools(data)

    for cat, keywords in categories.items():
        tools[cat] = []
        for t in raw_tools:
            best_for = t.get('bestFor', '').lower()
            if any(kw in best_for for kw in keywords):
                # Check for duplicates
                if not any(existing.get('url') == t.get('url') for existing in tools[cat]):
                    tools[cat].append({
                        "name": t.get('name'),
                        "url": t.get('url'),
                        "description": t.get('description')
                    })

    with open(TOOLS_YAML_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(tools, f, default_flow_style=False)

def get_tools_config():
    """Loads and returns the generated tools.yaml."""
    generate_tools_yaml()
    if os.path.exists(TOOLS_YAML_PATH):
        with open(TOOLS_YAML_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}
