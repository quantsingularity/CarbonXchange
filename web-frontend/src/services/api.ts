import axios from "axios";
import { io, Socket } from "socket.io-client";

// Define the base URL for the API
const API_BASE_URL =
  process.env.REACT_APP_API_URL || "http://localhost:3000/api/v1";

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Socket connection for real-time updates
let socket: Socket | null = null;

// Connect to websocket
export const connectSocket = (): Socket => {
  if (!socket) {
    socket = io(process.env.REACT_APP_SOCKET_URL || "http://localhost:3000", {
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    socket.on("connect", () => {
      console.log("Socket connected");
    });

    socket.on("disconnect", () => {
      console.log("Socket disconnected");
    });

    socket.on("error", (error: any) => {
      console.error("Socket error:", error);
    });
  }

  return socket;
};

// Disconnect socket
export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect();
    socket = null;
  }
};

// Subscribe to market data updates
export const subscribeToMarketData = (callback: (data: any) => void) => {
  const socket = connectSocket();
  socket.on("market_data_update", callback);

  // Request initial data
  socket.emit("subscribe_market_data");

  return () => {
    socket.off("market_data_update", callback);
    socket.emit("unsubscribe_market_data");
  };
};

// Subscribe to trading volume updates
export const subscribeToVolumeData = (callback: (data: any) => void) => {
  const socket = connectSocket();
  socket.on("volume_data_update", callback);

  // Request initial data
  socket.emit("subscribe_volume_data");

  return () => {
    socket.off("volume_data_update", callback);
    socket.emit("unsubscribe_volume_data");
  };
};

// Market Data API calls
export const getMarketStats = async () => {
  try {
    const response = await apiClient.get("/market/statistics");
    return response.data;
  } catch (error) {
    console.error("Get Market Stats API error:", error);
    throw error;
  }
};

export const getMarketForecast = async (params = {}) => {
  try {
    const response = await apiClient.get("/market/forecast", { params });
    return response.data;
  } catch (error) {
    console.error("Get Market Forecast API error:", error);
    throw error;
  }
};

// Historical data API calls
export const getHistoricalPriceData = async (timeframe: string) => {
  try {
    const response = await apiClient.get("/market/historical/price", {
      params: { timeframe },
    });
    return response.data;
  } catch (error) {
    console.error("Get Historical Price Data API error:", error);
    throw error;
  }
};

export const getHistoricalVolumeData = async (timeframe: string) => {
  try {
    const response = await apiClient.get("/market/historical/volume", {
      params: { timeframe },
    });
    return response.data;
  } catch (error) {
    console.error("Get Historical Volume Data API error:", error);
    throw error;
  }
};

// Mock API for development (when backend is not available)
export const getMockMarketStats = () => {
  return {
    success: true,
    data: {
      averagePrice: 25 + Math.random() * 5,
      priceChange24h: -0.5 + Math.random() * 2,
      volume24h: 15000 + Math.random() * 5000,
      totalVolume: 1250000 + Math.random() * 10000,
      lastUpdated: new Date().toISOString(),
    },
  };
};

// Mock historical data generator
export const getMockHistoricalData = (
  timeframe: string,
  dataType: "price" | "volume",
) => {
  const now = Date.now();
  const points = [];
  let interval: number;
  let count: number;

  // Set interval and count based on timeframe
  switch (timeframe) {
    case "1h":
      interval = 60 * 1000; // 1 minute
      count = 60;
      break;
    case "24h":
      interval = 15 * 60 * 1000; // 15 minutes
      count = 96;
      break;
    case "7d":
      interval = 2 * 60 * 60 * 1000; // 2 hours
      count = 84;
      break;
    case "30d":
      interval = 8 * 60 * 60 * 1000; // 8 hours
      count = 90;
      break;
    default:
      interval = 15 * 60 * 1000;
      count = 96;
  }

  // Base price and volume with some randomness
  let basePrice = 25;
  let baseVolume = 2500;

  // Generate data points
  for (let i = count - 1; i >= 0; i--) {
    const timestamp = now - i * interval;

    // Add some realistic price movements
    const priceChange = (Math.random() - 0.48) * 0.5;
    basePrice = Math.max(basePrice + priceChange, 10);

    // Volume tends to be higher when price changes more dramatically
    const volumeMultiplier = 1 + Math.abs(priceChange) * 5;
    // Add some randomness to volume
    const volumeNoise = Math.random() * 0.4 + 0.8; // 0.8 to 1.2
    const volume = Math.floor(baseVolume * volumeMultiplier * volumeNoise);

    // Add time-of-day patterns for volume (higher during market hours)
    const hour = new Date(timestamp).getHours();
    let timeOfDayFactor = 1;
    if (hour >= 9 && hour <= 16) {
      // Market hours
      timeOfDayFactor = 1.5;
    } else if (hour < 6 || hour > 20) {
      // Night hours
      timeOfDayFactor = 0.6;
    }

    points.push({
      timestamp,
      price: parseFloat(basePrice.toFixed(2)),
      volume: Math.floor(volume * timeOfDayFactor),
    });
  }

  return {
    success: true,
    data: {
      timeframe,
      dataType,
      points,
    },
  };
};

