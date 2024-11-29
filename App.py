
# Importing Necessary Libraries
import numpy as np
import pandas as pd
import pickle as pkl
import streamlit as st
from fpdf import FPDF
import base64

# Load the model
model = pkl.load(open('MIPML.pkl', 'rb'))

# Page Configuration
st.set_page_config(page_title="Medical Insurance Premium Predictor", page_icon="🏥", layout="wide")

# Custom CSS for Styling
page_style = '''
<style>
body { background-color: #ADD8E6; }
h1, h2 { font-family: 'Arial', sans-serif; text-align: center; color: #2a9df4; }
.sidebar .sidebar-content { background-color: #ADD8E6; }
footer { visibility: hidden; }
input[type="text"], input[type="email"], input[type="password"] { 
    width: 60%; margin-left: auto; margin-right: auto; display: block; 
    border-radius: 5px; padding: 10px; font-size: 16px;
}
.stButton > button { background-color: #4CAF50; color: white; font-size: 18px; 
    border-radius: 10px; height: 45px; width: 60%; margin: 10px auto; display: block; }
.animated-button { 
    display: inline-block; background-color: #4CAF50; padding: 10px 20px; 
    border-radius: 10px; font-size: 18px; color: white; text-align: center; 
    cursor: pointer; margin-top: 10px; transition: background-color 0.3s, transform 0.3s;
}
.animated-button:hover { background-color: #45a049; transform: scale(1.05); }
</style>
'''
st.markdown(page_style, unsafe_allow_html=True)

# Navigation Control
if "page" not in st.session_state:
    st.session_state.page = "personal_details"

def switch_page(new_page):
    st.session_state.page = new_page

def is_valid_phone(phone):
    return phone.isdigit() and len(phone) == 10

# PDF Generation Function
def generate_pdf(name, phone, email, age, gender, bmi, children, smoker, region, premium):
    pdf = FPDF()
    pdf.add_page()

    # Border and Title
    pdf.set_draw_color(0, 0, 0)  # Black border
    pdf.set_line_width(2)  # Thicker border
    pdf.rect(5, 5, 200, 287)  # Border

    pdf.set_font("Arial", 'B', 26)
    pdf.cell(0, 15, "Official Medical Insurance", ln=True, align='C')
    pdf.ln(10)

    # Customer Details
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, f"NAME : {name}", ln=True)
    pdf.cell(0, 10, f"PHONE : {phone}", ln=True)
    pdf.cell(0, 10, f"EMAIL ID : {email}", ln=True)
    pdf.cell(0, 10, f"AGE : {age}", ln=True)
    pdf.cell(0, 10, f"GENDER : {'Female' if gender == 0 else 'Male'}", ln=True)
    pdf.cell(0, 10, f"BMI : {bmi}", ln=True)
    pdf.cell(0, 10, f"NO. OF CHILDREN : {children}", ln=True)
    pdf.cell(0, 10, f"SMOCKING STATUS : {'Yes' if smoker == 1 else 'No'}", ln=True)
    pdf.cell(0, 10, f"REGION : {region}", ln=True)
    pdf.cell(0, 10, f"PREDICTED PREMIUM : {premium} USD", ln=True)

    # Thank You Note
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 14)
    pdf.cell(0, 10, "Thank you for choosing our insurance services!..", ln=True, align='C')

    pdf_name = f"{name}_Insurance_Details.pdf"
    pdf.output(pdf_name)
    return pdf_name

# Function to convert PDF to Base64
def pdf_to_base64(pdf_file):
    with open(pdf_file, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
    return pdf_base64


# Personal Details Page
if st.session_state.page == "personal_details":
    st.markdown("<h1>🏥 Medical Insurance Premium Predictor</h1>", unsafe_allow_html=True)

    with st.form("personal_form"):
        name = st.text_input("📛 Name...")
        phone = st.text_input("📱 Phone Number...", max_chars=10)
        email = st.text_input("📧 Email ID...")
        captcha = st.text_input("🔒 Enter verfication key...")
        submit = st.form_submit_button("Submit")

        if submit:
            if name and is_valid_phone(phone) and email and captcha == '1234':
                st.session_state.name = name
                st.session_state.phone = phone
                st.session_state.email = email
                switch_page("insurance_details")
            else:
                st.error("Please fill all fields correctly and pass the security check....")

# Insurance Details Input Page
elif st.session_state.page == "insurance_details":
    st.markdown("<h2>🔍 Provide Your Medical Insurance Details And Predict...</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([2.5, 2.5])  # 40% for inputs, 60% for icon and button

    with col1:
        gender = st.selectbox('👤 Gender', ['Female', 'Male'])
        smoker = st.selectbox('🚬 Are you a smoker?', ['Yes', 'No'])
        region = st.selectbox('🌍 Region', ['SouthEast', 'SouthWest', 'NorthEast', 'NorthWest'])
        age = st.slider('📅 Age', 5, 80)
        bmi = st.slider('⚖️ BMI (Body Mass Index)', 5, 100)
        children = st.slider('👶 Number of Children', 0, 5)

    with col2:
        st.image("https://img.icons8.com/ios-filled/50/4CAF50/health-insurance.png", width=50)
        if st.button('💼 Predict Premium'):
            gender = 0 if gender == 'Female' else 1
            smoker = 1 if smoker == 'Yes' else 0
            region_map = {'SouthEast': 0, 'SouthWest': 1, 'NorthEast': 2, 'NorthWest': 3}
            region = region_map[region]

            input_data = np.asarray([age, gender, bmi, children, smoker, region]).reshape(1, -1)
            predicted_premium = round(model.predict(input_data)[0], 2)

            st.markdown(f"<h3 style='color: #4CAF50;'>Your Insurance Premium: {predicted_premium} USD</h3>", unsafe_allow_html=True)
            pdf_file = generate_pdf(
                st.session_state.name, st.session_state.phone, st.session_state.email, 
                age, gender, bmi, children, smoker, region, predicted_premium
            )
            pdf_base64 = pdf_to_base64(pdf_file)
            st.markdown(
                f'<a class="animated-button" href="data:application/pdf;base64,{pdf_base64}" download="{pdf_file}">📥 Download PDF</a>', 
                unsafe_allow_html=True
            )
