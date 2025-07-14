# Semantic Kernel MCP Client

A web-based client application that uses **Semantic Kernel** and **Azure OpenAI** to provide an intelligent interface for the ticketing system via the **Model Context Protocol (MCP)**.

## 🎯 Features

- **Natural Language Interface**: Ask questions about tickets in plain English
- **Semantic Kernel Integration**: Powered by Microsoft Semantic Kernel framework
- **Azure OpenAI**: Uses GPT-3.5-Turbo for intelligent responses
- **MCP Protocol**: Connects to the ticketing API via Model Context Protocol
- **Modern Web UI**: Beautiful, responsive interface built with Bootstrap
- **Real-time Chat**: Interactive chat interface with quick actions
- **Function Calling**: AI can automatically call ticketing functions based on user requests

## 🔧 Setup

### Prerequisites

1. **Python 3.10+**
2. **Azure OpenAI Service** with GPT-3.5-Turbo deployment
3. **Running MCP Server** (the ticketing API from the parent directory)

### Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure Azure OpenAI**:
   - Copy `.env.example` to `.env`
   - Fill in your Azure OpenAI credentials:
   
```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
```

3. **Start the MCP Server** (in parent directory):
```bash
cd ..
python -m uvicorn app.main:app --reload --port 8000
```

4. **Test the client**:
```bash
python test_client.py
```

5. **Start the client**:
```bash
python main.py
```

6. **Open your browser** to http://localhost:8001

## 🎮 Usage

### Natural Language Queries

The AI assistant understands natural language and can help with:

- **Search tickets**: "Find all high priority tickets" or "Show me tickets about email problems"
- **Create tickets**: "Create a ticket for server downtime in the data center"
- **Get ticket details**: "What's the status of ticket #123?"
- **Update tickets**: "Mark ticket #456 as resolved"
- **Analytics**: "Show me ticket statistics" or "What are the most common issues?"
- **Resolution suggestions**: "How can I fix the issue in ticket #789?"

### Quick Actions

The interface provides quick action buttons for common tasks:
- 📋 List Open Tickets
- 📊 Show Analytics  
- 🔥 High Priority Tickets
- 🔍 Network Issues
- ➕ Create Ticket

### Example Conversations

**User**: "Find tickets about server performance"
**AI**: Found 2 tickets matching 'server performance':
🎫 Ticket #1: Server performance issue
   Priority: high | Status: open
   Description: The main application server is running slowly...
   Reporter: john.doe@company.com

**User**: "Create a ticket for email server down"
**AI**: ✅ Created ticket #9: Email server down
Status: open
Priority: high

## 🧠 How It Works

### Architecture

```
Web Browser → FastAPI Client → Semantic Kernel → Azure OpenAI
                    ↓
              MCP Client → MCP Server (Ticketing API)
```

### Semantic Kernel Integration

1. **Plugin System**: MCP tools are exposed as Semantic Kernel functions
2. **Function Calling**: AI automatically calls appropriate functions based on user intent
3. **Context Management**: Conversation history is maintained across interactions
4. **Error Handling**: Graceful handling of API errors and timeouts

### MCP Functions Available

- `search_tickets`: Semantic search across all tickets
- `create_ticket`: Create new support tickets
- `get_ticket`: Retrieve specific ticket details
- `list_tickets`: List tickets with filtering
- `update_ticket`: Modify existing tickets
- `get_analytics`: Get ticket statistics and insights
- `suggest_resolution`: AI-powered resolution suggestions

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_ENDPOINT` | Your Azure OpenAI endpoint | Yes |
| `AZURE_OPENAI_API_KEY` | API key for authentication | Yes |
| `AZURE_OPENAI_DEPLOYMENT_NAME` | Name of your GPT model deployment | Yes |
| `MCP_SERVER_URL` | URL of the MCP ticketing server | No (default: http://127.0.0.1:8000) |
| `PORT` | Port for the client web server | No (default: 8001) |

### Azure OpenAI Setup

1. Create an Azure OpenAI resource
2. Deploy a GPT-3.5-Turbo model
3. Get your endpoint and API key
4. Update the `.env` file

## 🐛 Troubleshooting

### Common Issues

1. **"Semantic Kernel not available"**
   - Run: `pip install semantic-kernel`
   - Check that all requirements are installed

2. **"MCP Server disconnected"**
   - Ensure the ticketing API is running on port 8000
   - Check the MCP_SERVER_URL setting

3. **"AI Service not ready"**
   - Verify your Azure OpenAI credentials
   - Check that your deployment name is correct
   - Ensure you have quota available

4. **Import errors**
   - Run: `pip install -r requirements.txt`
   - Check Python version (3.10+ required)

### Debug Mode

Enable debug mode in `.env`:
```env
DEBUG=true
```

This will:
- Show detailed error messages
- Enable API documentation at `/docs`
- Provide verbose logging

## 🔍 API Endpoints

- `GET /` - Web interface
- `POST /chat` - Send chat messages
- `GET /status` - Service status
- `GET /tools` - Available MCP tools
- `POST /reset` - Reset conversation
- `GET /health` - Health check

## 🎨 Customization

### Styling

The web interface uses Bootstrap 5 and custom CSS. You can modify the appearance by editing `templates/index.html`.

### AI Behavior

Modify the system message in `semantic_agent.py` to change how the AI responds:

```python
def _get_system_message(self) -> str:
    return """You are a helpful IT support assistant..."""
```

## 📈 Monitoring

The client provides status indicators for:
- MCP Server connection
- Semantic Kernel initialization
- Azure OpenAI service

Check `/health` endpoint for programmatic monitoring.

## 🔒 Security

- Never commit API keys to version control
- Use Azure Key Vault for production deployments
- Enable managed identity when possible
- Configure CORS appropriately for production

## 📄 License

This project is part of the RAG-based MCP Ticketing System demonstration.
