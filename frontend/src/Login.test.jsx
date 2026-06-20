import { render, screen } from "@testing-library/react";
import Login from "../pages/Login";

test("renders login page", () => {
  render(<Login />);

  expect(
    screen.getByText(/login/i)
  ).toBeInTheDocument();
});