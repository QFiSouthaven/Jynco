// frontend/src/api.ts
const AGENT_API_KEY = process.env.REACT_APP_AGENT_API_KEY;
const API_BASE_URL = "http://localhost:8000"; // FastAPI server URL

export async function sendChatMessage(prompt: string): Promise<string> {
  if (!AGENT_API_KEY) {
    throw new Error("REACT_APP_AGENT_API_KEY is not set. Check your .env file.");
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${AGENT_API_KEY}` // CRITICAL SECURITY
      },
      body: JSON.stringify({ prompt: prompt })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Server error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    return data.response; // This is the final, natural-language string

  } catch (error: any) {
    console.error("Failed to send chat message:", error);
    throw new Error(`Could not connect to the local agent or API error: ${error.message}. Is the backend running?`);
  }
}
