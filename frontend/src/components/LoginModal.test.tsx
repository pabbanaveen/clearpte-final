declare const jest: any;
declare const test: (name: string, callback: () => unknown) => void;
declare const expect: any;

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import LoginModal from "./LoginModal";

test("shows authentication failures in the login dialog", async () => {
  const onLogin = jest.fn().mockRejectedValue(new Error("Invalid email or password."));

  render(
    <LoginModal
      open
      onClose={jest.fn()}
      onLogin={onLogin}
      onRegister={jest.fn().mockResolvedValue(undefined)}
      selectedMode="login"
    />
  );

  fireEvent.change(screen.getByLabelText(/email address/i), {
    target: { value: "learner@example.test" },
  });
  fireEvent.change(screen.getByLabelText(/password/i), {
    target: { value: "bad-password" },
  });
  fireEvent.click(screen.getByRole("button", { name: "Login" }));

  await waitFor(() => {
    expect(screen.getByText("Invalid email or password.")).toBeInTheDocument();
  });
});
