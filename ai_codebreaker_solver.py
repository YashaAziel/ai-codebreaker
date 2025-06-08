# AI Codebreaker Solver (Streamlit + OCR + Logic)
# Part 1: Core game logic

import streamlit as st
import cv2
import numpy as np
import easyocr
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="AI Codebreaker Solver", layout="centered")
st.title("🔐 AI Codebreaker Solver")

# Constants
VALID_DIGITS = list(map(str, range(1, 9)))
MAX_ATTEMPTS = 3

# Color ranges (in BGR)
COLOR_RANGES = {
    'green': ((50, 150, 50), (100, 255, 130)),
    'yellow': ((0, 200, 200), (50, 255, 255)),
    'black': ((0, 0, 0), (50, 50, 50))
}

@st.cache_data
def read_image(file):
    image = Image.open(file).convert('RGB')
    return np.array(image)

@st.cache_data
def extract_text_and_colors(image):
    reader = easyocr.Reader(['en'], gpu=False)
    results = reader.readtext(image)
    text_data = []

    for (bbox, text, prob) in results:
        if prob > 0.4 and text.strip().isdigit():
            text_data.append(text.strip())

    return text_data

# Solver logic: build possible combinations and score them based on hints
from itertools import permutations

def get_feedback(code, guess):
    feedback = [''] * 4
    for i in range(4):
        if guess[i] == code[i]:
            feedback[i] = 'green'
        elif guess[i] in code:
            feedback[i] = 'yellow'
        else:
            feedback[i] = 'black'
    return feedback

def filter_candidates(attempts):
    all_perms = list(permutations(VALID_DIGITS, 4))
    candidates = []

    for cand in all_perms:
        valid = True
        for attempt in attempts:
            guess, expected = attempt
            if get_feedback(cand, guess) != expected:
                valid = False
                break
        if valid:
            candidates.append(cand)
    return candidates

# Main app
st.subheader("Upload a screenshot of the codebreaker game")
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image_np = read_image(uploaded_file)
    st.image(image_np, caption="Uploaded Screenshot", use_column_width=True)

    digits = extract_text_and_colors(image_np)
    st.write("Detected digits:", digits)

    # Manual input of color results
    st.subheader("Enter feedback for each attempt")
    attempts = []
    for i in range(MAX_ATTEMPTS):
        col1, col2 = st.columns(2)
        with col1:
            guess = st.text_input(f"Attempt {i+1} - Guess (4 digits, space-separated)", key=f"g{i}")
        with col2:
            colors = st.text_input(f"Attempt {i+1} - Colors (g/y/b)", key=f"c{i}")

        if guess and colors:
            guess_digits = guess.strip().split()
            color_list = [
                'green' if c=='g' else 'yellow' if c=='y' else 'black'
                for c in colors.strip().lower()
            ]
            if len(guess_digits) == 4 and len(color_list) == 4:
                attempts.append((guess_digits, color_list))

    if attempts:
        candidates = filter_candidates(attempts)
        if candidates:
            st.success(f"{len(candidates)} possible code(s) remaining")
            st.code("Next best guess: " + ' '.join(candidates[0]))
        else:
            st.error("No valid candidates found. Double-check your inputs.")