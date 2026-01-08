import streamlit as st
from datetime import date
from chroma_store import ChromaDiaryStore
from Generator.main import LLMsManager

if "generated_images" not in st.session_state:
    st.session_state.generated_images = None

if "generated_prompt" not in st.session_state:
    st.session_state.generated_prompt = None

@st.cache_resource
def get_store():
    return ChromaDiaryStore()

store = get_store()

@st.cache_resource
def get_ai_generator():
    return LLMsManager()


Art_generator = get_ai_generator()

def generate_images():
    with st.spinner("Generating Stable Diffusion images..."):
        images, prompt = Art_generator.create_image_from_diary(
            scene=diary_text,
            mood=mood,
            style=style,
            num_images=2
        )

    st.session_state.generated_images = images
    st.session_state.generated_prompt = prompt


# ------------------------
# Page config
# ------------------------
st.set_page_config(
    page_title="Diary App",
    page_icon="📔",
    layout="centered"
)

st.title("🌱 Personal Diary")

# ------------------------
# Date selector (calendar)
# ------------------------
selected_date = st.date_input(
    "Select date",
    value=date.today()
)

# ------------------------
# Style & Mood selectors
# ------------------------
style = st.selectbox(
    "Art Style",
    options=["Cyberpunk", "WaterColor", "Realistic", "Pixel Art", "Sketch"]
)

mood = st.selectbox(
    "Mood",
    options=["Happy", "Neutral", "Sad", "Excited", "Anxious"]
)

# ------------------------
# Diary text input
# ------------------------
diary_text = st.text_area(
    "Write your diary entry",
    height=250,
    placeholder="What happened today?"
)

# ------------------------
# Save button
# ------------------------
if st.button("💾 Save Diary"):
    if diary_text.strip() == "":
        st.warning("Diary entry cannot be empty.")
    else:
        
        st.write("### Preview")
        st.write(f"**Date:** {selected_date}")
        st.write(f"**Style:** {style}")
        st.write(f"**Mood:** {mood}")
        st.write("**Content:**")
        st.write(diary_text)

        store.save_diary(
            diary_text=diary_text,
            d=selected_date,
            style=style,
            mood=mood
        )
        st.success("Diary saved!")
        
        generate_images()

if st.session_state.generated_images:
    st.subheader("🎨 Generated Images")

    st.text_area(
        "Prompt",
        value=st.session_state.generated_prompt,
        height=100
    )

    # 🔁 Regenerate button
    if st.button("🔄 Regenerate Images"):
        generate_images()
        st.rerun()

    # ------------------------
    # Image selection
    # ------------------------
    st.subheader("🎨 Select your favorite image")

    cols = st.columns(len(st.session_state.generated_images))

    for i, (col, img) in enumerate(zip(cols, st.session_state.generated_images)):
        with col:
            st.image(img, use_container_width=True)

            if st.button("Select", key=f"select-img-{i}"):
                st.session_state.selected_image_index = i
    if "selected_image_index" in st.session_state:
        st.success(f"Selected Image {st.session_state.selected_image_index + 1}")



entries = store.load_diaries(selected_date)
if entries:
    st.subheader(f"📚 Diaries on {selected_date}")

    for entry in entries:
        time_label = entry["metadata"].get("time", "Unknown time")

        col_text, col_btn = st.columns([8, 1])

        with col_text:
            st.markdown(f"### ⏰ {time_label}")
            st.caption(
                f"🎭 {entry['metadata']['style']} | "
                f"🙂 {entry['metadata']['mood']}"
            )
            st.write(entry["text"])

        with col_btn:
            if st.button("🗑️", key=f"delete-{entry['id']}"):
                store.delete_diary(entry["id"])
                st.success("Diary deleted")
                st.rerun()   

        st.divider()
else:
    st.info("No diary entries for this date.")