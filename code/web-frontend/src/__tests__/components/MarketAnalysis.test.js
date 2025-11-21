import React from "react";
import { render, screen } from "@testing-library/react";
import "@testing-library/jest-dom";
import MarketAnalysis from "../../../components/MarketAnalysis"; // Adjust path as necessary

// Mock Recharts components used by MarketAnalysis
jest.mock("recharts", () => {
  const MockResponsiveContainer = ({ children }) => <div>{children}</div>;
  const MockBarChart = ({ children }) => <div>{children}</div>;
  const MockBar = () => <div data-testid="mock-bar"></div>;
  const MockXAxis = () => <div data-testid="mock-xaxis"></div>;
  const MockYAxis = () => <div data-testid="mock-yaxis"></div>;
  const MockCartesianGrid = () => <div data-testid="mock-cartesiangrid"></div>;
  const MockTooltip = () => <div data-testid="mock-tooltip"></div>;
  const MockLegend = () => <div data-testid="mock-legend"></div>;
  return {
    ResponsiveContainer: MockResponsiveContainer,
    BarChart: MockBarChart,
    Bar: MockBar,
    XAxis: MockXAxis,
    YAxis: MockYAxis,
    CartesianGrid: MockCartesianGrid,
    Tooltip: MockTooltip,
    Legend: MockLegend,
  };
});

describe("MarketAnalysis Component", () => {
  const mockMarketData = [
    { name: "Project A", value: 400 },
    { name: "Project B", value: 300 },
    { name: "Project C", value: 200 },
  ];

  it("renders without crashing with a title", () => {
    render(
      <MarketAnalysis data={mockMarketData} title="Market Analysis Overview" />,
    );
    expect(screen.getByText("Market Analysis Overview")).toBeInTheDocument();
  });

  it("renders mocked chart elements when data is provided", () => {
    render(<MarketAnalysis data={mockMarketData} title="Market Analysis" />);
    expect(screen.getByTestId("mock-bar")).toBeInTheDocument();
    expect(screen.getByTestId("mock-xaxis")).toBeInTheDocument();
    expect(screen.getByTestId("mock-yaxis")).toBeInTheDocument();
  });

  it("displays a message or renders differently when no data is provided", () => {
    render(<MarketAnalysis data={[]} title="Empty Market Analysis" />);
    // Assuming the component shows a message like "No market data available"
    // This depends on the actual implementation of MarketAnalysis.js
    // expect(screen.getByText('No market data available')).toBeInTheDocument();
    expect(screen.queryByTestId("mock-bar")).not.toBeInTheDocument();
    expect(screen.getByText("Empty Market Analysis")).toBeInTheDocument();
  });

  // Add tests for different data keys if the component is configurable
  // e.g., if `dataKey` for Bar is a prop
});
