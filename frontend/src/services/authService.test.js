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

// const mockAuth = auth;
// const mockSignIn = signInWithEmailAndPassword;
// const mockCreateUser = createUserWithEmailAndPassword;
// const mockUpdateProfile = updateProfile;
// const mockPost = api.post;

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
//   expect(result.data.token).toBe("firebase-id-token");
//   expect(result.data.user.role).toBe("user");
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
//   expect(result.data.user.role).toBe("user");
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
//   expect(result.data.token).toBe("legacy-token");
//   expect(result.data.user.role).toBe("user");
//   expect(localStorage.getItem("authProvider")).toBe("legacy");
// });