// Mock socket for development
export class MockSocket {
  private callbacks: Record<string, Array<(data: any) => void>> = {};
  private intervalIds: Record<string, NodeJS.Timeout> = {};

  on(event: string, callback: (data: any) => void) {
    if (!this.callbacks[event]) {
      this.callbacks[event] = [];
    }
    this.callbacks[event].push(callback);
  }

  off(event: string, callback: (data: any) => void) {
    if (this.callbacks[event]) {
      this.callbacks[event] = this.callbacks[event].filter(
        (cb) => cb !== callback,
      );
    }
  }

  emit(event: string) {
    if (event === "subscribe_market_data") {
      // Start sending mock market data updates
      this.intervalIds["market_data"] = setInterval(() => {
        const lastPrice = 25 + Math.random() * 5;
        const priceChange = (Math.random() - 0.48) * 0.2;
        const newPrice = Math.max(lastPrice + priceChange, 10);

        const update = {
          timestamp: Date.now(),
          price: parseFloat(newPrice.toFixed(2)),
          change: parseFloat(priceChange.toFixed(2)),
        };

        this.trigger("market_data_update", update);
      }, 5000);
    }

    if (event === "subscribe_volume_data") {
      // Start sending mock volume data updates
      this.intervalIds["volume_data"] = setInterval(() => {
        const baseVolume = 2500;
        const volumeNoise = Math.random() * 0.4 + 0.8;
        const volume = Math.floor(baseVolume * volumeNoise);

        const update = {
          timestamp: Date.now(),
          volume: volume,
        };

        this.trigger("volume_data_update", update);
      }, 5000);
    }

    if (event === "unsubscribe_market_data") {
      if (this.intervalIds["market_data"]) {
        clearInterval(this.intervalIds["market_data"]);
        delete this.intervalIds["market_data"];
      }
    }

    if (event === "unsubscribe_volume_data") {
      if (this.intervalIds["volume_data"]) {
        clearInterval(this.intervalIds["volume_data"]);
        delete this.intervalIds["volume_data"];
      }
    }
  }

  trigger(event: string, data: any) {
    if (this.callbacks[event]) {
      this.callbacks[event].forEach((callback) => callback(data));
    }
  }

  disconnect() {
    // Clear all intervals
    Object.values(this.intervalIds).forEach((intervalId) =>
      clearInterval(intervalId),
    );
    this.intervalIds = {};
    this.callbacks = {};
  }
}

// Create mock socket for development
let mockSocket: MockSocket | null = null;

// Connect to mock socket
export const connectMockSocket = (): MockSocket => {
  if (!mockSocket) {
    mockSocket = new MockSocket();
    console.log("Mock socket connected");
  }
  return mockSocket;
};

// Use real or mock socket based on environment
export const getSocket = (): Socket | MockSocket => {
  if (process.env.REACT_APP_USE_MOCK_SOCKET === "true") {
    return connectMockSocket();
  }
  return connectSocket();
};

// Export a function to determine if we're using mock data
export const isUsingMockData = (): boolean => {
  return (
    process.env.REACT_APP_USE_MOCK_SOCKET === "true" ||
    process.env.NODE_ENV === "development"
  );
};
