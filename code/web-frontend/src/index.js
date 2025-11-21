import React from "react";
import ReactDOM from "react-dom/client";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import App from "./App";
import theme from "./styles/theme";
import { Web3Provider } from "./hooks/useWeb3";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Web3Provider>
        <App />
      </Web3Provider>
    </ThemeProvider>
  </React.StrictMode>,
);
