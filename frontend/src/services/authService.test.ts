// declare const jest: any;
// declare const test: (name: string, callback: () => unknown) => void;
// declare const expect: any;
// declare const beforeEach: (callback: () => void) => void;

// import { auth } from "../firebase/firebase";
// import {
//   createUserWithEmailAndPassword,
//   signInWithEmailAndPassword,
//   updateProfile,
// } from "firebase/auth";
// import { api } from "./api";
// import { authService } from "./authService";

// jest.mock("../firebase/firebase", () => ({
//   auth: { currentUser: null },
//   isFirebaseConfigured: true,
// }));

// jest.mock("firebase/auth", () => ({
//   createUserWithEmailAndPassword: jest.fn(),
//   onAuthStateChanged: jest.fn(),
//   signInWithEmailAndPassword: jest.fn(),
//   signOut: jest.fn(),
//   updateProfile: jest.fn(),
// }));

// jest.mock("./api", () => ({
//   api: { post: jest.fn() },
// }));

// const mockAuth = auth as unknown as { currentUser: unknown };
// const mockSignIn = signInWithEmailAndPassword as any;
// const mockCreateUser = createUserWithEmailAndPassword as any;
// const mockUpdateProfile = updateProfile as any;
// const mockPost = api.post as any;

// const firebaseUser = {
//   uid: "firebase-user-123",
//   email: "learner@example.test",
//   displayName: "",
//   getIdToken: jest.fn().mockResolvedValue("firebase-id-token"),
// };

// beforeEach(() => {
//   localStorage.clear();
//   mockAuth.currentUser = null;
//   jest.clearAllMocks();
//   firebaseUser.getIdToken.mockResolvedValue("firebase-id-token");
// });

// test("Firebase login stores a user session and gives the user no client-side role", async () => {
//   mockSignIn.mockResolvedValue({ user: firebaseUser });

//   const result = await authService.loginWithFirebase({
//     email: "learner@example.test",
//     password: "valid-password",
//   });

//   expect(result.success).toBe(true);
//   expect(result.data?.token).toBe("firebase-id-token");
//   expect(result.data?.user.role).toBe("user");
//   expect(localStorage.getItem("authProvider")).toBe("firebase");
//   expect(localStorage.getItem("authToken")).toBeNull();
// });

// test("Firebase registration uses the entered display name and never submits a role", async () => {
//   mockCreateUser.mockResolvedValue({ user: firebaseUser });
//   mockUpdateProfile.mockResolvedValue(undefined);

//   const result = await authService.registerWithFirebase({
//     name: "Learner",
//     email: "learner@example.test",
//     password: "strong-password",
//   });

//   expect(mockCreateUser).toHaveBeenCalledWith(auth, "learner@example.test", "strong-password");
//   expect(mockUpdateProfile).toHaveBeenCalledWith(firebaseUser, { displayName: "Learner" });
//   expect(result.success).toBe(true);
//   expect(result.data?.user.role).toBe("user");
//   expect(mockPost).not.toHaveBeenCalled();
// });

// test("legacy database accounts can still sign in during migration", async () => {
//   mockSignIn.mockRejectedValue({ code: "auth/invalid-credential" });
//   mockPost.mockResolvedValue({
//     success: true,
//     data: {
//       user: { id: 7, email: "learner@example.test", full_name: "Learner", role: "admin" },
//       access_token: "legacy-token",
//     },
//   });

//   const result = await authService.loginWithFirebase({
//     email: "learner@example.test",
//     password: "legacy-password",
//   });

//   expect(result.success).toBe(true);
//   expect(result.data?.token).toBe("legacy-token");
//   expect(result.data?.user.role).toBe("user");
//   expect(localStorage.getItem("authProvider")).toBe("legacy");
// });

declare global {
	const jest: any;
}
declare const test: (name: string, callback: () => unknown) => void;
declare const expect: any;
declare const beforeEach: (callback: () => void) => void;

import { auth } from "../firebase/firebase";
import {
	createUserWithEmailAndPassword,
	onAuthStateChanged,
	reload,
	sendEmailVerification,
	signInWithEmailAndPassword,
	signOut,
	updateProfile,
} from "firebase/auth";
import { authService } from "./authService";

jest.mock("../firebase/firebase", () => ({
	auth: { currentUser: null },
	isFirebaseConfigured: true,
}));

jest.mock("firebase/auth", () => ({
	createUserWithEmailAndPassword: jest.fn(),
	onAuthStateChanged: jest.fn(),
	reload: jest.fn(),
	sendEmailVerification: jest.fn(),
	signInWithEmailAndPassword: jest.fn(),
	signOut: jest.fn(),
	updateProfile: jest.fn(),
}));

const mockAuth = auth as unknown as { currentUser: unknown };
const mockCreateUser = createUserWithEmailAndPassword as any;
const mockSignIn = signInWithEmailAndPassword as any;
const mockSendVerification = sendEmailVerification as any;
const mockSignOut = signOut as any;

const mockFirebaseUser = (emailVerified: boolean) => ({
	uid: "firebase-user-123",
	email: "learner@example.test",
	displayName: "Learner",
	emailVerified,
	getIdToken: jest.fn().mockResolvedValue("firebase-id-token"),
});

beforeEach(() => {
	localStorage.clear();
	mockAuth.currentUser = null;
	jest.clearAllMocks();
});

test("registration sends a verification email and does not create an app session", async () => {
	const user = mockFirebaseUser(false);
	mockCreateUser.mockResolvedValue({ user });

	const result = await authService.registerWithFirebase({
		name: "Learner",
		email: "learner@example.test",
		password: "correct-horse-battery",
	});

	expect(sendEmailVerification).toHaveBeenCalledWith(user);
	expect(mockSignOut).toHaveBeenCalledWith(auth);
	expect(result.requiresEmailVerification).toBe(true);
	expect(result.success).toBe(true);
	expect(localStorage.getItem("authToken")).toBeNull();
	expect(localStorage.getItem("user")).toBeNull();
});

test("unverified Firebase login is rejected and signs the user out", async () => {
	mockSignIn.mockResolvedValue({ user: mockFirebaseUser(false) });

	const result = await authService.loginWithFirebase({
		email: "learner@example.test",
		password: "correct-horse-battery",
	});

	expect(result.requiresEmailVerification).toBe(true);
	expect(result.success).toBe(false);
	expect(mockSignOut).toHaveBeenCalledWith(auth);
	expect(localStorage.getItem("user")).toBeNull();
});

test("verified Firebase login stores a learner session", async () => {
	mockSignIn.mockResolvedValue({ user: mockFirebaseUser(true) });

	const result = await authService.loginWithFirebase({
		email: "learner@example.test",
		password: "correct-horse-battery",
	});

	expect(result.success).toBe(true);
	expect(result.data?.user.role).toBe("user");
	expect(localStorage.getItem("authProvider")).toBe("firebase");
});

test("resend sends a new verification email for an unverified user", async () => {
	const user = mockFirebaseUser(false);
	mockSignIn.mockResolvedValue({ user });

	const result = await authService.resendVerificationEmail(
		"learner@example.test",
		"correct-horse-battery"
	);

	expect(mockSendVerification).toHaveBeenCalledWith(user);
	expect(result.success).toBe(true);
	expect(mockSignOut).toHaveBeenCalledWith(auth);
});

