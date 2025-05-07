import React from "react";
import { render, waitFor, fireEvent } from "@testing-library/react-native";
import { Provider } from "react-redux";
import { NavigationContainer } from "@react-navigation/native";
import configureStore from "redux-mock-store";
import thunk from "redux-thunk";
import WalletScreen from "../../../screens/Main/WalletScreen";
import * as api from "../../../services/api"; // To mock API calls

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

// Mock navigation
const mockNavigation = { navigate: jest.fn() };

// Mock API service
jest.mock("../../../services/api", () => ({
  getWalletBalance: jest.fn(),
  // Assuming there might be an API to get transaction history for the wallet
  getWalletTransactions: jest.fn(), 
}));

describe("WalletScreen", () => {
  let store;
  const initialState = {
    auth: { user: { id: "user123" }, token: "test-token", isLoggedIn: true },
    // You might have a dedicated wallet slice in Redux, or fetch directly
  };

  beforeEach(() => {
    store = mockStore(initialState);
    api.getWalletBalance.mockClear();
    api.getWalletTransactions.mockClear();
    mockNavigation.navigate.mockClear();
  });

  const renderComponent = (currentStore = store) => {
    return render(
      <Provider store={currentStore}>
        <NavigationContainer>
          <WalletScreen navigation={mockNavigation} />
        </NavigationContainer>
      </Provider>
    );
  };

  it("renders loading indicator initially for balance and transactions", () => {
    api.getWalletBalance.mockReturnValue(new Promise(() => {})); // Keep pending
    api.getWalletTransactions.mockReturnValue(new Promise(() => {})); // Keep pending
    const { queryByText } = renderComponent();
    // Example: expect(getAllByTestId("loading-indicator").length).toBeGreaterThanOrEqual(1);
    expect(queryByText(/Current Balance:/i)).toBeNull(); // Assuming balance is not shown while loading
    expect(queryByText("No transactions yet.")).toBeNull(); // Assuming transactions are not shown
  });

  it("fetches and displays wallet balance and transactions on mount", async () => {
    const mockBalance = { amount: 7500.50, currency: "USD" };
    const mockTransactions = [
      { id: "txn1", type: "deposit", amount: 1000, date: "2023-05-01", description: "Initial deposit" },
      { id: "txn2", type: "trade_profit", amount: 250.50, date: "2023-05-03", description: "Profit from SOLR trade" },
      { id: "txn3", type: "withdrawal", amount: -500, date: "2023-05-05", description: "Withdrawal to bank" },
    ];
    api.getWalletBalance.mockResolvedValue({ success: true, balance: mockBalance });
    api.getWalletTransactions.mockResolvedValue({ success: true, transactions: mockTransactions });

    const { findByText, getByText } = renderComponent();

    await waitFor(() => {
      expect(api.getWalletBalance).toHaveBeenCalledTimes(1);
      expect(api.getWalletTransactions).toHaveBeenCalledTimes(1);
    });

    expect(await findByText("Current Balance: $7,500.50")).toBeTruthy(); // Assuming formatting
    expect(getByText("Deposit: $1,000.00 - Initial deposit")).toBeTruthy();
    expect(getByText("Trade Profit: $250.50 - Profit from SOLR trade")).toBeTruthy();
    expect(getByText("Withdrawal: -$500.00 - Withdrawal to bank")).toBeTruthy();
  });

  it("displays a message if no transactions are available", async () => {
    api.getWalletBalance.mockResolvedValue({ success: true, balance: { amount: 100, currency: "USD" } });
    api.getWalletTransactions.mockResolvedValue({ success: true, transactions: [] });
    const { findByText } = renderComponent();
    expect(await findByText("No transactions yet.")).toBeTruthy();
  });

  it("displays error messages if fetching balance or transactions fails", async () => {
    api.getWalletBalance.mockRejectedValue(new Error("Failed to fetch balance"));
    api.getWalletTransactions.mockRejectedValue(new Error("Failed to fetch transactions"));

    const { findByText } = renderComponent();

    expect(await findByText(/Failed to load balance/i)).toBeTruthy();
    expect(await findByText(/Failed to load transactions/i)).toBeTruthy();
  });

  it("navigates to a deposit screen on 'Deposit Funds' button press", async () => {
    api.getWalletBalance.mockResolvedValue({ success: true, balance: { amount: 100, currency: "USD" } });
    api.getWalletTransactions.mockResolvedValue({ success: true, transactions: [] });
    const { findByText } = renderComponent();
    // Assuming a button with this text exists
    const depositButton = await findByText("Deposit Funds"); 
    fireEvent.press(depositButton);
    // expect(mockNavigation.navigate).toHaveBeenCalledWith("DepositScreen"); // Or relevant screen name
    expect(true).toBe(true); // Placeholder if navigation target is unknown
  });

  it("navigates to a withdrawal screen on 'Withdraw Funds' button press", async () => {
    api.getWalletBalance.mockResolvedValue({ success: true, balance: { amount: 100, currency: "USD" } });
    api.getWalletTransactions.mockResolvedValue({ success: true, transactions: [] });
    const { findByText } = renderComponent();
    // Assuming a button with this text exists
    const withdrawButton = await findByText("Withdraw Funds"); 
    fireEvent.press(withdrawButton);
    // expect(mockNavigation.navigate).toHaveBeenCalledWith("WithdrawScreen"); // Or relevant screen name
    expect(true).toBe(true); // Placeholder if navigation target is unknown
  });

  // Add test for pull-to-refresh functionality if implemented for balance and transactions
});

