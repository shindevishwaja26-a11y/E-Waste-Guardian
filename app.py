import streamlit as st
import sqlite3
from datetime import datetime

DB = 'ewaste_guardian.db'

st.set_page_config(page_title='E-Waste Guardian', page_icon='♻️', layout='centered')

# ---------- Database ----------
def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device TEXT, age INTEGER, working TEXT, condition TEXT,
        issue TEXT, recommendation TEXT, created_at TEXT
    )''')
    con.commit()
    con.close()


def save_check(data):
    con = sqlite3.connect(DB)
    con.execute('''INSERT INTO checks
        (device, age, working, condition, issue, recommendation, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
    con.commit()
    con.close()


def get_stats():
    con = sqlite3.connect(DB)
    total = con.execute('SELECT COUNT(*) FROM checks').fetchone()[0]
    sell = con.execute("SELECT COUNT(*) FROM checks WHERE recommendation='Sell / Exchange'").fetchone()[0]
    repair = con.execute("SELECT COUNT(*) FROM checks WHERE recommendation='Repair / Reuse'").fetchone()[0]
    recycle = con.execute("SELECT COUNT(*) FROM checks WHERE recommendation='Recycle'").fetchone()[0]
    con.close()
    return total, sell, repair, recycle


init_db()

# ---------- Styling ----------
st.markdown('''
<style>
.stApp { background: linear-gradient(180deg,#f4fff8 0%,#ffffff 55%,#f0faf5 100%); }
.block-container { max-width: 900px; padding-top: 2rem; }
.hero { padding: 28px; border-radius: 24px; background: linear-gradient(135deg,#0f7b55,#21a66f); color:white; margin-bottom:20px; box-shadow:0 10px 30px rgba(15,123,85,.18); }
.hero h1 { margin:0; font-size:2.4rem; }
.hero p { font-size:1.05rem; opacity:.95; }
.card { background:white; border:1px solid #dceee4; border-radius:18px; padding:20px; margin:12px 0; box-shadow:0 5px 18px rgba(20,70,45,.06); }
.result { background:#ecfff4; border:2px solid #27a96f; border-radius:18px; padding:22px; margin-top:18px; }
.small { color:#557266; font-size:.92rem; }
</style>
''', unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.title('♻️ E-Waste Guardian')
page = st.sidebar.radio('Navigate', ['Home', 'Check My Device', 'Impact Dashboard', 'E-Waste Guide'])
st.sidebar.caption('Python-only prototype using Streamlit + SQLite')

# ---------- Home ----------
if page == 'Home':
    st.markdown('''<div class="hero"><h1>♻️ E-Waste Guardian</h1>
    <p>Find the right next step for your old electronic device — sell, repair, reuse or recycle.</p></div>''', unsafe_allow_html=True)

    st.markdown('### Why this matters')
    st.markdown('''<div class="card"><b>Old electronics should not automatically become waste.</b><br><br>
    A device may still have resale value, may be repairable, or may need responsible recycling.
    E-Waste Guardian uses simple device information to recommend a practical next step.</div>''', unsafe_allow_html=True)

    cols = st.columns(3)
    for col, title, text in zip(cols,
        ['💰 Sell / Exchange','🔧 Repair / Reuse','♻️ Recycle'],
        ['For working devices with useful value.','For devices that can reasonably be repaired or reused.','For damaged or unsuitable devices that should enter responsible recycling.']):
        with col:
            st.markdown(f'<div class="card"><h4>{title}</h4><p class="small">{text}</p></div>', unsafe_allow_html=True)

    st.info('Start with “Check My Device” to get a recommendation.')

# ---------- Device checker ----------
elif page == 'Check My Device':
    st.title('🔍 Check My Device')
    st.write('Enter a few details and the Python decision engine will suggest what to do next.')

    with st.form('device_form'):
        device = st.selectbox('Device type', ['Smartphone','Laptop','Tablet','Smartwatch','Earbuds / Headphones','Printer','Camera','Charger / Adapter','Other'])
        age = st.slider('Device age (years)', 0, 15, 3)
        working = st.radio('Is the device currently working?', ['Yes','Partially','No'], horizontal=True)
        condition = st.select_slider('Physical condition', options=['Poor','Average','Good','Excellent'], value='Good')
        issue = st.selectbox('Main issue (if any)', ['None','Battery problem','Screen/display problem','Performance problem','Charging problem','Physical damage','Other'])
        submitted = st.form_submit_button('♻️ Analyse My Device', use_container_width=True)

    if submitted:
        # Simple explainable rule-based recommendation
        if working == 'Yes' and condition in ['Excellent','Good'] and age <= 5 and issue in ['None','Battery problem']:
            rec = 'Sell / Exchange'
            reason = 'The device is working and appears to retain useful value. Selling or exchanging it can extend its useful life.'
            actions = ['Back up your data', 'Sign out of accounts', 'Remove SIM/SD card', 'Factory reset before handing it over']
        elif working in ['Yes','Partially'] and (condition in ['Good','Average'] or issue in ['Battery problem','Performance problem','Charging problem']):
            rec = 'Repair / Reuse'
            reason = 'The device may still have useful life. A repair, upgrade, donation or reuse can delay disposal.'
            actions = ['Check repair cost', 'Back up your data', 'Ask for a repair diagnosis', 'Reuse/donate if repair is practical']
        else:
            rec = 'Recycle'
            reason = 'The device is significantly damaged, non-working or unsuitable for continued use. Responsible recycling is the appropriate next step.'
            actions = ['Back up data if possible', 'Remove SIM/SD card', 'Do not put electronics in regular waste', 'Find an authorised e-waste collection/recycling option']

        save_check((device, age, working, condition, issue, rec, datetime.now().isoformat(timespec='seconds')))

        st.markdown(f'''<div class="result"><h2>{rec}</h2><p>{reason}</p></div>''', unsafe_allow_html=True)
        st.markdown('### Recommended next steps')
        for action in actions:
            st.checkbox(action, key=f'{action}_{device}')

        st.markdown('### Find local options')
        city = st.text_input('Enter your city', placeholder='e.g. Nagpur, Pune, Mumbai')
        if city:
            import urllib.parse
            q1 = urllib.parse.quote_plus(f'{device} sell exchange {city}')
            q2 = urllib.parse.quote_plus(f'authorised e waste recycler {city}')
            c1, c2 = st.columns(2)
            with c1:
                st.link_button('🔎 Search selling/exchange options', f'https://www.google.com/search?q={q1}', use_container_width=True)
            with c2:
                st.link_button('🔎 Search recycling options', f'https://www.google.com/search?q={q2}', use_container_width=True)
        st.caption('Search results should be checked for current availability and authorisation before handing over a device.')

# ---------- Dashboard ----------
elif page == 'Impact Dashboard':
    st.title('📊 Impact Dashboard')
    total, sell, repair, recycle = get_stats()
    a,b,c,d = st.columns(4)
    a.metric('Devices checked', total)
    b.metric('Sell / Exchange', sell)
    c.metric('Repair / Reuse', repair)
    d.metric('Recycle', recycle)

    st.markdown('<div class="card"><h3>What the dashboard shows</h3><p class="small">Every analysis is stored locally in SQLite. This makes the prototype demonstrate basic data collection and sustainability analytics without requiring a separate backend.</p></div>', unsafe_allow_html=True)
    if total:
        st.bar_chart({'Recommendation': {'Sell / Exchange': sell, 'Repair / Reuse': repair, 'Recycle': recycle}})
    else:
        st.info('Analyse a device first to populate the dashboard.')

# ---------- Guide ----------
elif page == 'E-Waste Guide':
    st.title('📘 E-Waste Guide')
    sections = {
        '💾 Before selling or giving away': ['Back up important files', 'Sign out of accounts', 'Remove SIM and memory cards', 'Factory reset the device', 'Keep purchase/accessory information if needed'],
        '🔧 Before repair or reuse': ['Describe the problem clearly', 'Compare repair cost with replacement cost', 'Use the device safely while awaiting repair', 'Consider donating a working device'],
        '♻️ Before recycling': ['Keep electronics separate from household waste', 'Protect batteries from damage', 'Use an appropriate e-waste collection/recycling channel', 'Ask the recycler about data destruction for storage devices']
    }
    for title, items in sections.items():
        with st.expander(title, expanded=True):
            for item in items:
                st.write('• ' + item)

    st.success('Goal: keep electronics in use for longer when practical and route unusable devices toward responsible recycling.')
