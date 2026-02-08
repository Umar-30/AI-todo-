// JWT Authentication service using backend API

const TOKEN_KEY = 'auth_token';
const USER_KEY = 'auth_user';
const SESSION_KEY = 'todo-ai-chatbot-session';

interface User {
  id: string;
  email: string;
  name?: string;
  emailVerified: boolean;
}

interface Session {
  user: User;
  expiresAt: string;
}

interface AuthResponse {
  success: boolean;
  user?: User;
  session?: Session;
  error?: string;
}

// Get stored JWT token
export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

// Get stored user
const getStoredUser = (): User | null => {
  const userStr = localStorage.getItem(USER_KEY);
  if (userStr) {
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }
  return null;
};

// Store auth data
const storeAuth = (token: string, user: User) => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

// Clear auth data
const clearAuth = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(SESSION_KEY);
};

export const signIn = async (email: string, password: string): Promise<AuthResponse> => {
  try {
    const response = await fetch(`/auth/login?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      return {
        success: false,
        error: data.detail || 'Login failed'
      };
    }

    const user: User = {
      id: data.user.id,
      email: data.user.email,
      name: data.user.name,
      emailVerified: true
    };

    // Clear previous user's chat session before storing new auth
    localStorage.removeItem(SESSION_KEY);
    storeAuth(data.access_token, user);

    return {
      success: true,
      user,
      session: {
        user,
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
      }
    };
  } catch (error) {
    return {
      success: false,
      error: 'Network error'
    };
  }
};

export const signUp = async (email: string, password: string, name: string): Promise<AuthResponse> => {
  try {
    const response = await fetch(`/auth/signup?email=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}&name=${encodeURIComponent(name)}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();

    if (!response.ok || !data.success) {
      return {
        success: false,
        error: data.detail || 'Signup failed'
      };
    }

    const user: User = {
      id: data.user.id,
      email: data.user.email,
      name: data.user.name,
      emailVerified: false
    };

    storeAuth(data.access_token, user);

    return {
      success: true,
      user,
      session: {
        user,
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
      }
    };
  } catch (error) {
    return {
      success: false,
      error: 'Network error'
    };
  }
};

export const signOut = async (): Promise<AuthResponse> => {
  clearAuth();
  return { success: true };
};

// Hook for session state
export const useSession = () => {
  const token = getToken();
  const user = getStoredUser();

  if (token && user) {
    return {
      data: {
        user,
        expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
      },
      isLoading: false,
    };
  }

  return {
    data: null,
    isLoading: false,
  };
};