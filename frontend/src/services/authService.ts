import { User } from "../types";
import { auth, isFirebaseConfigured } from "../firebase/firebase";
import {
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  reload,
  sendEmailVerification,
  signInWithEmailAndPassword,
  signOut,
  updateProfile,
  type User as FirebaseUser,
} from "firebase/auth";

export interface LoginCredentials {
  email: string;
  password: string;
  name?: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
}

export interface AuthToken {
  token: string;
  refreshToken?: string;
}

export type AuthResponse = {
  success: boolean;
  data?: { user: User; token: string };
  message?: string;
  requiresEmailVerification?: boolean;
  email?: string;
};

const emptyProgress: NonNullable<User["progress"]> = {
  speaking: 0,
  writing: 0,
  reading: 0,
  listening: 0,
  totalTests: 0,
  completedTests: 0,
  averageScore: 0,
  strongAreas: [],
  weakAreas: [],
  createdAt: new Date().toISOString(),
};

const firebaseSetupMessage =
  "Firebase Authentication is not configured. Add the Firebase web app settings to the frontend environment.";

const createUser = (id: string, email: string, name?: string): User => ({
  id,
  email,
  name: name?.trim() || email.split("@")[0],
  role: "user",
  progress: { ...emptyProgress },
});

const getStoredUser = (): User | null => {
  try {
    const stored = localStorage.getItem("user");
    if (!stored) return null;

    const user = JSON.parse(stored) as Partial<User>;
    if (!user.email) return null;

    return {
      ...createUser(user.id || user.email, user.email, user.name),
      avatar: user.avatar,
      progress: user.progress || { ...emptyProgress },
    };
  } catch {
    return null;
  }
};

const saveFirebaseSession = (user: FirebaseUser) => {
  const cachedUser = getStoredUser();
  const name = user.displayName || (cachedUser?.id === user.uid ? cachedUser.name : undefined);
  localStorage.setItem("authProvider", "firebase");
  localStorage.removeItem("authToken");
  localStorage.setItem("user", JSON.stringify(createUser(user.uid, user.email || "", name)));
};

const firebaseErrorMessage = (error: unknown, fallback: string): string => {
  const code = (error as { code?: string } | null)?.code;
  switch (code) {
    case "auth/invalid-email":
      return "Enter a valid email address.";
    case "auth/user-disabled":
      return "This account has been disabled.";
    case "auth/user-not-found":
    case "auth/wrong-password":
    case "auth/invalid-credential":
      return "Invalid email or password.";
    case "auth/email-already-in-use":
      return "An account already exists for this email.";
    case "auth/weak-password":
      return "Choose a stronger password (at least 6 characters).";
    case "auth/too-many-requests":
      return "Too many attempts. Please wait and try again.";
    case "auth/network-request-failed":
      return "Unable to reach the authentication service. Check your connection and try again.";
    default:
      return fallback;
  }
};

export const authService = {
  loginWithFirebase: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    if (!auth || !isFirebaseConfigured) {
      return { success: false, message: firebaseSetupMessage };
    }

    try {
      const credential = await signInWithEmailAndPassword(
        auth,
        credentials.email.trim(),
        credentials.password
      );
      if (!credential.user.emailVerified) {
        await signOut(auth);
        authService.clearSession();
        return {
          success: false,
          requiresEmailVerification: true,
          email: credential.user.email || credentials.email.trim(),
          message: "Verify your email address before signing in. You can resend the verification email below.",
        };
      }

      const token = await credential.user.getIdToken();
      saveFirebaseSession(credential.user);
      return {
        success: true,
        data: {
          user: createUser(
            credential.user.uid,
            credential.user.email || credentials.email,
            credential.user.displayName || credentials.name
          ),
          token,
        },
      };
    } catch (error) {
      return {
        success: false,
        message: firebaseErrorMessage(error, "Login failed. Please try again."),
      };
    }
  },

  registerWithFirebase: async (data: RegisterData): Promise<AuthResponse> => {
    if (!auth || !isFirebaseConfigured) {
      return { success: false, message: firebaseSetupMessage };
    }

    try {
      const credential = await createUserWithEmailAndPassword(
        auth,
        data.email.trim(),
        data.password
      );
      try {
        await updateProfile(credential.user, { displayName: data.name.trim() });
      } catch {
        // Account creation succeeded; keep the entered name in the local profile.
      }
      await sendEmailVerification(credential.user);
      await signOut(auth);
      authService.clearSession();
      return {
        success: true,
        requiresEmailVerification: true,
        email: credential.user.email || data.email.trim(),
        message: "Account created. Check your inbox and verify your email before signing in.",
      };
    } catch (error) {
      return {
        success: false,
        message: firebaseErrorMessage(error, "Registration failed. Please try again."),
      };
    }
  },

  resendVerificationEmail: async (
    email: string,
    password: string
  ): Promise<{ success: boolean; message: string }> => {
    if (!auth || !isFirebaseConfigured) {
      return { success: false, message: firebaseSetupMessage };
    }

    try {
      const credential = await signInWithEmailAndPassword(auth, email.trim(), password);
      if (credential.user.emailVerified) {
        await signOut(auth);
        authService.clearSession();
        return { success: true, message: "Your email is verified. You can sign in now." };
      }

      await sendEmailVerification(credential.user);
      await signOut(auth);
      authService.clearSession();
      return { success: true, message: "Verification email sent. Check your inbox and spam folder." };
    } catch (error) {
      return {
        success: false,
        message: firebaseErrorMessage(error, "Could not send the verification email. Please try again."),
      };
    }
  },

  logout: async (): Promise<void> => {
    if (auth?.currentUser) {
      try {
        await signOut(auth);
      } finally {
        authService.clearSession();
      }
      return;
    }
    authService.clearSession();
  },

  clearSession: () => {
    localStorage.removeItem("authProvider");
    localStorage.removeItem("authToken");
    localStorage.removeItem("user");
  },

  getCurrentUser: (): User | null => {
    return getStoredUser();
  },

  isAuthenticated: (): boolean => {
    return !!auth?.currentUser?.emailVerified;
  },

  // Admin UI stays disabled until the backend exposes verified role claims.
  isAdmin: (): boolean => false,

  initializeAuth: async (): Promise<{ isAuthenticated: boolean; user: User | null }> => {
    const configuredAuth = auth;
    if (configuredAuth) {
      const firebaseUser = configuredAuth.currentUser || await new Promise<FirebaseUser | null>((resolve, reject) => {
        let unsubscribe: (() => void) | undefined;
        unsubscribe = onAuthStateChanged(
          configuredAuth,
          (user) => {
            unsubscribe?.();
            resolve(user);
          },
          (error) => {
            unsubscribe?.();
            reject(error);
          }
        );
      });

      if (firebaseUser) {
        await reload(firebaseUser);
        if (!firebaseUser.emailVerified) {
          await signOut(configuredAuth);
          authService.clearSession();
          return { isAuthenticated: false, user: null };
        }
        saveFirebaseSession(firebaseUser);
        return { isAuthenticated: true, user: authService.getCurrentUser() };
      }

      authService.clearSession();
    }

    return { isAuthenticated: false, user: null };
  },
};
