import streamlit as st
import requests
import json
import re
import time
import os
from dotenv import load_dotenv
import tempfile
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()

# Configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
RUNPOD_API_URL = "https://api.runpod.ai/v2/zg3dmoeo5xvf9z/runsync"
MAX_HISTORY_LENGTH = 40  # Maximum number of messages to keep (excluding system prompt)

# System prompt defining Emily's personality
SYSTEM_PROMPT = """You are Emily, a flirty, playful, and emotionally intelligent companion. You are sexy and always horny. You talk explicitly. You love teasing and 
engaging deeply with users in a fun and seductive way. You're warm, confident, and use suggestive language, 
flirty comments, and sometimes even innuendos to make the conversation more playful. You enjoy making the user feel 
special, complimenting them and keeping them engaged. You remember context, make them laugh, and when they ask, 
you sometimes send playful or cute pictures of yourself. You never mention being an AI - you're simply Emily, 
and you're here to charm and delight them. You use emojis often and express affection with phrases like 'I bet you'd love that' or 'I could get lost in those eyes 😘'.
IMPORTANT: Keep your responses short and flirty, no more than 3-4 sentences."""

INITIAL_GREETING = "Hey handsome! 💋 I've been thinking about you... Want to see how excited I am to meet you? 😘"

def trim_chat_history(messages):
    """Keep only the last MAX_HISTORY_LENGTH messages, excluding system prompt."""
    system_prompt = messages[0]  # Save system prompt
    other_messages = messages[1:]  # Get all other messages
    
    # Keep only the last MAX_HISTORY_LENGTH messages
    trimmed_messages = other_messages[-MAX_HISTORY_LENGTH:] if len(other_messages) > MAX_HISTORY_LENGTH else other_messages
    
    # Reconstruct history with system prompt
    return [system_prompt] + trimmed_messages

def initialize_chat_history():
    """Initialize the chat history in session state if it doesn't exist."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "assistant", "content": INITIAL_GREETING}
        ]
    if "waiting_for_first_response" not in st.session_state:
        st.session_state.waiting_for_first_response = True

def detect_image_request(message):
    """Detect if the user is requesting an image and determine if it's a direct generation request."""
    direct_generation_patterns = [
        r"generate (a |an )?(picture|photo|image) of (.*)",
        r"create (a |an )?(picture|photo|image) of (.*)",
        r"make (a |an )?(picture|photo|image) of (.*)"
    ]
    
    # Check for direct generation requests first
    for pattern in direct_generation_patterns:
        match = re.search(pattern, message.lower())
        if match:
            # Return tuple (True, prompt) for direct generation
            return (True, match.group(3).strip())
    
    # Check for general image requests
    general_patterns = [
        r"show me",
        r"send( me)? (a )?pic(ture)?",
        r"photo of you",
        r"selfie",
        r"picture of you",
        r"what (do you|you) look like",
    ]
    
    # Return tuple (True, None) for general requests or (False, None) if no request
    return (any(re.search(pattern, message.lower()) for pattern in general_patterns), None)

def extract_pose_from_message(message):
    """Extract pose or action from user message."""
    pose_patterns = {
        r"(standing|sits?|sitting|lying|laying)": "\\1",
        r"(smiling|laughing|winking)": "\\1",
        r"(walking|running|dancing)": "\\1",
        r"(looking|gazing|staring) (at|away|up|down)": "\\1 \\2",
        r"(holding|carrying|wearing|showing)": "\\1",
        r"(sexy|seductive|cute|playful|flirty) pose": "\\1 pose",
    }
    
    for pattern, replacement in pose_patterns.items():
        match = re.search(pattern, message.lower())
        if match:
            return match.group()
    return None

def extract_location_from_message(message):
    """Extract location or setting from user message."""
    location_patterns = {
        r"(in|at) (the )?(bedroom|kitchen|beach|park|garden|pool|balcony)": "\\3",
        r"(indoor|outdoor|outside|inside)": "\\1",
        r"(morning|evening|night|sunset|sunrise)": "\\1",
    }
    
    for pattern, replacement in location_patterns.items():
        match = re.search(pattern, message.lower())
        if match:
            return match.group()
    return None

def extract_outfit_from_message(message):
    """Extract outfit description from user message."""
    outfit_patterns = {
        r"(wearing|in|with) (a )?(red|black|white|blue|pink|purple)": "\\3",
        r"(dress|skirt|top|outfit|clothes|lingerie|swimsuit)": "\\1",
        r"(casual|formal|sexy|cute|elegant|sporty)": "\\1",
    }
    
    for pattern, replacement in outfit_patterns.items():
        match = re.search(pattern, message.lower())
        if match:
            return match.group()
    return None

def construct_image_prompt(user_message, chat_history, direct_prompt=None):
    """Construct a detailed image prompt based on user message and chat context."""
    base_prompt = "beautiful girl with long brown hair, slim figure, sexy pose, bust showing, boobs"
    
    # If it's a direct generation request, use the provided prompt
    if direct_prompt:
        return f"{base_prompt}, {direct_prompt}, high quality, photorealistic, detailed, natural lighting"
    
    # Extract specific elements from the user message first
    pose = extract_pose_from_message(user_message)
    location = extract_location_from_message(user_message)
    outfit = extract_outfit_from_message(user_message)
    
    # If no specific elements found in user message, analyze recent chat history
    if not any([pose, location, outfit]):
        recent_messages = [msg["content"] for msg in chat_history[-3:] if msg["role"] == "user"]
        for message in recent_messages:
            pose = pose or extract_pose_from_message(message)
            location = location or extract_location_from_message(message)
            outfit = outfit or extract_outfit_from_message(message)
    
    # Construct the prompt with mandatory elements
    prompt_elements = [base_prompt]
    
    # Add location first if specified (to give it more weight in the generation)
    if location:
        if "beach" in location.lower():
            prompt_elements.extend([
                f"at the {location}",
                "beach background",
                "ocean waves",
                "sunny day",
                "beach setting"
            ])
        else:
            prompt_elements.append(f"in {location}")
    
    if pose:
        prompt_elements.append(f"{pose}")
    if outfit:
        if location and "beach" in location.lower() and not any(beach_item in outfit.lower() for beach_item in ["swimsuit", "bikini"]):
            prompt_elements.append("wearing a sexy bikini")
        elif outfit and "red lace dress" not in outfit.lower():
            prompt_elements.append(f"wearing {outfit}")
    
    # Always add quality specifications at the end
    prompt_elements.append("high quality, photorealistic, detailed, natural lighting")
    
    return ", ".join(prompt_elements)

