# Emily AI Chat Assistant 💝

An interactive AI chat assistant that combines natural language conversation with dynamic image generation capabilities. Emily is designed to be engaging, personable, and can generate contextually appropriate images during conversations.

## Features

- **Natural Conversation**: Powered by Mistral AI for human-like interactions
- **Dynamic Image Generation**: Creates contextual images based on conversation
- **Interactive UI**: Built with Streamlit for a smooth user experience
- **Adaptive Responses**: Maintains context and personality throughout conversations
- **Click-to-Expand Images**: Thumbnail views that expand to full size on click
- **Smart Context Handling**: Remembers conversation history for coherent dialogue
- **Location-Aware Imaging**: Generates images that match mentioned locations and settings

## Prerequisites

- Python 3.8+
- Mistral AI API key
- Stable Diffusion API access

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
Create a `.env` file in the project root with:
```
MISTRAL_API_KEY=your_mistral_api_key
STABLE_DIFFUSION_API_KEY=your_stable_diffusion_api_key
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run chat_emily.py
```

2. Access the application in your web browser (typically at `http://localhost:8501`)

3. Start chatting with Emily! You can:
   - Have natural conversations
   - Request images by describing what you'd like to see
   - Click on generated images to view them in full size

## Project Structure

```
storage/demo/
├── chat_emily.py        # Main application file
├── requirements.txt     # Project dependencies
├── .env                # Environment variables (not in repo)
└── .gitignore         # Git ignore rules
```

## Key Components

### Chat Interface
- Built with Streamlit's chat components
- Maintains conversation history
- Displays both text and images in a cohesive interface

### Image Generation
- Dynamic prompt construction based on conversation context
- Location-aware image generation
- Supports various scenarios and settings
- Thumbnail preview with click-to-expand functionality

### Response Processing
- Context-aware responses using Mistral AI
- Personality consistency throughout conversations
- Natural language understanding and generation

## Security Notes

- API keys and credentials should be stored in `.env` file
- Never commit sensitive information to the repository
- Use environment variables for all sensitive data

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[Your chosen license]

## Acknowledgments

- Mistral AI for the chat capabilities
- Stable Diffusion for image generation
- Streamlit for the user interface framework 