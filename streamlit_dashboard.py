import streamlit as st
from agent import run_query_and_get_response

st.set_page_config(page_title="SQL Chatbot Dashboard", layout="wide")
st.title("🧠 SQL + Chart Chatbot Dashboard")

query = st.text_input("💬 Ask something about the Chinook database:",
                      placeholder="Example: Which country's customers spent the most?")

if st.button("Run Query"):
    if not query.strip():
        st.warning("Please enter a query.")
    else:
        with st.spinner("⏳ Thinking..."):
            try:
                result = run_query_and_get_response(query)
                st.success("✅ Query completed!")

                if result.startswith("__chart__:"):
                    import base64
                    from io import BytesIO
                    from PIL import Image

                    base64_str = result.replace("__chart__:", "")
                    try:
                        image_data = base64.b64decode(base64_str)
                        image = Image.open(BytesIO(image_data))
                        st.image(image, caption="📊 Dashboard Chart", use_container_width=True)
                    except Exception as e:
                        st.error(f"❌ Failed to load chart image: {e}")
                else:
                    # fallback to show markdown/table if it's not a chart
                    st.markdown(result)

            except Exception as e:
                st.error(f"❌ Error: {e}")