import React, { useState } from 'react';

// Create a context for Web3 and wallet connection
const Web3Context = React.createContext();

export const Web3Provider = ({ children }) => {
  const [account, setAccount] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [balance, setBalance] = useState(0);

  // Function to connect wallet
  const connectWallet = async () => {
    if (window.ethereum) {
      try {
        // Request account access
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        setAccount(accounts[0]);
        setIsConnected(true);
        
        // For demo purposes, set a sample balance
        setBalance(250);
        
        return true;
      } catch (error) {
        console.error("Error connecting to wallet:", error);
        return false;
      }
    } else {
      console.error("No Ethereum browser extension detected");
      return false;
    }
  };

  // Function to disconnect wallet
  const disconnectWallet = () => {
    setAccount(null);
    setIsConnected(false);
    setBalance(0);
  };

  return (
    <Web3Context.Provider
      value={{
        account,
        isConnected,
        balance,
        connectWallet,
        disconnectWallet
      }}
    >
      {children}
    </Web3Context.Provider>
  );
};

export const useWeb3 = () => React.useContext(Web3Context);

export default Web3Context;
