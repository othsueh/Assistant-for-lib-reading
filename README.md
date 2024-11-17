# Assistant For library reading

A full-stack application featuring a Vue.js frontend and FastAPI backend for interacting with an AI coding assistant powered by Claude 3.5 Sonnet.

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- Anthropic API key

## Installation

### Backend Setup

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up your Anthropic API key:
   - Replace the API key in `.env` with your own key

4. Generate the project structure:
```bash
python code_to_json.py /path/to/your/codebase --output project_structure.json
```

5. Start the backend server:
```bash
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Install frontend dependencies:
```bash
cd chat-assistant-frontend
npm install
```

2. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI server
│   ├── codebase_assistant.py   # AI assistant implementation
│   ├── code_to_json.py         # Code analysis tool
│   └── project_structure.json  # Generated code structure
│
└── chat-assistant-frontend/
    ├── src/
    │   ├── components/
    │   │   └── MessageList.vue # Chat interface
    │   └── stores/
    │       └── chat.js         # State management
    └── package.json
```

## Features

- Real-time chat interface with AI assistant
- Code syntax highlighting
- Expandable thought process sections
- Multiple chat dialogs support
- Server-sent events for streaming responses
- Code analysis and context-aware responses

## Development

### Backend Development

- The backend uses FastAPI for the API server
- Langchain for AI interactions
- FAISS for vector storage and similarity search
- Supports both streaming and non-streaming responses

### Frontend Development

- Built with Vue 3 and Composition API
- Uses Pinia for state management
- Markdown rendering with syntax highlighting
- Responsive design with custom styling

## API Endpoints

- `POST /api/chat` - Send a message (non-streaming)
- `POST /api/chat/stream` - Send a message (streaming)
- `GET /api/dialogs` - Get all chat dialogs
- `POST /api/dialogs/new` - Create a new dialog

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details