# 👔 My Wardrobe App

A smart wardrobe management app that uses AI to automatically categorize your clothes from photos and generate outfit combinations.

## ✨ Features

- **AI Auto-Tagging**: Upload a photo and GPT-4o automatically detects category, color, style, and occasion
- **Tag Scanner**: Snap a photo of the clothing tag to extract brand, size, material, and care instructions
- **My Closet**: View all your clothing items, filter by category, and delete items
- **Generate Outfit**: Create random outfit combinations with optional filters
- **Saved Outfits**: Save your favorite outfit combinations for later

---

## Setup Instructions

### Step 1: Install Python

If you don't have Python installed:
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.11 or newer
3. During installation, **check the box that says "Add Python to PATH"**

### Step 2: Get an OpenAI API Key

1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Step 3: Open Terminal/Command Prompt

- **Windows**: Press `Win + R`, type `cmd`, press Enter
- **Mac**: Press `Cmd + Space`, type `Terminal`, press Enter

### Step 4: Navigate to the App Folder

```bash
cd path/to/wardrobe_app
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Run the App

```bash
streamlit run app.py
```

### Step 7: Enter Your API Key

When the app opens, you'll be prompted to enter your OpenAI API key. This is saved locally and used for AI image analysis.

### Step 8: Access on Your Phone

When Streamlit starts, it will show something like:
```
Local URL: http://localhost:8501
Network URL: http://192.168.1.XXX:8501
```

To access from your phone:
1. Make sure your phone is on the same WiFi network as your computer
2. Open your phone's browser
3. Type in the **Network URL**

---

## How to Use

### Adding Clothes (AI-Powered)

1. Go to "Add Clothes" in the sidebar
2. Upload a photo of your clothing item
3. (Optional) Upload a photo of the clothing tag
4. Click "✨ Analyze with AI"
5. Review the auto-filled details, make any edits
6. Click "Add to Wardrobe"

### What the AI Extracts

**From garment photo:**
- Category (Top, Bottom, Shoes, etc.)
- Primary color
- Style tags (Casual, Formal, etc.)
- Suitable occasions
- Seasonal appropriateness
- Suggested item name

**From tag photo:**
- Brand name
- Size
- Material/fabric composition
- Care instructions

### Generating Outfits

1. Go to "Generate Outfit"
2. Optionally select an occasion or season filter
3. Click "Generate Random Outfit"
4. If you like it, name it and click "Save Outfit"

---

## File Structure

```
wardrobe_app/
├── app.py              # Main application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── user_config.json   # Your API key (created on first run)
├── wardrobe_data.json # Your wardrobe data (created automatically)
└── clothing_images/   # Uploaded images (created automatically)
```

---

## API Costs

The app uses GPT-4o for image analysis. Typical costs:
- ~$0.01-0.03 per garment analyzed
- Adding 100 items ≈ $1-3 total

---

## Troubleshooting

**"streamlit: command not found"**
- Try: `python -m streamlit run app.py`

**API key validation fails**
- Make sure you copied the full key (starts with `sk-`)
- Check that your OpenAI account has credits/payment method

**Can't access from phone**
- Make sure both devices are on the same WiFi
- Check if your firewall is blocking port 8501

**AI analysis fails**
- Check your internet connection
- Verify your API key is valid in Settings

---

## Future Enhancements

- [ ] Color harmony matching for outfits
- [ ] Weather-based suggestions
- [ ] Outfit calendar with wear tracking
- [ ] Cost-per-wear analytics
- [ ] Native mobile app

---

Built with ❤️ using Streamlit + GPT-4o
