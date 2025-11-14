# 🎨 Frontend Setup Guide - Local AI Agent

This guide walks you through setting up the React frontend for the Local AI Agent.

## 🎯 Overview

The frontend is a clean, modern React application that provides:
- Chat interface for interacting with the AI agent
- Markdown rendering for formatted responses
- Secure Bearer token authentication
- Real-time response streaming
- Clean, responsive UI

## 🚀 Quick Setup

### Option 1: Using Create React App (Recommended for Beginners)

```bash
# Navigate to your project root
cd /home/user/Jynco/local-ai-agent

# Create React app with TypeScript
npx create-react-app frontend --template typescript

# Navigate into frontend directory
cd frontend

# Install additional dependencies
npm install react-markdown
```

### Option 2: Using Vite (Faster, Modern Alternative)

```bash
# Create Vite project
npm create vite@latest frontend -- --template react-ts

# Navigate and install
cd frontend
npm install
npm install react-markdown
```

## 🔑 Configure Frontend Environment

Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_AGENT_API_KEY=your_backend_secret_token_here
```

**IMPORTANT**: This must match the `AGENT_SECRET_TOKEN` from your backend's `.env` file!

### For Vite users:

Create `.env` with Vite-compatible variable names:

```env
VITE_AGENT_API_KEY=your_backend_secret_token_here
```

## 📝 Create API Client

Create `frontend/src/api.ts`:

```typescript
// frontend/src/api.ts
const AGENT_API_KEY = process.env.REACT_APP_AGENT_API_KEY; // For Create React App
// const AGENT_API_KEY = import.meta.env.VITE_AGENT_API_KEY; // For Vite

const API_BASE_URL = "http://localhost:8000";

