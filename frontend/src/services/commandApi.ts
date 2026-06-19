export interface CommandRequest {
  text: string;
  session_id: string;
  context: {
    grade_level: number;
    subject: string;
  };
  source_mode: boolean;
  hands_free_mode: boolean;
}

export interface CommandResponse {
  status: 'success' | 'error';
  data?: any; // Define a more specific type based on the actual API contract
  error?: { message: string };
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Sends a command to the backend API.
 * @param request The command request payload.
 * @returns The backend's response.
 */
export const sendCommand = async (request: CommandRequest): Promise<CommandResponse> => {
  try {
    const res = await fetch(`${API_URL}/command/text`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ message: 'Unknown server error' }));
      throw new Error(errorData.error?.message || `HTTP error! status: ${res.status}`);
    }

    return await res.json();
  } catch (error: any) {
    console.error("Error sending command:", error);
    return {
      status: 'error',
      error: {
        message: error.message || 'A network error occurred.',
      },
    };
  }
};
