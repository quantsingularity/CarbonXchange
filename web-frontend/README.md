# CarbonXchange Web Frontend

This directory contains the web-based user interface for the CarbonXchange platform, a real-time carbon credit trading and market data visualization application.

## 🚀 Technology Stack

The frontend is a modern, full-stack application built with the following core technologies:

| Category | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | **React** (via Vite) | A fast, component-based JavaScript library for building user interfaces. |
| **Language** | **TypeScript** | A superset of JavaScript that adds static typing, improving code quality and maintainability. |
| **Styling** | **Tailwind CSS** | A utility-first CSS framework for rapidly building custom designs. |
| **Component Library** | **Shadcn/ui** (Radix UI) | A collection of reusable components built with Radix UI and styled with Tailwind CSS, providing a modern and accessible design system. |
| **State Management** | **React Hooks** | Utilizes built-in React hooks for state management. |
| **Data Fetching** | **Axios** & **Socket.IO** | Axios for traditional REST API calls and Socket.IO for real-time, bidirectional communication with the backend. |
| **Charting** | **Recharts** & **D3** | Used for visualizing carbon credit price and trading volume data. |
| **Build Tool** | **Vite** | A next-generation frontend tooling that provides a fast development server and optimized build process. |

## 📁 Directory Structure

The application follows a standard structure for a modern React/Vite project:

```
web-frontend/
├── public/
├── src/
│   ├── assets/             # Static assets like images or icons
│   ├── components/         # Reusable UI components and page-level components
│   │   ├── charts/         # Components for data visualization (e.g., CarbonPriceChart)
│   │   ├── ui/             # Shadcn/ui components (e.g., button, card, dialog)
│   │   ├── Dashboard.tsx   # Main dashboard view
│   │   └── MarketStats.tsx # Component for displaying key market statistics
│   ├── hooks/              # Custom React hooks (e.g., use-mobile, use-toast)
│   ├── lib/                # Utility functions (e.g., utils.ts for Tailwind class merging)
│   ├── services/           # API and real-time data handling logic (api.ts)
│   ├── App.tsx             # Main application component, including layout and routing
│   ├── main.tsx            # Entry point for the React application
│   └── index.css           # Global styles, including Tailwind directives
├── package.json            # Project dependencies and scripts
├── tailwind.config.js      # Tailwind CSS configuration
├── vite.config.ts          # Vite build configuration
└── tsconfig.json           # TypeScript configuration
```

## ⚙️ Setup and Installation

To set up the project locally, follow these steps:

1.  **Navigate to the project directory:**
    ```bash
    cd CarbonXchange/web-frontend
    ```

2.  **Install dependencies:**
    The project uses `pnpm` as the package manager.
    ```bash
    pnpm install
    ```

3.  **Configure Environment Variables (Optional):**
    The application is configured to connect to a backend API and a Socket.IO server. You may need to create a `.env` file in the `web-frontend` directory to override the default `http://localhost:3000` URLs.

    | Variable | Default Value | Description |
    | :--- | :--- | :--- |
    | `VITE_REACT_APP_API_URL` | `http://localhost:3000/api/v1` | Base URL for REST API calls (Axios). |
    | `VITE_REACT_APP_SOCKET_URL` | `http://localhost:3000` | Base URL for the Socket.IO connection. |
    | `VITE_REACT_APP_USE_MOCK_SOCKET` | `false` | Set to `true` to use mock data and a mock socket for development without a running backend. |

    *Note: The `api.ts` file contains logic to use mock data and a mock socket if the backend is unavailable, which is useful for isolated frontend development.*

## ▶️ Available Scripts

In the project directory, you can run the following scripts:

| Script | Command | Description |
| :--- | :--- | :--- |
| **Development** | `pnpm run dev` | Starts the development server using Vite. The application will be available at `http://localhost:5173` (or another port if 5173 is in use). |
| **Build** | `pnpm run build` | Compiles the application for production into the `dist` directory. |
| **Lint** | `pnpm run lint` | Runs ESLint to check for code quality and style issues. |
| **Preview** | `pnpm run preview` | Serves the production build locally for testing. |

## 🌐 API and Real-Time Data

The application uses the `src/services/api.ts` file to manage all backend communication:

*   **REST API:** Uses **Axios** to fetch market statistics and historical data (price and volume) from the `/api/v1` endpoint.
*   **Real-Time Data:** Uses **Socket.IO** to establish a persistent connection for live updates on market data and trading volume. The frontend subscribes to `market_data_update` and `volume_data_update` events.

## 🎨 Design and Components

The UI is built using a component-driven approach:

*   **Main Layout:** Defined in `App.tsx`, featuring a header with navigation, a main content area, and a footer.
*   **Dashboard:** The primary view is `Dashboard.tsx`, which organizes the main features:
    *   **Market Statistics:** Displayed via the `MarketStats.tsx` component.
    *   **Charts:** Interactive charts for price and volume are implemented in `CarbonPriceChart.tsx` and `TradingVolumeChart.tsx`, utilizing a tabbed interface.
*   **Theming:** The application uses `next-themes` and a `ThemeProvider` (`src/components/theme-provider.tsx`) to support light and dark modes.
*   **UI Primitives:** The `src/components/ui` directory contains a comprehensive set of UI components based on Shadcn/ui, ensuring consistency and accessibility across the application.
