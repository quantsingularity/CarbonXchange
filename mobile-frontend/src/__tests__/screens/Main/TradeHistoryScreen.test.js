import React from "react";
import { render, waitFor, fireEvent } from "@testing-library/react-native";
import { Provider } from "react-redux";
import { NavigationContainer } from "@react-navigation/native";
import configureStore from "redux-mock-store";
import thunk from "redux-thunk";
import TradeHistoryScreen from "../../../screens/Main/TradeHistoryScreen";
import * as api from "../../../services/api"; // To mock API calls

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

// Mock navigation
const mockNavigation = { navigate: jest.fn() };

// Mock API service
jest.mock("../../../services/api", () => ({
  getUserTrades: jest.fn(),
}));

describe("TradeHistoryScreen", () => {
  let store;
  const initialState = {
    auth: { user: { id: "user123" }, token: "test-token", isLoggedIn: true },
    // Add other relevant initial states if your screen depends on them
  };

  beforeEach(() => {
    store = mockStore(initialState);
    api.getUserTrades.mockClear();
    mockNavigation.navigate.mockClear();
  });

  const renderComponent = (currentStore = store) => {
    return render(
      <Provider store={currentStore}>
        <NavigationContainer>
          <TradeHistoryScreen navigation={mockNavigation} />
        </NavigationContainer>
      </Provider>
    );
  };

  it("renders correctly and shows loading indicator initially", () => {
    api.getUserTrades.mockReturnValue(new Promise(() => {})); // Keep it pending
    const { queryByText } = renderComponent();
    // Check for loading state, e.g., a loading indicator or absence of trade items/empty message
    // For example, if you have a specific loading component:
    // expect(getByTestId("loading-indicator")).toBeTruthy();
    expect(queryByText("No trades yet.")).toBeNull();
  });

  it("fetches and displays user trades on mount", async () => {
    const mockTrades = [
      { id: "t1", creditId: "c1", type: "buy", quantity: 10, price: 200, timestamp: "2023-01-01T10:00:00Z", creditName: "Solar Project" },
      { id: "t2", creditId: "c2", type: "sell", quantity: 5, price: 150, timestamp: "2023-01-02T11:00:00Z", creditName: "Forestry Fund" },
    ];
    api.getUserTrades.mockResolvedValue({ success: true, trades: mockTrades });

    const { findByText, getByText } = renderComponent();

    await waitFor(() => expect(api.getUserTrades).toHaveBeenCalledTimes(1));

    expect(await findByText("Bought: Solar Project")).toBeTruthy();
    expect(getByText("10 Units at $200.00")).toBeTruthy();
    expect(getByText("Sold: Forestry Fund")).toBeTruthy();
    expect(getByText("5 Units at $150.00")).toBeTruthy();
  });

  it("displays a message if no trades are available", async () => {
    api.getUserTrades.mockResolvedValue({ success: true, trades: [] });
    const { findByText } = renderComponent();
    expect(await findByText("No trades yet. Make your first trade!")).toBeTruthy();
  });

  it("displays error message if fetching trades fails", async () => {
    api.getUserTrades.mockRejectedValue(new Error("Failed to fetch trades"));
    const { findByText } = renderComponent();
    expect(await findByText(/Failed to load trade history/i)).toBeTruthy();
  });

  it("navigates to CreditDetailScreen when a trade item is pressed", async () => {
    const mockTrades = [
      { id: "t1", creditId: "c1", type: "buy", quantity: 10, price: 200, timestamp: "2023-01-01T10:00:00Z", creditName: "Solar Project" },
    ];
    api.getUserTrades.mockResolvedValue({ success: true, trades: mockTrades });

    const { findByText } = renderComponent();
    const tradeItem = await findByText("Bought: Solar Project");
    fireEvent.press(tradeItem);

    // Assuming pressing a trade navigates to the detail of the associated credit
    expect(mockNavigation.navigate).toHaveBeenCalledWith("CreditDetail", { creditId: "c1" });
  });

  // Add test for pull-to-refresh functionality if implemented
});

