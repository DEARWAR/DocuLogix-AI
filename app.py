import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import csv
import re
import json
from io import BytesIO, StringIO
import fitz
from PIL import Image
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

st.set_page_config(page_title="DocuLogix AI", page_icon="💠", layout="wide", initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    #MainMenu {visibility:hidden;} footer {visibility:hidden;} header {visibility:hidden;}
    .stDeployButton {display:none;} div[data-testid="stToolbar"] {display:none;}
    * { font-family:'Inter',sans-serif; box-sizing:border-box; }
    .stApp { background-color:#0d1117; }
    .block-container { padding-top:24px !important; padding-left:28px !important; padding-right:28px !important; padding-bottom:12px !important; max-width:100% !important; }

    [data-testid="stSidebar"] { background-color:#161b27 !important; border-right:1px solid #21293a !important; min-width:240px !important; max-width:240px !important; }
    [data-testid="stSidebar"] > div:first-child { padding:0 !important; }
    [data-testid="stSidebar"] .stRadio { display:none !important; }

    .sidebar-logo { display:flex; align-items:center; gap:10px; padding:22px 20px 18px 20px; border-bottom:1px solid #21293a; margin-bottom:10px; }
    .sidebar-logo-icon { width:32px; height:32px; background:linear-gradient(135deg,#3b82f6,#8b5cf6); border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:16px; }
    .sidebar-logo-text { font-size:17px; font-weight:700; color:#fff; letter-spacing:-0.3px; }
    .sidebar-logo-text span { color:#3b82f6; }
    .nav-section { padding:0 12px; }
    .nav-label { font-size:10px; font-weight:600; color:#4b5563; letter-spacing:0.08em; text-transform:uppercase; padding:14px 8px 6px 8px; }
    .nav-item { display:flex; align-items:center; gap:10px; padding:10px 12px; border-radius:8px; font-size:14px; font-weight:500; color:#8b9ab4; cursor:pointer; transition:all 0.15s; margin-bottom:2px; }
    .nav-item:hover { background:#1e2840; color:#fff; }
    .nav-item.active { background:#1e3a5f; color:#3b82f6; }
    .nav-item .nav-icon { font-size:16px; width:20px; text-align:center; }
    .sidebar-profile { position:absolute; bottom:0; left:0; right:0; padding:14px 16px; border-top:1px solid #21293a; background:#161b27; display:flex; align-items:center; gap:10px; }
    .profile-avatar { width:34px; height:34px; border-radius:50%; background:linear-gradient(135deg,#6366f1,#8b5cf6); display:flex; align-items:center; justify-content:center; font-weight:700; font-size:13px; color:white; flex-shrink:0; }
    .profile-info { flex:1; min-width:0; }
    .profile-name { font-size:13px; font-weight:600; color:#fff; }
    .profile-email { font-size:11px; color:#6b7a94; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .profile-chevron { color:#6b7a94; font-size:12px; }

    .page-header { margin-bottom:20px; }
    .page-title { font-size:26px; font-weight:700; color:#f0f4ff; margin-bottom:4px; letter-spacing:-0.4px; }
    .page-subtitle { font-size:13.5px; color:#6b7a94; }

    [data-testid="column"] { background:transparent !important; border:none !important; padding:0 !important; box-shadow:none !important; }
    .card { background:#161b27; border:1px solid #21293a; border-radius:14px; padding:20px 20px 16px 20px; }
    .card-title { font-size:15px; font-weight:600; color:#e8edf5; display:flex; align-items:center; gap:8px; margin-bottom:14px; }

    div[data-testid="stFileUploader"] { background:#0d1117 !important; border:1.5px dashed #2c3d5a !important; border-radius:10px !important; }
    div[data-testid="stFileUploader"] > div { background:transparent !important; }
    div[data-testid="stFileUploader"] label { color:#8b9ab4 !important; }
    div[data-testid="stFileUploader"] button { background:#1e3a5f !important; color:#3b82f6 !important; border:1px solid #2563eb !important; }

    .file-item { display:flex; align-items:center; gap:12px; padding:11px 14px; border-radius:9px; background:#0d1117; border:1px solid #21293a; margin-bottom:8px; }
    .file-icon-box { width:34px; height:34px; border-radius:7px; display:flex; align-items:center; justify-content:center; font-size:13px; font-weight:700; flex-shrink:0; background:#7f1d1d; color:#fca5a5; }
    .file-details { flex:1; min-width:0; }
    .file-name { font-size:13px; font-weight:500; color:#d1d9e6; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .file-size { font-size:11px; color:#4b5e78; margin-top:2px; }
    .file-check { color:#22c55e; font-size:18px; flex-shrink:0; }
    .success-banner { display:flex; align-items:center; gap:10px; padding:11px 14px; border-radius:9px; background:rgba(34,197,94,0.08); border:1px solid rgba(34,197,94,0.25); color:#4ade80; font-size:13px; font-weight:500; margin:10px 0; }
    .process-btn { width:100%; padding:12px; background:linear-gradient(135deg,#2563eb,#3b82f6); color:white; border:none; border-radius:9px; font-size:14px; font-weight:600; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:8px; margin-top:12px; transition:opacity 0.2s; }
    .process-btn:hover { opacity:0.9; }

    .chat-welcome { background:#0d1117; border:1px solid #21293a; border-radius:12px; padding:16px 18px; font-size:13.5px; color:#8b9ab4; line-height:1.8; margin-bottom:10px; }
    .chat-welcome ul { margin:6px 0 0 0; padding-left:18px; }
    .chat-welcome li { margin-bottom:2px; }

    [data-testid="stChatMessage"] { background:transparent !important; border:none !important; padding:3px 0 !important; }
    .stChatMessage [data-testid="stChatMessageContent"] { background:#0d1117 !important; border:1px solid #21293a !important; color:#c9d4e8 !important; border-radius:4px 14px 14px 14px !important; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] { background:linear-gradient(135deg,#2563eb,#3b82f6) !important; color:white !important; border:none !important; border-radius:14px 14px 4px 14px !important; }

    [data-testid="stChatInput"] { background:#0d1117 !important; border:1px solid #21293a !important; border-radius:10px !important; }
    [data-testid="stChatInput"] textarea { color:#c9d4e8 !important; font-size:13.5px !important; }
    [data-testid="stChatInput"] button { background:#2563eb !important; border-radius:7px !important; }

    [data-testid="baseButton-secondary"] { background:rgba(34,197,94,0.08) !important; border:1px solid rgba(34,197,94,0.3) !important; color:#4ade80 !important; border-radius:8px !important; font-size:13px !important; font-weight:500 !important; width:100% !important; }
    [data-testid="baseButton-secondary"]:hover { background:rgba(34,197,94,0.15) !important; color:#86efac !important; }

    .footer-bar { text-align:center; font-size:12px; color:#3a4a62; padding:12px 0 4px 0; border-top:1px solid #1a2133; margin-top:12px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Parent-level clipboard listener — receives postMessage from iframes and writes to clipboard
st.markdown("""
<script>
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'streamlit-copy') {
        var text = event.data.text;
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).catch(function() {});
        } else {
            var ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            document.body.appendChild(ta);
            ta.focus(); ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
        }
    }
});
</script>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# LLM + SESSION
# ══════════════════════════════════════════════════════
# CLOUD SECURITY: Force system to read Streamlit Secrets
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest", temperature=0)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_images" not in st.session_state:
    st.session_state.pdf_images = []
# YAHAN ADD KIYA HAI CURRENT PAGE KI MEMORY 👇
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

def get_base64_image(img):
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# ══════════════════════════════════════════════════════
# SMART INTENT DETECTION
# ══════════════════════════════════════════════════════
def detect_intent(query: str) -> str:
    """
    Returns intent tag to guide how we extract copyable data.
    Tags: container_numbers | weights | bl_number | shipper_consignee |
          shipper_only | consignee_only | notify_party | generic
    """
    q = query.lower()
    if any(w in q for w in ['container number', 'container no', 'cntr', 'container id']):
        return 'container_numbers'
    if any(w in q for w in ['weight', 'gross weight', 'net weight', 'kg', 'kgs', 'mt ', 'metric ton']):
        return 'weights'
    if any(w in q for w in ['bl number', 'b/l number', 'bl no', 'bill of lading number', 'lading no']):
        return 'bl_number'
    if any(w in q for w in ['notify party', 'notify']):
        return 'notify_party'
    if ('shipper' in q and 'consignee' in q) or ('shipper' in q and 'consign' in q):
        return 'shipper_consignee'
    if 'shipper' in q:
        return 'shipper_only'
    if 'consignee' in q:
        return 'consignee_only'
    return 'generic'


def strip_ai_preamble(text: str) -> str:
    """Remove common AI introductory phrases from the start of a response."""
    patterns = [
        r'^based on .*?[:\n]',
        r'^according to .*?[:\n]',
        r'^here are .*?[:\n]',
        r'^here is .*?[:\n]',
        r'^the following .*?[:\n]',
        r'^below .*?[:\n]',
        r'^from the .*?[:\n]',
        r'^as per .*?[:\n]',
        r'^the extracted .*?[:\n]',
        r'^i found .*?[:\n]',
        r'^sure[,!]? .*?[:\n]',
    ]
    result = text.strip()
    for pat in patterns:
        result = re.sub(pat, '', result, flags=re.IGNORECASE | re.DOTALL).strip()
    return result


def extract_bullet_values(text: str) -> list:
    """Extract all bullet point values from text as a clean list."""
    lines = text.split('\n')
    values = []
    for line in lines:
        line = line.strip()
        # Remove bullet/dash/asterisk prefix
        line = re.sub(r'^[\*\-•◦▪▸]+\s*', '', line).strip()
        # Remove bold markers
        line = re.sub(r'\*\*(.+?)\*\*', r'\1', line).strip()
        if line and not line.endswith(':'):
            values.append(line)
    return values


def extract_copyable_data(raw_response: str, intent: str):
    """
    Returns either:
      - A single string (copyable text) for most intents
      - A list of dicts [{'label': ..., 'copy_text': ..., 'display_html': ...}] for multi-section intents
    """
    clean = strip_ai_preamble(raw_response)

    if intent == 'container_numbers':
        # Find all container numbers: exactly 4 letters + 7 digits
        containers = re.findall(r'\b[A-Z]{4}\d{7}\b', raw_response.upper())
        if containers:
            return '\n'.join(containers)
        # fallback: bullet values
        vals = extract_bullet_values(clean)
        return '\n'.join(vals)

    elif intent == 'weights':
        # Extract weight values: numbers with KGS / MT / LBS / TON
        weights = re.findall(
            r'[\d,]+(?:\.\d+)?\s*(?:KGS?|MT|LBS?|TONS?|METRIC TONS?)',
            raw_response.upper()
        )
        if weights:
            return '\n'.join(w.strip() for w in weights)
        # fallback: lines that contain digits with units
        lines = [l.strip() for l in raw_response.split('\n') if re.search(r'\d', l) and re.search(r'(kg|mt|lb|ton)', l, re.I)]
        if lines:
            cleaned = []
            for l in lines:
                l = re.sub(r'^[\*\-•◦]+\s*', '', l)
                l = re.sub(r'\*\*(.+?)\*\*', r'\1', l)
                # Remove container number prefix if present (e.g. "Container CMAU0420918: ")
                l = re.sub(r'^container\s+[A-Z0-9]+[:\s]+', '', l, flags=re.I)
                cleaned.append(l.strip())
            return '\n'.join(cleaned)
        return '\n'.join(extract_bullet_values(clean))

    elif intent == 'bl_number':
        # Try to find BL number patterns
        bl = re.findall(r'(?:BL|B/L|BILL)[:\s#]*([A-Z0-9\-\/]+)', raw_response.upper())
        if bl:
            return '\n'.join(bl)
        vals = extract_bullet_values(clean)
        return '\n'.join(vals)

    elif intent == 'notify_party':
        vals = extract_bullet_values(clean)
        return '\n'.join(vals)

    elif intent in ('shipper_consignee', 'shipper_only', 'consignee_only'):
        # Split into sections by heading keywords
        sections = []

        def extract_section(text, keyword):
            """Extract name + address block after a keyword heading."""
            pattern = rf'(?:^|\n)\**{keyword}\**[:\s]*\n?(.*?)(?=\n\**(?:shipper|consignee|notify|$))'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                block = match.group(1).strip()
                lines = []
                for l in block.split('\n'):
                    l = re.sub(r'^[\*\-•◦]+\s*', '', l.strip())
                    l = re.sub(r'\*\*(.+?)\*\*', r'\1', l)
                    l = re.sub(r'^(?:name|address)\s*:\s*', '', l, flags=re.I)
                    l = l.strip()
                    if l:
                        lines.append(l)
                return '\n'.join(lines)
            return None

        shipper_text = extract_section(raw_response, 'shipper')
        consignee_text = extract_section(raw_response, 'consignee')

        if intent == 'shipper_only':
            if shipper_text:
                return [{'label': 'Shipper', 'copy_text': shipper_text}]
            return shipper_text or '\n'.join(extract_bullet_values(clean))

        if intent == 'consignee_only':
            if consignee_text:
                return [{'label': 'Consignee', 'copy_text': consignee_text}]
            return consignee_text or '\n'.join(extract_bullet_values(clean))

        # Both
        result = []
        if shipper_text:
            result.append({'label': 'Shipper', 'copy_text': shipper_text})
        if consignee_text:
            result.append({'label': 'Consignee', 'copy_text': consignee_text})
        if result:
            return result
        return '\n'.join(extract_bullet_values(clean))

    else:
        # generic: return full response minus preamble
        return clean


# ══════════════════════════════════════════════════════
# RENDER HELPERS
# ══════════════════════════════════════════════════════
def markdown_to_html(text: str) -> str:
    import html as hl
    lines = text.split('\n')
    parts = []
    in_ul = False
    for line in lines:
        raw = line.rstrip()
        stripped = raw.lstrip()
        indent = len(raw) - len(stripped)
        is_bullet = bool(re.match(r'^[\*\-•◦▪]+\s+', stripped))
        if is_bullet:
            item = re.sub(r'^[\*\-•◦▪]+\s+', '', stripped)
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', hl.escape(item))
            if not in_ul:
                parts.append('<ul style="margin:6px 0;padding-left:18px;">')
                in_ul = True
            parts.append(f'<li style="color:#c9d4e8;margin-bottom:4px;">{item}</li>')
        else:
            if in_ul:
                parts.append('</ul>')
                in_ul = False
            if stripped:
                h = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', hl.escape(stripped))
                parts.append(f'<p style="margin:3px 0;color:#c9d4e8;">{h}</p>')
    if in_ul:
        parts.append('</ul>')
    return '\n'.join(parts)


def copy_button_component(copy_text: str, label: str = "📋 Copy", height: int = 44) -> None:
    """Render a standalone copy button via components.html."""
    encoded = json.dumps(copy_text)
    components.html(f"""
    <style>
        body{{margin:0;padding:0;background:transparent;font-family:'Inter',sans-serif;}}
        .cbtn{{display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:7px;
               background:#1e293b;border:1px solid #2c3d5a;color:#8b9ab4;font-size:12.5px;
               cursor:pointer;transition:all 0.15s;font-family:'Inter',sans-serif;}}
        .cbtn:hover{{background:#243447;color:#c9d4e8;border-color:#3a5070;}}
        .cbtn.done{{background:rgba(34,197,94,0.12);border-color:rgba(34,197,94,0.3);color:#4ade80;}}
    </style>
    <button class="cbtn" id="b" onclick="copyToClipboard()">{label}</button>
    <script>
    var copyData = {encoded};
    function copyToClipboard() {{
        var btn = document.getElementById('b');
        function onSuccess() {{
            btn.textContent = '✅ Copied!';
            btn.classList.add('done');
            setTimeout(function() {{ btn.innerHTML = '{label}'; btn.classList.remove('done'); }}, 2000);
        }}
        // Method 1: Try textarea execCommand (works in iframes)
        try {{
            var ta = document.createElement('textarea');
            ta.value = copyData;
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            ta.style.top = '-9999px';
            document.body.appendChild(ta);
            ta.focus();
            ta.select();
            ta.setSelectionRange(0, ta.value.length);
            var ok = document.execCommand('copy');
            document.body.removeChild(ta);
            if (ok) {{ onSuccess(); return; }}
        }} catch(e) {{}}
        // Method 2: postMessage to parent for clipboard write
        window.parent.postMessage({{type: 'streamlit-copy', text: copyData}}, '*');
        onSuccess();
    }}
    </script>
    """, height=height, scrolling=False)


def render_section_card(label: str, copy_text: str, display_html: str = None) -> None:
    """Render a labeled card with its own copy button."""
    if display_html is None:
        lines = copy_text.strip().split('\n')
        display_html = ''.join(f'<p style="margin:2px 0;color:#c9d4e8;font-size:13.5px;">{l}</p>' for l in lines if l.strip())

    encoded = json.dumps(copy_text)
    safe_id = re.sub(r'[^a-zA-Z0-9]', '_', label)
    components.html(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body{{margin:0;padding:0;background:transparent;font-family:'Inter',sans-serif;}}
        .card{{background:#0d1117;border:1px solid #21293a;border-radius:10px;padding:14px 16px;margin-bottom:10px;}}
        .card-label{{font-size:11px;font-weight:600;color:#3b82f6;text-transform:uppercase;
                     letter-spacing:0.06em;margin-bottom:8px;}}
        .card-body{{font-size:13.5px;color:#c9d4e8;line-height:1.7;margin-bottom:10px;}}
        .card-body strong{{color:#e8edf5;}}
        .cbtn{{display:inline-flex;align-items:center;gap:5px;padding:5px 12px;border-radius:6px;
               background:#1e293b;border:1px solid #2c3d5a;color:#8b9ab4;font-size:12px;
               cursor:pointer;transition:all 0.15s;font-family:'Inter',sans-serif;}}
        .cbtn:hover{{background:#243447;color:#c9d4e8;}}
        .cbtn.done{{background:rgba(34,197,94,0.12);border-color:rgba(34,197,94,0.3);color:#4ade80;}}
    </style>
    <div class="card">
        <div class="card-label">📌 {label}</div>
        <div class="card-body">{display_html}</div>
        <button class="cbtn" id="btn_{safe_id}" onclick="copyCard_{safe_id}()">📋 Copy {label}</button>
    </div>
    <script>
    var copyData_{safe_id} = {encoded};
    function copyCard_{safe_id}() {{
        var btn = document.getElementById('btn_{safe_id}');
        function onSuccess() {{
            btn.textContent = '✅ Copied!';
            btn.classList.add('done');
            setTimeout(function() {{ btn.innerHTML = '📋 Copy {label}'; btn.classList.remove('done'); }}, 2000);
        }}
        try {{
            var ta = document.createElement('textarea');
            ta.value = copyData_{safe_id};
            ta.style.position = 'fixed';
            ta.style.left = '-9999px';
            ta.style.top = '-9999px';
            document.body.appendChild(ta);
            ta.focus();
            ta.select();
            ta.setSelectionRange(0, ta.value.length);
            var ok = document.execCommand('copy');
            document.body.removeChild(ta);
            if (ok) {{ onSuccess(); return; }}
        }} catch(e) {{}}
        window.parent.postMessage({{type: 'streamlit-copy', text: copyData_{safe_id}}}, '*');
        onSuccess();
    }}
    </script>
    """, height=int(len(copy_text.split('\n')) * 26 + 100), scrolling=False)


def render_ai_response(raw_response: str, intent: str, msg_key: str) -> None:
    """Main render function — shows full AI response + smart copyable section(s)."""
    copyable = extract_copyable_data(raw_response, intent)

    # 1. Show the full formatted AI response for context
    full_html = markdown_to_html(raw_response)
    line_count = raw_response.count('\n') + 1
    est_height = max(60, line_count * 22 + 50)

    encoded_full = json.dumps(raw_response)
    components.html(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body{{margin:0;padding:0;background:transparent;font-family:'Inter',sans-serif;}}
        .rb{{font-size:13.5px;color:#c9d4e8;line-height:1.7;}}
        .rb strong{{color:#e8edf5;}} .rb ul{{padding-left:18px;margin:6px 0;}} .rb li{{margin-bottom:4px;}}
        .rb p{{margin:3px 0;}}
    </style>
    <div class="rb">{full_html}</div>
    """, height=est_height, scrolling=False)

    # 2. Show copyable section(s)
    if isinstance(copyable, list):
        # Multiple section cards (shipper/consignee)
        for section in copyable:
            lines = section['copy_text'].strip().split('\n')
            disp_html = ''.join(
                f'<p style="margin:2px 0;color:#c9d4e8;font-size:13.5px;">{l}</p>'
                for l in lines if l.strip()
            )
            render_section_card(section['label'], section['copy_text'], disp_html)
    else:
        # Single copyable block
        if copyable and copyable.strip():
            lines = copyable.strip().split('\n')
            disp_html = ''.join(
                f'<p style="margin:2px 0;color:#c9d4e8;font-size:13.5px;font-family:monospace;">{l}</p>'
                for l in lines if l.strip()
            )
            render_section_card("Extracted Data", copyable, disp_html)


# ══════════════════════════════════════════════════════
# CSV EXPORT
# ══════════════════════════════════════════════════════
def generate_csv(messages):
    output = StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    writer.writerow(["#", "Role", "Message"])
    for i, msg in enumerate(messages, 1):
        role = "User" if msg["role"] == "user" else "Assistant (AI)"
        clean = re.sub(r'\*\*(.+?)\*\*', r'\1', msg["content"])
        clean = re.sub(r'\*(.+?)\*', r'\1', clean)
        clean = re.sub(r'^[\s]*[\*\-•]+\s*', '', clean, flags=re.MULTILINE)
        writer.writerow([i, role, clean.strip()])
    return output.getvalue().encode("utf-8-sig")


# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-icon">💠</div>
        <div class="sidebar-logo-text">DocuLogix <span>AI</span></div>
    </div>
    <div class="nav-section">
        <div class="nav-item active"><span class="nav-icon">🏠</span> Dashboard</div>
        <div class="nav-item"><span class="nav-icon">📄</span> Documents</div>
        <div class="nav-item"><span class="nav-icon">💬</span> Chat History</div>
        <div class="nav-label">SETTINGS</div>
        <div class="nav-item"><span class="nav-icon">👤</span> Profile</div>
        <div class="nav-item"><span class="nav-icon">⚙️</span> Settings</div>
    </div>
    <div class="sidebar-profile">
        <div class="profile-avatar">A</div>
        <div class="profile-info">
            <div class="profile-name">Admin User</div>
            <div class="profile-email">admin@example.com</div>
        </div>
        <div class="profile-chevron">⌄</div>
    </div>
    """, unsafe_allow_html=True)

    # Terms & Conditions button
    st.markdown("<div style='height:60px;'></div>", unsafe_allow_html=True)
    if st.button("📜 Terms & Conditions", key="tnc_btn", use_container_width=True):
        st.session_state["show_tnc"] = not st.session_state.get("show_tnc", False)

# ══════════════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════════════
if st.session_state.current_page == "Dashboard":
    title = "Welcome back, Admin! 👋"
    subtitle = "Upload documents and ask questions to get AI-powered insights."
else:
    title = st.session_state.current_page
    subtitle = f"Manage your {st.session_state.current_page.lower()} settings and preferences here."

st.markdown(f"""
<div class="page-header">
    <div class="page-title">{title}</div>
    <div class="page-subtitle">{subtitle}</div>
</div>
""", unsafe_allow_html=True)

def close_tnc():
    st.session_state["show_tnc"] = False

if st.session_state.get("show_tnc", False):
    st.markdown("""
    <div style="background:#161b27;border:1px solid #21293a;border-radius:12px;padding:26px 32px;font-size:14px;color:#c9d4e8;line-height:1.7;margin-bottom:24px;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
        <div style="font-size:20px;font-weight:700;color:#3b82f6;margin-bottom:8px;">📄 DOCULOGIX AI: USER MANUAL & TERMS OF SERVICE</div>
        <div style="color:#8b9ab4;font-size:12.5px;margin-bottom:20px;padding-bottom:14px;border-bottom:1px solid #21293a;">
            <strong>Effective Date:</strong> May 2026<br/>
            <strong>Created and Developed By:</strong> Manish Dearwar
        </div>
        <p>Welcome to DocuLogix AI. This document serves as the official guide and legal agreement for using our proprietary artificial intelligence tool designed for the logistics and freight forwarding industry.</p>
        <h4 style="color:#f0f4ff;font-size:16px;margin-top:24px;margin-bottom:12px;">PART I: COMPREHENSIVE USER GUIDE (HOW TO USE)</h4>
        <p>DocuLogix AI is engineered to simplify complex freight operations. Follow these steps to maximize your productivity:</p>
        <p><strong>Step 1: Document Ingestion (Upload)</strong><br/>
        • <strong>Action:</strong> Navigate to the "Document Upload" panel on the left side of your dashboard.<br/>
        • <strong>Process:</strong> Drag and drop your shipping document (PDF format)—such as a Bill of Lading, Commercial Invoice, or Packing List.<br/>
        • <strong>System Response:</strong> The application uses High-Definition Vision AI to scan and digitize the document, regardless of whether it is an original digital PDF or a scanned copy. Wait for the green success banner confirming the document is ready.</p>
        <p><strong>Step 2: Intelligent Querying (Chat)</strong><br/>
        • <strong>Action:</strong> Move to the "AI Chat Assistant" panel on the right.<br/>
        • <strong>Process:</strong> Type your request in natural language. You do not need to use complex commands.<br/>
        • <strong>Example 1:</strong> "Extract the Shipper, Consignee, and Notify Party details."<br/>
        • <strong>Example 2:</strong> "List all Container Numbers, Seal Numbers, and their respective Gross Weights."<br/>
        • <strong>System Response:</strong> The AI will instantly read the complex tables, boxes, and watermarks to provide highly accurate, formatted answers.</p>
        <p><strong>Step 3: Data Export & Integration (Download)</strong><br/>
        • <strong>Action:</strong> Once you have extracted all necessary information via chat, look at the bottom of the left navigation sidebar.<br/>
        • <strong>Process:</strong> Click the "📥 Download CSV" button.<br/>
        • <strong>System Response:</strong> A structured Excel/CSV file containing your entire data extraction session will be downloaded to your local machine, ready to be imported into your ERP, Customs portal, or shared with your team.</p>
        <h4 style="color:#f0f4ff;font-size:16px;margin-top:24px;margin-bottom:12px;">PART II: CORE BENEFITS & VALUE PROPOSITION</h4>
        <p><strong>⚡ Unprecedented Speed:</strong> Reduce manual data entry time from 15 minutes per shipment to under 10 seconds.<br/>
        <strong>👁️ Advanced Optical Vision (OCR 2.0):</strong> Powered by state-of-the-art Multimodal AI, the system reads crumpled, skewed, or watermarked scans with human-like precision, capturing faint digits that traditional OCRs miss.<br/>
        <strong>🧠 Logistics-Optimized Logic:</strong> The AI is hard-coded with global logistics standards (e.g., validating that every Container Number follows the 4-letter, 7-digit ISO standard) to eliminate typos.<br/>
        <strong>📊 Seamless Workflow Integration:</strong> The one-click CSV export ensures that AI-extracted data bridges perfectly with your existing operational software.<br/>
        <strong>🔒 Zero-Retention Privacy:</strong> Your sensitive trade documents are processed in a volatile memory environment and are instantly discarded after your session ends. We do not build databases out of your freight data.</p>
        <h4 style="color:#f0f4ff;font-size:16px;margin-top:24px;margin-bottom:12px;">PART III: TERMS AND CONDITIONS OF USE</h4>
        <p>By accessing, uploading documents to, or otherwise utilizing DocuLogix AI (the "Software"), you agree to be bound by the following terms.</p>
        <p><strong>1. Acceptance of Agreement</strong><br/>
        This is a legally binding agreement between you (the User) and Manish Dearwar (the Creator & Owner). If you do not agree to these terms, you must immediately cease all use of the Software.</p>
        <p><strong>2. Nature of Service and AI Limitations</strong><br/>
        DocuLogix AI utilizes third-party advanced Generative AI and Vision models (Google Gemini) to process and extract text from images. While the technology is highly accurate, Artificial Intelligence is inherently subject to occasional misinterpretations, formatting errors, or "hallucinations."</p>
        <p><strong>3. User Responsibility and Mandatory Verification</strong><br/>
        <strong>Critical Rule:</strong> The Software is an operational assistant, not a replacement for human oversight.<br/>
        <strong>Manual Verification:</strong> Users are strictly required to manually verify all extracted critical data (including but not limited to Container Numbers, Seal Numbers, HS Codes, Weights, and Vessel Names) against the original document before submitting data to Customs Authorities, Port Terminals, Shipping Lines, or internal ERPs.</p>
        <p><strong>4. Limitation of Liability</strong><br/>
        Under no circumstances shall Manish Dearwar, his affiliates, or partners be held liable for any direct, indirect, incidental, financial, or legal damages arising from the use of this Software. This includes, but is not limited to, damages caused by delayed customs clearances, misfiled manifests, container roll-overs, or operational penalties resulting from unchecked AI-generated data.</p>
        <p><strong>5. Data Privacy and Third-Party Processing</strong><br/>
        By utilizing this Software, you consent to the secure transmission of your uploaded documents to our designated AI provider API for the sole purpose of real-time data extraction. The Creator does not claim ownership of your uploaded documents, nor are they permanently stored on our hosting servers.</p>
        <p><strong>6. Intellectual Property Rights</strong><br/>
        The DocuLogix AI application, including its source code, UI/UX design, custom CSS styling, operational logic, and brand identity, is the exclusive intellectual property of Manish Dearwar. Users are granted a limited, non-transferable, and non-exclusive license to use the Software. Reverse engineering, cloning, or unauthorized commercial distribution of the Software is strictly prohibited.</p>
        <h4 style="color:#f0f4ff;font-size:16px;margin-top:24px;margin-bottom:12px;">PART IV: COPYRIGHT AND OWNERSHIP</h4>
        <p><strong>© 2026 Manish Dearwar. All Rights Reserved.</strong><br/>
        No part of this software, its design, or its underlying architecture may be reproduced, distributed, or transmitted in any form or by any means, including photocopying, recording, or other electronic or mechanical methods, without the prior written permission of the copyright owner, Manish Dearwar. Email Me On- Royr13920@gmail.com</p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✕ Close Document", on_click=close_tnc)

if st.session_state.current_page != "Dashboard":
    st.markdown(f"""
    <div style="text-align:center; padding: 80px 20px; color:#8b9ab4; background:#161b27; border:1px solid #21293a; border-radius:12px; margin-top:20px;">
        <div style="font-size:48px; margin-bottom:16px;">🚧</div>
        <h2 style="color:#e8edf5; margin-bottom:8px;">{st.session_state.current_page}</h2>
        <p>This module is currently under development. Stay tuned for updates!</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="footer-bar" style="margin-top:40px;">🔒 Your data is secure and private. Only you can access your documents and conversations.</div>', unsafe_allow_html=True)
    st.stop()

col1, col2 = st.columns([1, 1.15], gap="large")

# ══════════════════════════════════════════════════════
# LEFT CARD — UPLOAD
# ══════════════════════════════════════════════════════
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>📄 Document Upload</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded_file is not None:
        file_size_kb = len(uploaded_file.getvalue()) / 1024
        size_str = f"{file_size_kb/1024:.1f} MB" if file_size_kb >= 1024 else f"{file_size_kb:.0f} KB"

        st.markdown(f"""
        <div class="file-item">
            <div class="file-icon-box">PDF</div>
            <div class="file-details">
                <div class="file-name">{uploaded_file.name}</div>
                <div class="file-size">{size_str}</div>
            </div>
            <div class="file-check">✅</div>
        </div>
        <div class="success-banner">✅ 1 document uploaded successfully!</div>
        """, unsafe_allow_html=True)

        try:
            pdf_bytes = uploaded_file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            base64_images = []
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                base64_images.append(get_base64_image(img))
            st.session_state.pdf_images = base64_images
        except Exception as e:
            st.error(f"Processing error: {e}")

        st.markdown('<button class="process-btn">✨ Process Documents</button>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:12px;color:#4b5e78;text-align:center;padding:6px 0;">Supports PDF · Max 50MB</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# RIGHT CARD — CHAT
# ══════════════════════════════════════════════════════
with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='card-title'>💬 AI Chat Assistant</div>", unsafe_allow_html=True)

    chat_container = st.container(height=520, border=False)

    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div class="chat-welcome">
                Hello! I'm your smart document assistant. Ask me to extract anything from your uploaded documents.
                <ul>
                    <li>Give me container numbers</li>
                    <li>How much per container weight?</li>
                    <li>Give me shipper and consignee details</li>
                    <li>What is the BL number?</li>
                    <li>Give me notify party details</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        for i, msg in enumerate(st.session_state.messages):
            avatar = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"], avatar=avatar):
                if msg["role"] == "assistant":
                    intent = msg.get("intent", "generic")
                    render_ai_response(msg["content"], intent, f"hist_{i}")
                else:
                    st.write(msg["content"])

    user_query = st.chat_input("Ask a question about your documents...")

    if user_query:
        intent = detect_intent(user_query)

        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.write(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})

        with chat_container:
            with st.chat_message("assistant", avatar="🤖"):
                if not st.session_state.pdf_images:
                    st.warning("Please upload a document first.")
                else:
                    system_instruction = """
You are an expert logistics document AI. Extract precise data from shipping document images.

RESPONSE FORMAT RULES (CRITICAL):
1. NEVER start with phrases like "Based on the document", "According to", "Here are", "Here is", "The following", etc.
2. Start DIRECTLY with the data. Example: Instead of "Here are the container numbers: CMAU0420918" just output the structured data.
3. Use bullet points for lists.
4. For shipper/consignee: use clear headings "**Shipper:**" and "**Consignee:**" on their own lines, followed by "* Name: ..." and "* Address: ..." bullets.
5. For container numbers: list each on its own bullet line.
6. For weights: list each as "* Container XXXX: 26,600.000 KGS" format.
7. A valid Container Number = exactly 4 uppercase letters + 7 digits.
8. Do not hallucinate. Only extract what is clearly visible.
                    """
                    content_list = [{"type": "text", "text": f"Question: {user_query}"}]
                    for b64_img in st.session_state.pdf_images:
                        content_list.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                        })
                    messages_llm = [
                        SystemMessage(content=system_instruction),
                        HumanMessage(content=content_list)
                    ]
                    response = llm.invoke(messages_llm)
                    final_answer = response.content[0]["text"] if isinstance(response.content, list) else response.content
                    render_ai_response(final_answer, intent, f"new_{len(st.session_state.messages)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": final_answer,
                        "intent": intent
                    })

    if st.session_state.messages:
        csv_data = generate_csv(st.session_state.messages)
        st.download_button(
            label="📊 Export to CSV — Download Data",
            data=csv_data,
            file_name="doculogix_extracted_data.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div class="footer-bar">
    🔒 Your data is secure and private. Only you can access your documents and conversations.
</div>
""", unsafe_allow_html=True)
