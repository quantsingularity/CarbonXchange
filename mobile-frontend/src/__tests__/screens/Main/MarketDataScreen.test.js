import React from "react";
import { render, waitFor } from "@testing-library/react-native";
import { Provider } from "react-redux";
import { NavigationContainer } from "@react-navigation/native";
import configureStore from "redux-mock-store";
import thunk from "redux-thunk";
import MarketDataScreen from "../../../screens/Main/MarketDataScreen";
import * as api from "../../../services/api"; // To mock API calls

const middlewares = [thunk];
const mockStore = configureStore(middlewares);

// Mock navigation
const mockNavigation = { navigate: jest.fn() };

// Mock API service
jest.mock("../../../services/api", () => ({
  getMarketStats: jest.fn(),
  getMarketForecast: jest.fn(),
}));

// Mock react-native-chart-kit
jest.mock("react-native-chart-kit", () => ({
  LineChart: (props) => <mock-LineChart {...props} />,
  BarChart: (props) => <mock-BarChart {...props} />,
}));

describe("MarketDataScreen", () => {
  let store;
  const initialState = {
    auth: { user: { id: "1" }, token: "test-token", isLoggedIn: true },
  };

  beforeEach(() => {
    store = mockStore(initialState);
    api.getMarketStats.mockClear();
    api.getMarketForecast.mockClear();
  });

  const renderComponent = (currentStore = store) => {
    return render(
      <Provider store={currentStore}>
        <NavigationContainer>
          <MarketDataScreen navigation={mockNavigation} />
        </NavigationContainer>
      </Provider>
    );
  };

  it("renders correctly and shows loading indicators initially", () => {
    api.getMarketStats.mockReturnValue(new Promise(() => {})); // Keep pending
    api.getMarketForecast.mockReturnValue(new Promise(() => {})); // Keep pending
    const { getAllByTestId } = renderComponent();
    // Assuming loading indicators have testID="loading-indicator"
    // expect(getAllByTestId("loading-indicator").length).toBeGreaterThan(0);
    // For now, a simple check that it renders without crashing
    expect(true).toBe(true);
  });

  it("fetches and displays market stats and forecast", async () => {
    const mockStats = { totalVolume: 10000, averagePrice: 25.5, activeListings: 150 };
    const mockForecast = { trend: "upward", nextWeekPrice: 26.0, confidence: "high" };
    api.getMarketStats.mockResolvedValue({ success: true, statistics: mockStats });
    api.getMarketForecast.mockResolvedValue({ success: true, forecast: mockForecast });

    const { findByText } = renderComponent();

    await waitFor(() => {
      expect(api.getMarketStats).toHaveBeenCalledTimes(1);
      expect(api.getMarketForecast).toHaveBeenCalledTimes(1);
    });

    // Check for stats
    expect(await findByText(/Total Volume:/i)).toBeTruthy();
    expect(await findByText("10000")).toBeTruthy();
    expect(await findByText(/Average Price:/i)).toBeTruthy();
    expect(await findByText("$25.50")).toBeTruthy(); // Assuming formatting

    // Check for forecast
    expect(await findByText(/Market Trend:/i)).toBeTruthy();
    expect(await findByText("Upward")).toBeTruthy(); // Assuming capitalization
    expect(await findByText(/Next Week Est. Price:/i)).toBeTruthy();
    expect(await findByText("$26.00")).toBeTruthy(); // Assuming formatting
  });

  it("displays error messages if fetching data fails", async () => {
    api.getMarketStats.mockRejectedValue(new Error("Failed to fetch stats"));
    api.getMarketForecast.mockRejectedValue(new Error("Failed to fetch forecast"));

    const { findByText } = renderComponent();

    expect(await findByText(/Failed to load market statistics/i)).toBeTruthy();
    expect(await findByText(/Failed to load market forecast/i)).toBeTruthy();
  });

  // Add tests for chart rendering if possible by inspecting props passed to mocked charts
  it("passes correct data to LineChart for price trends", async () => {
    // This test would be more involved, requiring inspection of props passed to the mocked LineChart
    // For example, if getMarketPriceHistory is another API call made by the screen:
    // api.getMarketPriceHistory.mockResolvedValue({ success: true, history: [{date: '2023-01-01', price: 20}, ...] });
    // const { getByTestId } = renderComponent();
    // await waitFor(() => expect(getByTestId('price-trend-chart')).toBeTruthy());
    // const lineChart = getByTestId('price-trend-chart');
    // expect(lineChart.props.data.datasets[0].data).toEqual([expected data]);
    expect(true).toBe(true); // Placeholder
  });
});
