import streamlit as st
from PIL import Image
import base64
import os

st.set_page_config(layout="centered")

# Title
st.markdown(
    "<h1 style='text-align:center; color:#333;'>👗 Welcome to AP Collections</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align:center; color:gray;'>Find Your Inner Diva with AP Collections</h3>",
    unsafe_allow_html=True
)

# Banner
banner_path = "images/fb_banner.png"
if os.path.exists(banner_path):
    with open(banner_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <div>
            <img src='data:image/png;base64,{encoded}' style="width: 100%; height: 300px; border-radius: 10px; object-fit: cover;" />
        </div>
        """,
        unsafe_allow_html=True
    )

# About Us
st.markdown("## 🌟 Made in Myanmar, For You")
st.write("""
* Locally designed and crafted with pride  
* **“Warm & Cozy” coat & pants sets** — effortless style and comfort  
* **“Free & Smart” straight pants** — high quality and modern cut  
* Each piece tells the story of Myanmar elegance  
""")

# Gallery
st.markdown("## 🖼️ Signature Styles")
image_dir = "images/gallery"
if os.path.exists(image_dir):
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    cols = st.columns(3)
    for i, img_file in enumerate(image_files):
        with cols[i % 3]:
            st.image(os.path.join(image_dir, img_file), use_container_width=True)
else:
    st.info("Gallery folder not found. Add product images to 'images/gallery/' to display them here.")

# Message
st.markdown("## 💬 Our Connection with You")
st.info("""
“Thank you for supporting local craftsmanship!  
Your trust inspires each design — whether it’s staying ‘Warm & Cozy’ or feeling ‘Free & Smart’.  
— The AP Collections Family”
""")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#999;'>📍 Mandalay, Myanmar | 📞 Contact us on Facebook: <a href='https://www.facebook.com/apcollection.mdy' target='_blank'>apcollection.mdy</a></p>",
    unsafe_allow_html=True
)