export async function sendChatMessage(prompt: string): Promise<string> {
  if (!AGENT_API_KEY) {
    throw new Error("REACT_APP_AGENT_API_KEY is not set. Check your .env file.");
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${AGENT_API_KEY}`,
      },
      body: JSON.stringify({ prompt }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.detail || `Server error: ${response.status} ${response.statusText}`
      );
    }

    const data = await response.json();
    return data.response;
  } catch (error: any) {
    console.error("Failed to send chat message:", error);
    throw new Error(
      `Could not connect to the local agent: ${error.message}. Is the backend running?`
    );
  }
}
```

## 💬 Create Chat Component

Create `frontend/src/Chat.tsx`:

```typescript
// frontend/src/Chat.tsx
import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import './Chat.css';
import { sendChatMessage } from './api';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const assistantResponse = await sendChatMessage(input);
      const assistantMessage: Message = {
        role: 'assistant',
        content: assistantResponse,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `❌ Error: ${error.message}`,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="message-list">
        {messages.length === 0 && (
          <div className="welcome-message">
            <h2>👋 Welcome to your Local AI Agent</h2>
            <p>Ask me to:</p>
            <ul>
              <li>Check Git repository status</li>
              <li>Manage Docker containers</li>
              <li>Explore your file system</li>
              <li>Automate development tasks</li>
            </ul>
          </div>
        )}
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-header">
              {msg.role === 'user' ? '👤 You' : '🤖 Agent'}
            </div>
            <div className="message-content">
              {msg.role === 'user' ? (
                <p>{msg.content}</p>
              ) : (
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant loading">
            <div className="message-header">🤖 Agent</div>
            <div className="message-content">
              <p>Thinking...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-area">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your command or question..."
          disabled={isLoading}
          rows={3}
        />
        <button onClick={handleSend} disabled={isLoading || !input.trim()}>
          {isLoading ? '⏳ Sending...' : '🚀 Send'}
        </button>
      </div>
    </div>
  );
}
```

## 🎨 Add Styling

Create `frontend/src/Chat.css`:

```css
/* frontend/src/Chat.css */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 900px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.message-list {
  flex-grow: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: #f5f7fa;
}

.welcome-message {
  background: white;
  border-radius: 12px;
  padding: 30px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.welcome-message h2 {
  color: #667eea;
  margin-bottom: 20px;
}

.welcome-message ul {
  text-align: left;
  max-width: 400px;
  margin: 20px auto;
  list-style: none;
  padding: 0;
}

.welcome-message li {
  padding: 8px 0;
  padding-left: 25px;
  position: relative;
}

.welcome-message li:before {
  content: "✓";
  position: absolute;
  left: 0;
  color: #667eea;
  font-weight: bold;
}

.message {
  margin-bottom: 16px;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-header {
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 6px;
  color: #4a5568;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  max-width: 80%;
  word-wrap: break-word;
}

.message.user .message-header {
  text-align: right;
  color: #667eea;
}

.message.user .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-left: auto;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
}

.message.assistant .message-content {
  background-color: white;
  color: #2d3748;
  margin-right: auto;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.message.assistant .message-content code {
  background-color: #f7fafc;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.message.assistant .message-content pre {
  background-color: #2d3748;
  color: #f7fafc;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
}

.message.assistant.loading .message-content p {
  animation: blink 1.5s infinite;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.input-area {
  display: flex;
  gap: 12px;
  padding: 20px;
  background-color: white;
  border-top: 2px solid #e2e8f0;
}

.input-area textarea {
  flex-grow: 1;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  font-size: 15px;
  font-family: inherit;
  resize: none;
  transition: border-color 0.2s;
}

.input-area textarea:focus {
  outline: none;
  border-color: #667eea;
}

.input-area button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  cursor: pointer;
  font-size: 15px;
  font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s;
  white-space: nowrap;
}

.input-area button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.input-area button:disabled {
  background: #cbd5e0;
  cursor: not-allowed;
  transform: none;
}

/* Scrollbar styling */
.message-list::-webkit-scrollbar {
  width: 8px;
}

.message-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.message-list::-webkit-scrollbar-thumb {
  background: #667eea;
  border-radius: 4px;
}

.message-list::-webkit-scrollbar-thumb:hover {
  background: #764ba2;
}
```

## 🎯 Update App Component

Update `frontend/src/App.tsx`:

```typescript
// frontend/src/App.tsx
import React from 'react';
import { Chat } from './Chat';
import './App.css';

function App() {
  return (
    <div className="App">
      <Chat />
    </div>
  );
}

export default App;
```

Update `frontend/src/App.css`:

```css
/* frontend/src/App.css */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.App {
  height: 100vh;
}
```

## 🚀 Run the Frontend

### For Create React App:

```bash
cd frontend
npm start
```

The frontend will open at http://localhost:3000

### For Vite:

```bash
cd frontend
npm run dev
```

The frontend will open at http://localhost:5173 (you'll need to update CORS settings in backend)

## ✅ Verification Checklist

- [ ] Backend is running on http://localhost:8000
- [ ] Frontend is running on http://localhost:3000
- [ ] `.env` file exists in frontend with correct `REACT_APP_AGENT_API_KEY`
- [ ] Token in frontend `.env` matches backend `AGENT_SECRET_TOKEN`
- [ ] CORS whitelist in backend includes your frontend URL
- [ ] No console errors in browser developer tools

## 🧪 Test the Integration

### 1. Open Browser Developer Tools (F12)

Check for:
- No CORS errors
- No authentication errors
- Network requests showing 200 status codes

### 2. Try These Test Prompts:

```
Hello!
```
Expected: Friendly greeting from Gemini

```
What's the status of my Git repositories?
```
Expected: List of repos with their Git status

```
List my Docker containers
```
Expected: List of all Docker containers

```
Show me what's in my project directory
```
Expected: Directory listing

## 🔧 Troubleshooting

### CORS Errors

**Problem**: Browser console shows CORS policy errors

**Solution**:
1. Verify frontend URL matches CORS whitelist in `main.py`
2. If using Vite (port 5173), add to whitelist:
   ```python
   origins = [
       "http://localhost:3000",
       "http://localhost:5173",  # Add this for Vite
       "http://127.0.0.1:3000",
       "http://127.0.0.1:5173",  # Add this too
   ]
   ```
3. Restart backend after changes

### 401 Unauthorized Errors

**Problem**: API calls return 401 status

**Solution**:
1. Verify `REACT_APP_AGENT_API_KEY` is set in frontend `.env`
2. Ensure it matches backend `AGENT_SECRET_TOKEN`
3. Restart frontend after `.env` changes

### "Cannot connect to local agent" Error

**Problem**: Frontend can't reach backend

**Solution**:
1. Check backend is running: `curl http://localhost:8000/`
2. Verify API_BASE_URL in `api.ts` is correct
3. Check firewall isn't blocking localhost:8000

### React Environment Variable Not Loading

**Problem**: `process.env.REACT_APP_AGENT_API_KEY` is undefined

**Solution**:
1. Ensure variable name starts with `REACT_APP_` (for CRA)
2. Or use `VITE_` prefix (for Vite) and access via `import.meta.env.VITE_*`
3. Restart dev server after creating/modifying `.env`
4. Never commit `.env` to git!

## 📦 Build for Production

### Create React App:

```bash
npm run build
```

Serves static files from `build/` directory

### Vite:

```bash
npm run build
npm run preview  # Preview production build
```

Serves static files from `dist/` directory

### Serve with Python (Simple Option):

```bash
cd build  # or dist for Vite
python -m http.server 3000
```

## 🎨 Customization Ideas

- Add dark mode toggle
- Implement chat history persistence (localStorage)
- Add voice input/output
- Create keyboard shortcuts
- Add file upload capability
- Implement chat export functionality
- Add system notifications
- Create mobile-responsive design
- Add typing indicators
- Implement chat sessions/contexts

## 📚 Next Steps

1. Customize the UI to match your preferences
2. Add more interactive elements
3. Implement additional features
4. Deploy to production
5. Add analytics and monitoring

---

**Your Local AI Agent is now complete!** 🎉

Start chatting and watch your agent automate your development workflow!
