import streamlit as st
import json
import os
import random
from datetime import datetime
from pathlib import Path
import base64
from PIL import Image
import io
import httpx

# Configuration
DATA_FILE = "wardrobe_data.json"
IMAGES_DIR = "clothing_images"
CONFIG_FILE = "user_config.json"

# Ensure directories exist
Path(IMAGES_DIR).mkdir(exist_ok=True)


# ====================
# API Key Management
# ====================

def load_config():
    """Load user configuration including API key."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(config):
    """Save user configuration."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def validate_openai_key(api_key):
    """Validate OpenAI API key by making a simple request."""
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 5
            },
            timeout=10.0
        )
        return response.status_code == 200
    except Exception:
        return False


def image_to_base64(image_file):
    """Convert uploaded image to base64 string."""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')


def analyze_garment_image(api_key, image_base64, image_type="image/jpeg"):
    """Use GPT-4o to analyze a garment image."""
    
    prompt = """Analyze this clothing item image and extract the following attributes. 
    Return ONLY a valid JSON object with these exact keys:
    {
        "category": "one of: Top, Bottom, Shoes, Outerwear, Accessory, Dress/Jumpsuit",
        "color": "primary color - one of: Black, White, Gray, Navy, Blue, Red, Green, Brown, Beige, Pink, Purple, Orange, Yellow, Multi",
        "style": ["list of applicable styles from: Casual, Formal, Business, Streetwear, Athleisure, Smart Casual, Bohemian, Minimalist"],
        "occasions": ["list of applicable occasions from: Everyday, Work, Date Night, Party, Workout, Outdoor, Formal Event, Loungewear"],
        "seasons": ["list of applicable seasons from: Spring, Summer, Fall, Winter, All Season"],
        "pattern": "solid, striped, plaid, floral, graphic, etc.",
        "suggested_name": "a descriptive name for this item, e.g. 'Navy Cotton Oxford Shirt'"
    }
    
    Be accurate and practical with your categorization. Return ONLY the JSON, no other text."""
    
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{image_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 500
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            # Clean up the response - remove markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return json.loads(content.strip())
        else:
            return None
    except Exception as e:
        st.error(f"Error analyzing image: {str(e)}")
        return None


def analyze_tag_image(api_key, image_base64, image_type="image/jpeg"):
    """Use GPT-4o to OCR and extract info from a clothing tag."""
    
    prompt = """Analyze this clothing tag/label image and extract any visible information.
    Return ONLY a valid JSON object with these keys (use null for any info not visible):
    {
        "brand": "brand name if visible",
        "size": "size if visible (S, M, L, XL, or numeric)",
        "material": "fabric composition if visible, e.g. '100% Cotton' or '60% Cotton, 40% Polyester'",
        "care_instructions": ["list of care instructions if visible, e.g. 'Machine wash cold', 'Tumble dry low'"],
        "country_of_origin": "country if visible"
    }
    
    Return ONLY the JSON, no other text. Use null for fields you cannot read."""
    
    try:
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{image_type};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            content = response.json()["choices"][0]["message"]["content"]
            # Clean up the response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            return json.loads(content.strip())
        else:
            return None
    except Exception as e:
        st.error(f"Error analyzing tag: {str(e)}")
        return None

# Category and tag options
CATEGORIES = ["Top", "Bottom", "Shoes", "Outerwear", "Accessory", "Dress/Jumpsuit"]
COLORS = ["Black", "White", "Gray", "Navy", "Blue", "Red", "Green", "Brown", "Beige", "Pink", "Purple", "Orange", "Yellow", "Multi"]
STYLES = ["Casual", "Formal", "Business", "Streetwear", "Athleisure", "Smart Casual", "Bohemian", "Minimalist"]
OCCASIONS = ["Everyday", "Work", "Date Night", "Party", "Workout", "Outdoor", "Formal Event", "Loungewear"]
SEASONS = ["Spring", "Summer", "Fall", "Winter", "All Season"]


def load_wardrobe():
    """Load wardrobe data from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"items": [], "outfits": []}


def save_wardrobe(data):
    """Save wardrobe data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def save_image(uploaded_file, item_id):
    """Save uploaded image and return the file path."""
    extension = uploaded_file.name.split(".")[-1]
    filename = f"{item_id}.{extension}"
    filepath = os.path.join(IMAGES_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return filepath


def get_image_base64(filepath):
    """Convert image to base64 for display."""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode()


def display_clothing_item(item, show_delete=False):
    """Display a clothing item card."""
    if os.path.exists(item["image_path"]):
        st.image(item["image_path"], use_container_width=True)
    st.caption(f"**{item['name']}**")
    st.caption(f"{item['category']} • {item['color']}")
    if show_delete:
        return st.button("🗑️ Delete", key=f"del_{item['id']}")
    return False


def generate_random_outfit(wardrobe, include_categories):
    """Generate a random outfit based on selected categories."""
    outfit = {}
    items = wardrobe["items"]
    
    for category in include_categories:
        category_items = [item for item in items if item["category"] == category]
        if category_items:
            outfit[category] = random.choice(category_items)
    
    return outfit


def generate_smart_outfit(wardrobe, occasion=None, season=None):
    """Generate an outfit with optional filtering by occasion/season."""
    items = wardrobe["items"]
    
    # Filter by occasion and season if specified
    if occasion:
        items = [item for item in items if occasion in item.get("occasions", [])]
    if season:
        items = [item for item in items if season in item.get("seasons", []) or "All Season" in item.get("seasons", [])]
    
    # If filters result in too few items, fall back to all items
    if len(items) < 3:
        items = wardrobe["items"]
    
    outfit = {}
    
    # Check if there's a dress/jumpsuit (which replaces top+bottom)
    dresses = [item for item in items if item["category"] == "Dress/Jumpsuit"]
    
    if dresses and random.random() > 0.5:
        # Use a dress/jumpsuit
        outfit["Dress/Jumpsuit"] = random.choice(dresses)
    else:
        # Use top + bottom
        tops = [item for item in items if item["category"] == "Top"]
        bottoms = [item for item in items if item["category"] == "Bottom"]
        
        if tops:
            outfit["Top"] = random.choice(tops)
        if bottoms:
            outfit["Bottom"] = random.choice(bottoms)
    
    # Add shoes
    shoes = [item for item in items if item["category"] == "Shoes"]
    if shoes:
        outfit["Shoes"] = random.choice(shoes)
    
    # Maybe add outerwear
    outerwear = [item for item in items if item["category"] == "Outerwear"]
    if outerwear and random.random() > 0.6:
        outfit["Outerwear"] = random.choice(outerwear)
    
    # Maybe add accessory
    accessories = [item for item in items if item["category"] == "Accessory"]
    if accessories and random.random() > 0.5:
        outfit["Accessory"] = random.choice(accessories)
    
    return outfit


# Page configuration
st.set_page_config(
    page_title="My Wardrobe",
    page_icon="👔",
    layout="wide"
)

# Custom CSS for mobile-friendly design
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
    }
    .clothing-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 1rem;
    }
    .outfit-display {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = load_wardrobe()

if "current_outfit" not in st.session_state:
    st.session_state.current_outfit = None

# Sidebar navigation
st.sidebar.title("👔 My Wardrobe")

# Load config
config = load_config()

# Check for API key
if "api_key" not in config or not config["api_key"]:
    st.sidebar.warning("⚠️ API key required")
    page = "Setup"
else:
    page = st.sidebar.radio("Navigate", ["My Closet", "Add Clothes", "Generate Outfit", "Saved Outfits", "Settings"])

# Display wardrobe stats in sidebar
wardrobe = st.session_state.wardrobe
st.sidebar.markdown("---")
st.sidebar.markdown("**Wardrobe Stats**")
st.sidebar.write(f"Total items: {len(wardrobe['items'])}")
for cat in CATEGORIES:
    count = len([i for i in wardrobe["items"] if i["category"] == cat])
    if count > 0:
        st.sidebar.write(f"  {cat}: {count}")


# Page: Setup (API Key Entry)
if page == "Setup":
    st.title("🔑 Welcome to My Wardrobe")
    st.write("To use AI-powered features, please enter your OpenAI API key.")
    st.write("")
    
    with st.form("api_key_form"):
        st.markdown("""
        **How to get an API key:**
        1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
        2. Sign in or create an account
        3. Click "Create new secret key"
        4. Copy and paste it below
        """)
        
        api_key_input = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        
        submitted = st.form_submit_button("Save & Continue", use_container_width=True)
        
        if submitted:
            if not api_key_input:
                st.error("Please enter an API key.")
            elif not api_key_input.startswith("sk-"):
                st.error("Invalid API key format. It should start with 'sk-'")
            else:
                with st.spinner("Validating API key..."):
                    if validate_openai_key(api_key_input):
                        config["api_key"] = api_key_input
                        save_config(config)
                        st.success("API key saved successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid API key. Please check and try again.")
    
    st.markdown("---")
    st.caption("Your API key is stored locally on your device and is never shared.")


# Page: My Closet
elif page == "My Closet":
    st.title("👕 My Closet")
    
    if not wardrobe["items"]:
        st.info("Your closet is empty! Go to 'Add Clothes' to start building your wardrobe.")
    else:
        # Filter options
        filter_category = st.selectbox("Filter by category", ["All"] + CATEGORIES)
        
        filtered_items = wardrobe["items"]
        if filter_category != "All":
            filtered_items = [i for i in filtered_items if i["category"] == filter_category]
        
        # Display items in a grid
        cols = st.columns(3)
        for idx, item in enumerate(filtered_items):
            with cols[idx % 3]:
                if display_clothing_item(item, show_delete=True):
                    # Delete item
                    wardrobe["items"] = [i for i in wardrobe["items"] if i["id"] != item["id"]]
                    # Delete image file
                    if os.path.exists(item["image_path"]):
                        os.remove(item["image_path"])
                    save_wardrobe(wardrobe)
                    st.session_state.wardrobe = wardrobe
                    st.rerun()


# Page: Add Clothes
elif page == "Add Clothes":
    st.title("➕ Add New Item")
    
    # Initialize session state for AI results
    if "ai_analysis" not in st.session_state:
        st.session_state.ai_analysis = None
    if "tag_analysis" not in st.session_state:
        st.session_state.tag_analysis = None
    
    # Step 1: Upload images
    st.subheader("📸 Step 1: Upload Photos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Garment Photo** (required)")
        garment_file = st.file_uploader(
            "Upload a photo of your clothing item",
            type=["jpg", "jpeg", "png", "webp"],
            key="garment_upload"
        )
        if garment_file:
            st.image(garment_file, caption="Garment", use_container_width=True)
    
    with col2:
        st.markdown("**Tag Photo** (optional)")
        tag_file = st.file_uploader(
            "Upload a photo of the clothing tag",
            type=["jpg", "jpeg", "png", "webp"],
            key="tag_upload"
        )
        if tag_file:
            st.image(tag_file, caption="Tag", use_container_width=True)
    
    # Step 2: Analyze with AI
    if garment_file:
        st.subheader("🤖 Step 2: AI Analysis")
        
        if st.button("✨ Analyze with AI", use_container_width=True):
            api_key = config.get("api_key")
            
            with st.spinner("Analyzing garment..."):
                # Analyze garment image
                garment_base64 = image_to_base64(garment_file)
                garment_type = garment_file.type or "image/jpeg"
                st.session_state.ai_analysis = analyze_garment_image(api_key, garment_base64, garment_type)
            
            if tag_file:
                with st.spinner("Reading tag..."):
                    # Analyze tag image
                    tag_base64 = image_to_base64(tag_file)
                    tag_type = tag_file.type or "image/jpeg"
                    st.session_state.tag_analysis = analyze_tag_image(api_key, tag_base64, tag_type)
            
            if st.session_state.ai_analysis:
                st.success("Analysis complete! Review and edit below.")
            else:
                st.error("Analysis failed. Please try again or enter details manually.")
        
        # Step 3: Review and save
        st.subheader("📝 Step 3: Review & Save")
        
        # Pre-fill form with AI results if available
        ai = st.session_state.ai_analysis or {}
        tag = st.session_state.tag_analysis or {}
        
        with st.form("add_item_form"):
            # Basic info
            name = st.text_input(
                "Item name",
                value=ai.get("suggested_name", ""),
                placeholder="e.g., Blue Oxford Shirt"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Get default index for category
                category_default = 0
                if ai.get("category") in CATEGORIES:
                    category_default = CATEGORIES.index(ai.get("category"))
                category = st.selectbox("Category", CATEGORIES, index=category_default)
                
                # Get default index for color
                color_default = 0
                if ai.get("color") in COLORS:
                    color_default = COLORS.index(ai.get("color"))
                color = st.selectbox("Primary color", COLORS, index=color_default)
            
            with col2:
                # Tag info
                brand = st.text_input("Brand", value=tag.get("brand") or "")
                size = st.text_input("Size", value=tag.get("size") or "")
            
            # Style tags
            default_styles = ai.get("style", ["Casual"])
            valid_styles = [s for s in default_styles if s in STYLES] or ["Casual"]
            style = st.multiselect("Style tags", STYLES, default=valid_styles)
            
            # Occasions
            default_occasions = ai.get("occasions", ["Everyday"])
            valid_occasions = [o for o in default_occasions if o in OCCASIONS] or ["Everyday"]
            occasions = st.multiselect("Occasions", OCCASIONS, default=valid_occasions)
            
            # Seasons
            default_seasons = ai.get("seasons", ["All Season"])
            valid_seasons = [s for s in default_seasons if s in SEASONS] or ["All Season"]
            seasons = st.multiselect("Seasons", SEASONS, default=valid_seasons)
            
            # Additional tag info
            with st.expander("Additional Details (from tag)"):
                material = st.text_input("Material", value=tag.get("material") or "")
                care = st.text_area(
                    "Care instructions",
                    value="\n".join(tag.get("care_instructions", [])) if tag.get("care_instructions") else ""
                )
            
            submitted = st.form_submit_button("💾 Add to Wardrobe", use_container_width=True)
            
            if submitted:
                if not name:
                    st.error("Please enter a name for this item.")
                else:
                    # Generate unique ID
                    item_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"
                    
                    # Save garment image
                    image_path = save_image(garment_file, item_id)
                    
                    # Save tag image if provided
                    tag_image_path = None
                    if tag_file:
                        tag_image_path = save_image(tag_file, f"{item_id}_tag")
                    
                    # Create item
                    new_item = {
                        "id": item_id,
                        "name": name,
                        "category": category,
                        "color": color,
                        "style": style,
                        "occasions": occasions,
                        "seasons": seasons,
                        "image_path": image_path,
                        "tag_image_path": tag_image_path,
                        "brand": brand,
                        "size": size,
                        "material": material,
                        "care_instructions": care.split("\n") if care else [],
                        "pattern": ai.get("pattern"),
                        "added_date": datetime.now().isoformat()
                    }
                    
                    # Add to wardrobe
                    wardrobe["items"].append(new_item)
                    save_wardrobe(wardrobe)
                    st.session_state.wardrobe = wardrobe
                    
                    # Clear AI analysis
                    st.session_state.ai_analysis = None
                    st.session_state.tag_analysis = None
                    
                    st.success(f"Added '{name}' to your wardrobe!")
                    st.balloons()


# Page: Generate Outfit
elif page == "Generate Outfit":
    st.title("✨ Generate Outfit")
    
    if len(wardrobe["items"]) < 2:
        st.warning("Add at least 2 items to your wardrobe to generate outfits!")
    else:
        # Generation options
        st.subheader("Options")
        
        col1, col2 = st.columns(2)
        with col1:
            occasion_filter = st.selectbox("Occasion (optional)", ["Any"] + OCCASIONS)
        with col2:
            season_filter = st.selectbox("Season (optional)", ["Any"] + SEASONS)
        
        # Generate button
        if st.button("🎲 Generate Random Outfit", use_container_width=True):
            occasion = None if occasion_filter == "Any" else occasion_filter
            season = None if season_filter == "Any" else season_filter
            
            st.session_state.current_outfit = generate_smart_outfit(wardrobe, occasion, season)
        
        # Display current outfit
        if st.session_state.current_outfit:
            st.markdown("---")
            st.subheader("Your Outfit")
            
            outfit = st.session_state.current_outfit
            
            # Display outfit items
            cols = st.columns(len(outfit))
            for idx, (category, item) in enumerate(outfit.items()):
                with cols[idx]:
                    st.markdown(f"**{category}**")
                    if os.path.exists(item["image_path"]):
                        st.image(item["image_path"], use_container_width=True)
                    st.caption(item["name"])
            
            # Save outfit button
            col1, col2 = st.columns(2)
            with col1:
                outfit_name = st.text_input("Name this outfit", placeholder="e.g., Monday Work Look")
            with col2:
                st.write("")  # Spacing
                st.write("")  # Spacing
                if st.button("💾 Save Outfit"):
                    if outfit_name:
                        saved_outfit = {
                            "id": f"outfit_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "name": outfit_name,
                            "items": [item["id"] for item in outfit.values()],
                            "created_date": datetime.now().isoformat()
                        }
                        wardrobe["outfits"].append(saved_outfit)
                        save_wardrobe(wardrobe)
                        st.session_state.wardrobe = wardrobe
                        st.success(f"Saved '{outfit_name}'!")
                    else:
                        st.error("Please name your outfit before saving.")


# Page: Saved Outfits
elif page == "Saved Outfits":
    st.title("💾 Saved Outfits")
    
    if not wardrobe["outfits"]:
        st.info("No saved outfits yet. Generate and save some outfits!")
    else:
        for outfit_data in wardrobe["outfits"]:
            with st.expander(f"👔 {outfit_data['name']}", expanded=False):
                # Get outfit items
                outfit_items = [item for item in wardrobe["items"] if item["id"] in outfit_data["items"]]
                
                if outfit_items:
                    cols = st.columns(len(outfit_items))
                    for idx, item in enumerate(outfit_items):
                        with cols[idx]:
                            if os.path.exists(item["image_path"]):
                                st.image(item["image_path"], use_container_width=True)
                            st.caption(f"{item['category']}: {item['name']}")
                
                # Delete button
                if st.button("🗑️ Delete Outfit", key=f"del_outfit_{outfit_data['id']}"):
                    wardrobe["outfits"] = [o for o in wardrobe["outfits"] if o["id"] != outfit_data["id"]]
                    save_wardrobe(wardrobe)
                    st.session_state.wardrobe = wardrobe
                    st.rerun()


# Page: Settings
elif page == "Settings":
    st.title("⚙️ Settings")
    
    st.subheader("API Key")
    
    # Show masked current key
    current_key = config.get("api_key", "")
    if current_key:
        masked_key = current_key[:7] + "..." + current_key[-4:]
        st.write(f"Current key: `{masked_key}`")
    
    with st.form("update_api_key"):
        new_key = st.text_input("New OpenAI API Key", type="password", placeholder="sk-...")
        
        if st.form_submit_button("Update API Key"):
            if new_key:
                if not new_key.startswith("sk-"):
                    st.error("Invalid API key format.")
                else:
                    with st.spinner("Validating..."):
                        if validate_openai_key(new_key):
                            config["api_key"] = new_key
                            save_config(config)
                            st.success("API key updated!")
                        else:
                            st.error("Invalid API key.")
    
    st.markdown("---")
    
    st.subheader("Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Total items:** {len(wardrobe['items'])}")
        st.write(f"**Saved outfits:** {len(wardrobe['outfits'])}")
    
    with col2:
        # Export data
        if st.button("📤 Export Wardrobe Data"):
            export_data = json.dumps(wardrobe, indent=2)
            st.download_button(
                "Download JSON",
                export_data,
                file_name="wardrobe_backup.json",
                mime="application/json"
            )
    
    st.markdown("---")
    
    # Danger zone
    with st.expander("⚠️ Danger Zone"):
        st.warning("These actions cannot be undone!")
        
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.session_state.confirm_delete = True
        
        if st.session_state.get("confirm_delete"):
            st.error("Are you sure? This will delete all your clothes and outfits.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, delete everything"):
                    # Clear wardrobe
                    wardrobe = {"items": [], "outfits": []}
                    save_wardrobe(wardrobe)
                    st.session_state.wardrobe = wardrobe
                    
                    # Clear images
                    for f in Path(IMAGES_DIR).glob("*"):
                        f.unlink()
                    
                    st.session_state.confirm_delete = False
                    st.success("All data cleared.")
                    st.rerun()
            with col2:
                if st.button("Cancel"):
                    st.session_state.confirm_delete = False
                    st.rerun()


# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("*Phase 1 Prototype*")
st.sidebar.markdown("Built with Streamlit 🎈")
