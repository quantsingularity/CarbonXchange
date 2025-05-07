import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react-native";
import { Provider } from "react-redux";
import { NavigationContainer } from "@react-navigation/native";
import configureStore from "redux-mock-store";
import thunk from "redux-thunk";
import TradingScreen from "../../../screens/Main/TradingScreen";
import * as api from "../../../services/api"; // To mock API calls

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

// Mock navigation
const mockNavigation = { navigate: jest.fn(), goBack: jest.fn() };
const mockRoute = {
  params: {
    creditId: "credit123",
    creditName: "Test Credit",
    availableTons: 100,
    pricePerTon: 25,
  },
};

// Mock API service
jest.mock("../../../services/api", () => ({
  createTrade: jest.fn(),
  getWalletBalance: jest.fn(), // Assuming wallet balance is fetched
}));

describe("TradingScreen", () => {
  let store;
  const initialState = {
    auth: { user: { id: "user123" }, token: "test-token", isLoggedIn: true },
    // Mock wallet state if the screen uses it directly from Redux
    // wallet: { balance: 5000, isLoading: false, error: null }
  };

  beforeEach(() => {
    store = mockStore(initialState);
    api.createTrade.mockClear();
    api.getWalletBalance.mockClear().mockResolvedValue({ success: true, balance: { amount: 5000, currency: "USD" } });
    mockNavigation.navigate.mockClear();
    mockNavigation.goBack.mockClear();
  });

  const renderComponent = (currentStore = store, route = mockRoute) => {
    return render(
      <Provider store={currentStore}>
        <NavigationContainer>
          <TradingScreen navigation={mockNavigation} route={route} />
        </NavigationContainer>
      </Provider>
    );
  };

  it("renders correctly with credit details and form elements", async () => {
    const { getByText, getByPlaceholderText } = renderComponent();

    await waitFor(() => expect(api.getWalletBalance).toHaveBeenCalled());

    expect(getByText("Trading: Test Credit")).toBeTruthy();
    expect(getByText("Available: 100 Tons")).toBeTruthy();
    expect(getByText("Price: $25.00 / Ton")).toBeTruthy();
    expect(getByText("Your Balance: $5,000.00")).toBeTruthy(); // Assuming balance is fetched and displayed

    expect(getByPlaceholderText("Quantity (Tons)")).toBeTruthy();
    expect(getByText("BUY")).toBeTruthy();
    expect(getByText("SELL")).toBeTruthy();
  });

  it("allows inputting quantity", async () => {
    const { getByPlaceholderText } = renderComponent();
    await waitFor(() => expect(api.getWalletBalance).toHaveBeenCalled());

    const quantityInput = getByPlaceholderText("Quantity (Tons)");
    fireEvent.changeText(quantityInput, "10");
    expect(quantityInput.props.value).toBe("10");
  });

  it("calculates total cost correctly when quantity changes for BUY", async () => {
    const { getByPlaceholderText, getByText } = renderComponent();
    await waitFor(() => expect(api.getWalletBalance).toHaveBeenCalled());

    fireEvent.press(getByText("BUY")); // Select BUY mode
    const quantityInput = getByPlaceholderText("Quantity (Tons)");
    fireEvent.changeText(quantityInput, "5");
    expect(getByText("Total Cost: $125.00")).toBeTruthy();
  });

  it("calculates total proceeds correctly when quantity changes for SELL", async () => {
    const { getByPlaceholderText, getByText } = renderComponent();
    await waitFor(() => expect(api.getWalletBalance).toHaveBeenCalled());

    fireEvent.press(getByText("SELL")); // Select SELL mode
    const quantityInput = getByPlaceholderText("Quantity (Tons)");
    fireEvent.changeText(quantityInput, "3");
    expect(getByText("Total Proceeds: $75.00")).toBeTruthy();
  });

  it("calls createTrade with correct payload on BUY and navigates on success", async () => {
    api.createTrade.mockResolvedValue({ success: true, trade: { id: "tradeSuccess" } });
    const { getByPlaceholderText, getByText } = renderComponent();
    await waitFor(() => expect(api.getWalletBalance).toHaveBeenCalled());

    fireEvent.press(getByText("BUY"));
    fireEvent.changeText(getByPlaceholderText("Quantity (Tons)"), "10");
    fireEvent.press(getByText("Confirm BUY")); // Assuming button text changes based on mode

    await waitFor(() => {
      expect(api.createTrade).toHaveBeenCalledWith({
        creditId: "credit123",
        quantity: 10,
        pricePerTon: 25,
        type: "buy",
      });
    });
    expect(mockNavigation.goBack).toHaveBeenCalledTimes(1);
    // Optionally, check for a success alert or toast message if implemented
  });

  it("calls createTrade with correct payload on SELL and navigates on success", async () => {
    api.createTrade.mockResolvedValue({ success: true, trade: { id: "tradeSuccess" } });
    const { getByPlaceholderText, getByText } = renderComponent();
    await waitFor(() => expect(api.getWalletBalance).toHaveBeenCalled());

    fireEvent.press(getByText("SELL"));
    fireEvent.changeText(getByPlaceholderText("Quantity (Tons)"), "5");
    fireEvent.press(getByText("Confirm SELL"));

    await waitFor(() => {
      expect(api.createTrade).toHaveBeenCalledWith({
        creditId: "credit123",
        quantity: 5,
        pricePerTon: 25,
        type: "sell",
      });
    });
    expect(mockNavigation.goBack).toHaveBeenCalledTimes(1);
  });

  it("shows alert if quantity is zero or invalid", async () => {
    const { getByPlaceholderText, getByText } = renderComponent();
    await waitFor(() => expect(api.getWalletBalance).toHaveBeenCalled());
    const alertSpy = jest.spyOn(require("react-native").Alert, "alert");

    fireEvent.press(getByText("BUY"));
    fireEvent.changeText(getByPlaceholderText("Quantity (Tons)"), "0");
    fireEvent.press(getByText("Confirm BUY"));
    expect(alertSpy).toHaveBeenCalledWith("Invalid Quantity", "Please enter a valid quantity greater than 0.");

    alertSpy.mockClear();
    fireEvent.changeText(getByPlaceholderText("Quantity (Tons)"), "abc");
    fireEvent.press(getByText("Confirm BUY"));
    expect(alertSpy).toHaveBeenCalledWith("Invalid Quantity", "Please enter a valid quantity greater than 0.");

    alertSpy.mockRestore();
  });

  it("shows alert if trying to sell more tons than available", async () => {
    const { getByPlaceholderText, getByText } = renderComponent();
    await waitFor(() => expect(api.getWalletBalance).toHaveBeenCalled());
    const alertSpy = jest.spyOn(require("react-native").Alert, "alert");

    fireEvent.press(getByText("SELL"));
    fireEvent.changeText(getByPlaceholderText("Quantity (Tons)"), "101"); // availableTons is 100
    fireEvent.press(getByText("Confirm SELL"));
    expect(alertSpy).toHaveBeenCalledWith("Insufficient Credits", "You cannot sell more credits than available (100 Tons).");
    alertSpy.mockRestore();
  });

  it("shows alert if trying to buy with insufficient balance", async () => {
    // Mock a lower balance for this specific test
    api.getWalletBalance.mockResolvedValue({ success: true, balance: { amount: 100, currency: "USD" } });
    const { getByPlaceholderText, getByText } = renderComponent();
    await waitFor(() => expect(api.getWalletBalance).toHaveBeenCalled());
    const alertSpy = jest.spyOn(require("react-native").Alert, "alert");

    fireEvent.press(getByText("BUY"));
    fireEvent.changeText(getByPlaceholderText("Quantity (Tons)"), "5"); // 5 * $25 = $125, balance is $100
    fireEvent.press(getByText("Confirm BUY"));
    expect(alertSpy).toHaveBeenCalledWith("Insufficient Balance", "You do not have enough funds to complete this purchase. Required: $125.00, Available: $100.00");
    alertSpy.mockRestore();
  });

  it("shows error alert if createTrade API call fails", async () => {
    api.createTrade.mockRejectedValue({ response: { data: { message: "Trade execution failed" } } });
    const { getByPlaceholderText, getByText } = renderComponent();
    await waitFor(() => expect(api.getWalletBalance).toHaveBeenCalled());
    const alertSpy = jest.spyOn(require("react-native").Alert, "alert");

    fireEvent.press(getByText("BUY"));
    fireEvent.changeText(getByPlaceholderText("Quantity (Tons)"), "2");
    fireEvent.press(getByText("Confirm BUY"));

    await waitFor(() => expect(api.createTrade).toHaveBeenCalled());
    expect(alertSpy).toHaveBeenCalledWith("Trade Failed", "Trade execution failed");
    alertSpy.mockRestore();
  });
});

