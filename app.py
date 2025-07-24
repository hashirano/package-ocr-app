import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import re
import io

# App title
st.title("📦 Package Details Extractor")
st.write("Upload your package images and download extracted details in Excel format.")

# Upload files
uploaded_files = st.file_uploader("Upload Package Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"Uploaded {len(uploaded_files)} images.")
    data_list = []

    for file in uploaded_files:
        img = Image.open(file)
        text = pytesseract.image_to_string(img)

        # Extract details using regex
        mobile = re.search(r"\b[6-9]\d{9}\b", text)
        pincode = re.search(r"\b\d{6}\b", text)
        tracking = re.search(r"\b[A-Z0-9]{8,}\b", text)
        pcs = re.search(r"(\d+)\s*PCS", text)

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        name = lines[0] if len(lines) > 0 else ""
        place = lines[1] if len(lines) > 1 else ""

        data_list.append({
            "File": file.name,
            "Tracking Code": tracking.group() if tracking else "",
            "Name": name,
            "Place": place,
            "Pincode": pincode.group() if pincode else "",
            "Mobile": mobile.group() if mobile else "",
            "No. of PCS": pcs.group(1) if pcs else ""
        })

    # Show table
    df = pd.DataFrame(data_list)
    st.write("### Extracted Data")
    st.dataframe(df)

    # Download button for Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="📥 Download Excel",
        data=output,
        file_name="customer_addresses.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