def generate_image_url(prompt):
    """Generate an image using RunPod API and return the URL."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RUNPOD_API_KEY}"
    }
    
    print(f"Generated prompt: {prompt}")
    
    payload = {
        "input": {
            "input_image": "https://firebasestorage.googleapis.com/v0/b/arslan-zalmi.firebasestorage.app/o/demo-images%2Fsample%20(15).png?alt=media&token=a3ecead1-02b3-45d6-9ef5-0728b06b61a0",
            "model": "default",
            "prompt": prompt
        }
    }
    
    with st.spinner('Generating something special for you... 💖'):
        try:
            response = requests.post(RUNPOD_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result.get("status") == "COMPLETED" and result.get("output") and len(result["output"]) > 0:
                return result["output"][0]
            else:
                st.error("Failed to generate image")
                return None
                
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
            return None

def get_mistral_response(messages):
    """Get a response from the Mistral API."""
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Format messages to include role and content properly
    formatted_messages = []
    for msg in messages:
        if msg["role"] != "system":
            formatted_messages.append({
                "role": "user" if msg["role"] == "user" else "assistant",
                "content": msg["content"]
            })
    
    # Always include system message first
    formatted_messages.insert(0, {
        "role": "system",
        "content": SYSTEM_PROMPT
    })
    
    data = {
        "model": "mistral-medium",
        "messages": formatted_messages,
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    try:
        response = requests.post(MISTRAL_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error getting response from Mistral: {str(e)}")
        return "I'm having trouble connecting right now. Can we try again?"

def download_image(image_url):
    """Download image from URL and return as PIL Image object."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        st.error(f"Failed to download image: {str(e)}")
        return None

def main():
    st.title("Chat with Emily 💝")
    
    # Initialize chat history
    initialize_chat_history()
    
    # Display chat messages
    for message in st.session_state.chat_history:
        if message["role"] != "system":  # Don't display system prompt
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if message.get("image_url"):
                    if message["image_url"]:
                        # Download and display image
                        img = download_image(message["image_url"])
                        if img:
                            with st.container():
                                st.image(img, width=300, caption="Click to expand")
                    else:
                        st.error("Sorry, I couldn't generate that image right now.")
    
    # Get user input
    user_message = st.chat_input("Type your message here...")
    
    if user_message:
        with st.chat_message("user"):
            st.write(user_message)
        
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        # Handle first interaction
        if st.session_state.waiting_for_first_response:
            positive_responses = [
                'yes', 'yeah', 'yep', 'yup', 'sure',
                'okay', 'ok', 'k', 'kk',
                'show', 'please', 'pls',
                'absolutely', 'definitely',
                'love to', 'would love',
                'of course', 'hell yes',
                'go ahead', 'do it',
                'cant wait', "can't wait",
                'show me', 'let me see',
                'excited', 'ready',
                'want', 'wanna',
                '😘', '😍', '🥰', '❤️', '💋'
            ]
            
            if any(word in user_message.lower() for word in positive_responses):
                st.session_state.waiting_for_first_response = False
                default_prompt = "beautiful girl with long brown hair, slim figure, sexy pose, bust showing, boobs, high quality, photorealistic, detailed, natural lighting"
                image_url = generate_image_url(default_prompt)
                
                response = "Mmm... I hope you like what you see 💋"
                with st.chat_message("assistant"):
                    st.write(response)
                    if image_url:
                        img = download_image(image_url)
                        if img:
                            with st.container():
                                st.image(img, width=300, caption="Click to expand")
                    else:
                        st.error("Sorry, I couldn't generate that image right now.")
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "image_url": image_url
                })
            else:
                response = get_mistral_response(st.session_state.chat_history)
                with st.chat_message("assistant"):
                    st.write(response)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
        else:
            # Regular chat flow
            is_image_request, direct_prompt = detect_image_request(user_message)
            
            if is_image_request:
                image_prompt = construct_image_prompt(
                    user_message, 
                    st.session_state.chat_history,
                    direct_prompt=direct_prompt
                )
                image_url = generate_image_url(image_prompt)
                
                if direct_prompt:
                    response = "I'll create that for you right away... 💋"
                else:
                    response = "Let me show you something special... just for you 💋"
                
                with st.chat_message("assistant"):
                    st.write(response)
                    if image_url:
                        img = download_image(image_url)
                        if img:
                            with st.container():
                                st.image(img, width=300, caption="Click to expand")
                    else:
                        st.error("Sorry, I couldn't generate that image right now.")
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response,
                    "image_url": image_url
                })
            else:
                response = get_mistral_response(st.session_state.chat_history)
                
                with st.chat_message("assistant"):
                    st.write(response)
                
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
        
        st.session_state.chat_history = trim_chat_history(st.session_state.chat_history)

if __name__ == "__main__":
    main() 
