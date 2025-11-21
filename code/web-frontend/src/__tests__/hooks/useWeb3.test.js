import { renderHook, act } from "@testing-library/react";
import useWeb3 from "../../../hooks/useWeb3"; // Adjust path as necessary
import Web3 from "web3";

// Mock the Web3 library
jest.mock("web3");

const mockSetAccount = jest.fn();
const mockSetBalance = jest.fn();
const mockSetError = jest.fn();

// Mock window.ethereum for testing connectWallet
global.window = Object.create(window);
Object.defineProperty(window, "ethereum", {
  value: {
    request: jest.fn(),
    on: jest.fn(),
    removeListener: jest.fn(),
  },
  writable: true,
});

describe("useWeb3 Hook", () => {
  let mockWeb3Instance;

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Mock Web3 constructor and its methods
    mockWeb3Instance = {
      eth: {
        requestAccounts: jest.fn(),
        getAccounts: jest.fn(),
        getBalance: jest.fn(),
        Contract: jest.fn().mockImplementation(() => ({
          methods: {
            someMethod: jest.fn().mockReturnThis(), // Chainable
            call: jest.fn(),
            send: jest.fn(),
          },
        })),
      },
    };
    Web3.mockImplementation(() => mockWeb3Instance);
    window.ethereum.request.mockClear();
  });

  it("initializes with default values", () => {
    const { result } = renderHook(() => useWeb3());
    expect(result.current.account).toBeNull();
    expect(result.current.balance).toBe("0");
    expect(result.current.web3).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.loading).toBe(false);
  });

  describe("connectWallet", () => {
    it("connects to wallet and sets account and balance successfully", async () => {
      const mockAccounts = ["0x12345"];
      const mockBalance = "1000000000000000000"; // 1 ETH in Wei
      window.ethereum.request.mockResolvedValueOnce(mockAccounts); // For 'eth_requestAccounts'
      mockWeb3Instance.eth.getAccounts.mockResolvedValueOnce(mockAccounts);
      mockWeb3Instance.eth.getBalance.mockResolvedValueOnce(mockBalance);

      const { result } = renderHook(() => useWeb3());

      await act(async () => {
        await result.current.connectWallet();
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.account).toBe(mockAccounts[0]);
      expect(result.current.balance).toBe(
        Web3.utils.fromWei(mockBalance, "ether"),
      );
      expect(result.current.error).toBeNull();
      expect(result.current.web3).toBe(mockWeb3Instance);
    });

    it("handles error if window.ethereum is not present", async () => {
      const originalEthereum = window.ethereum;
      delete window.ethereum;

      const { result } = renderHook(() => useWeb3());
      await act(async () => {
        await result.current.connectWallet();
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBe(
        "Please install MetaMask or a Web3-enabled browser.",
      );
      expect(result.current.account).toBeNull();
      expect(result.current.balance).toBe("0");
      window.ethereum = originalEthereum; // Restore for other tests
    });

    it("handles error during account fetching", async () => {
      const errorMessage = "Error fetching accounts";
      window.ethereum.request.mockRejectedValueOnce(new Error(errorMessage));

      const { result } = renderHook(() => useWeb3());
      await act(async () => {
        await result.current.connectWallet();
      });

      expect(result.current.loading).toBe(false);
      expect(result.current.error).toContain(errorMessage);
      expect(result.current.account).toBeNull();
    });

    it("sets loading state correctly during connection", async () => {
      window.ethereum.request.mockResolvedValueOnce(["0x123"]);
      mockWeb3Instance.eth.getAccounts.mockResolvedValueOnce(["0x123"]);
      mockWeb3Instance.eth.getBalance.mockResolvedValueOnce("100");

      const { result } = renderHook(() => useWeb3());

      act(() => {
        result.current.connectWallet(); // Don't await here to check intermediate loading state
      });
      expect(result.current.loading).toBe(true);

      // Wait for connectWallet to complete
      await act(async () => {
        await new Promise((resolve) => setTimeout(resolve, 0)); // Allow promises to resolve
      });
      expect(result.current.loading).toBe(false);
    });
  });

  describe("getContractInstance", () => {
    it("returns a contract instance", async () => {
      // First, connect wallet to initialize web3 instance
      window.ethereum.request.mockResolvedValueOnce(["0x123"]);
      mockWeb3Instance.eth.getAccounts.mockResolvedValueOnce(["0x123"]);
      mockWeb3Instance.eth.getBalance.mockResolvedValueOnce("100");

      const { result } = renderHook(() => useWeb3());
      await act(async () => {
        await result.current.connectWallet();
      });

      const mockAbi = [{ type: "function", name: "someMethod" }];
      const mockAddress = "0xContractAddress";
      act(() => {
        result.current.getContractInstance(mockAbi, mockAddress);
      });

      expect(mockWeb3Instance.eth.Contract).toHaveBeenCalledWith(
        mockAbi,
        mockAddress,
      );
    });

    it("returns null if web3 is not initialized", () => {
      const { result } = renderHook(() => useWeb3()); // Don't connect wallet
      const contractInstance = result.current.getContractInstance(
        [],
        "0xAddress",
      );
      expect(contractInstance).toBeNull();
      expect(result.current.error).toBe(
        "Web3 instance not available. Connect wallet first.",
      );
    });
  });

  // Add tests for accountChanged and chainChanged listeners if implemented in the hook
  // This would involve mocking window.ethereum.on and simulating events.
});
