import { useState, useEffect } from 'react';
import { useSession } from '../services/authService';

export interface AuthState {
  isAuthenticated: boolean;
  user: UserProfile | null;
  isLoading: boolean;
  error: string | null;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string | null;
  emailVerified: boolean;
}

export const useAuth = (): AuthState => {
  const { data: session, isLoading } = useSession();
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    user: null,
    isLoading: true,
    error: null
  });

  useEffect(() => {
    if (isLoading) {
      setAuthState(prev => ({ ...prev, isLoading: true }));
      return;
    }

    if (session?.user) {
      setAuthState({
        isAuthenticated: true,
        user: {
          id: session.user.id,
          email: session.user.email,
          name: session.user.name || null,
          emailVerified: session.user.emailVerified || false
        },
        isLoading: false,
        error: null
      });
    } else {
      setAuthState({
        isAuthenticated: false,
        user: null,
        isLoading: false,
        error: null
      });
    }
  }, [session, isLoading]);

  return authState;
};