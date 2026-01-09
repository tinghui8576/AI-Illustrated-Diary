import streamlit as st
from datetime import date
from chroma_store import ChromaDiaryStore
from Generator.main import LLMsManager

if "generated_images" not in st.session_state:
    st.session_state.generated_images = None

if "generated_prompt" not in st.session_state:
    st.session_state.generated_prompt = None

if "has_generated" not in st.session_state:
    st.session_state.has_generated = False

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
    st.session_state.has_generated = True

def reset_temp_state():
    temp_keys = ["generated_images", "generated_prompt", "selected_image_index", "has_generated"]
    for key in temp_keys:
        if key in st.session_state:
            del st.session_state[key]


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
# Generate Images 
# ------------------------
if not st.session_state.has_generated:
    if st.button("🎨 Generate Images"):
        if diary_text.strip() == "":
            st.warning("Diary entry cannot be empty.")
        else:
            generate_images()
            st.rerun()



if st.session_state.generated_images:

    # ------------------------
    # Regenerate Images
    # ------------------------
    if st.session_state.generated_images and st.session_state.has_generated:
        if st.button("🔄 Regenerate Images"):
            reset_temp_state()
            generate_images()
            st.rerun()
    # ------------------------
    # Image selection
    # ------------------------
    st.subheader("🎨 Select your favorite image")

    st.markdown("""
    <style>
    .image-card {
        border-radius: 12px;
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .image-card:hover {
        transform: scale(1.03);
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(st.session_state.generated_images))

    for i, (col, img) in enumerate(zip(cols, st.session_state.generated_images)):
        with col:
            st.markdown('<div class="image-card">', unsafe_allow_html=True)
            st.image(img, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("Select", key=f"select-img-{i}"):
                st.session_state.selected_image_index = i
                st.success(f"Selected Image {i+1}")

    # ------------------------
    # Save diary entry with image
    # ------------------------
    if "selected_image_index" in st.session_state:
        store.save_diary(
            diary_text=diary_text,
            d=selected_date,
            image=st.session_state.generated_images[st.session_state.selected_image_index],
            style=style,
            mood=mood
        )
        
        st.success("Diary saved!")
        reset_temp_state()
        st.rerun() 
    

# ------------------------
# Load and display diaries for the selected date
# ------------------------
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

            image_path = entry["metadata"].get("image_path")
            if image_path:
                st.image(image_path, use_container_width=True)

            st.write(entry["text"])

        with col_btn:
            if st.button("🗑️", key=f"delete-{entry['id']}"):
                store.delete_diary(entry["id"])
                st.success("Diary deleted")
                st.rerun()   

        st.divider()
else:
    st.info("No diary entries for this date.")