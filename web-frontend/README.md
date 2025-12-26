# CarbonXchange Web Frontend

Modern, production-ready React frontend for the CarbonXchange carbon credit trading platform.

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite 6
- **Routing**: React Router v7
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: React Context API
- **HTTP Client**: Axios
- **Real-time Updates**: Socket.IO Client
- **Charts**: Recharts + D3.js
- **Testing**: Vitest + React Testing Library
- **Code Quality**: ESLint + TypeScript

## Features

- ✅ User Authentication (Login/Register)
- ✅ Real-time Market Dashboard
- ✅ Carbon Credit Marketplace
- ✅ Trading Interface (Buy/Sell)
- ✅ Portfolio Management
- ✅ Live Price Charts
- ✅ Mock Data Mode for Standalone Testing
- ✅ Responsive Design
- ✅ Dark Mode Support
- ✅ Comprehensive Test Coverage

## Getting Started

### Prerequisites

- Node.js 14+ (recommended: Node.js 18+)
- npm or pnpm

### Installation

1. Install dependencies:

```bash
npm install
```

2. Create environment file:

```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:

```env
VITE_API_URL=http://localhost:5000/api
VITE_SOCKET_URL=http://localhost:5000
VITE_USE_MOCK_SOCKET=true  # Set to false when backend is running
VITE_USE_MOCK_DATA=true    # Set to false when backend is running
```

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Building for Production

Build the application:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

### Testing

Run tests:

```bash
npm test
```

Run tests with UI:

```bash
npm run test:ui
```

Run tests once (CI mode):

```bash
npm run test:run
```

## Project Structure

```
web-frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── layout/         # Layout components
│   │   ├── ui/             # shadcn/ui components
│   │   ├── charts/         # Chart components
│   │   ├── Dashboard.tsx   # Main dashboard
│   │   └── ...
│   ├── pages/              # Page components
│   │   ├── Login.tsx       # Login page
│   │   ├── Register.tsx    # Registration page
│   │   ├── Market.tsx      # Carbon credit marketplace
│   │   ├── Trade.tsx       # Trading interface
│   │   └── Portfolio.tsx   # Portfolio management
│   ├── contexts/           # React contexts
│   │   └── AuthContext.tsx # Authentication context
│   ├── services/           # API services
│   │   └── api.ts          # API client and mock data
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility functions
│   ├── __tests__/          # Test files
│   └── App.tsx             # Main app component
├── public/                 # Static assets
└── ...config files
```

## API Integration

The frontend is designed to work with the CarbonXchange Python backend (Flask).

### Backend Endpoints Used

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/users/me` - Get current user
- `GET /api/market/statistics` - Market statistics
- `GET /api/carbon-credits` - List carbon credits
- `POST /api/trading/orders` - Create trading order
- `GET /api/users/me/portfolio` - Get user portfolio

### Mock Data Mode

When the backend is not available, the frontend automatically falls back to mock data. This allows:

- Standalone development and testing
- UI/UX development without backend dependency
- Demo mode for presentations

To enable mock mode, set in `.env`:

```env
VITE_USE_MOCK_DATA=true
```

## Running with Backend

1. Start the backend server (see `code/backend/README.md`):

```bash
cd ../code/backend
python src/main.py
```

2. Update `.env` in web-frontend:

```env
VITE_API_URL=http://localhost:5000/api
VITE_USE_MOCK_DATA=false
```

3. Start the frontend:

```bash
npm run dev
```

## Testing Strategy

### Unit Tests

- Component rendering tests
- API service tests
- Utility function tests

### Integration Tests

- User authentication flow
- Trading workflow
- Portfolio management

Tests are located in `src/__tests__/` and use Vitest + React Testing Library.

## Deployment

### Build for Production

```bash
npm run build
```

The build output will be in the `dist/` directory.

### Deployment Options

1. **Static Hosting** (Vercel, Netlify, etc.)
    - Deploy the `dist/` folder
    - Configure environment variables in hosting platform

2. **Serve with Backend**
    - Copy `dist/` contents to `code/backend/src/static/`
    - Backend will serve the frontend at root URL

3. **Docker**
    - Use the provided Dockerfile
    - Build: `docker build -t carbonxchange-frontend .`
    - Run: `docker run -p 3000:3000 carbonxchange-frontend`

## Environment Variables

| Variable               | Description        | Default                     |
| ---------------------- | ------------------ | --------------------------- |
| `VITE_API_URL`         | Backend API URL    | `http://localhost:5000/api` |
| `VITE_SOCKET_URL`      | WebSocket URL      | `http://localhost:5000`     |
| `VITE_USE_MOCK_SOCKET` | Use mock WebSocket | `true`                      |
| `VITE_USE_MOCK_DATA`   | Use mock API data  | `true`                      |
| `VITE_APP_ENV`         | Environment        | `development`               |

## Troubleshooting

### Port Already in Use

If port 5173 is in use, Vite will automatically try the next available port.

### API Connection Issues

1. Verify backend is running
2. Check `VITE_API_URL` in `.env`
3. Check browser console for CORS errors
4. Enable mock mode for development without backend

### Build Errors

1. Clear node_modules: `rm -rf node_modules package-lock.json`
2. Reinstall: `npm install`
3. Try with legacy peer deps: `npm install --legacy-peer-deps`

## Code Quality

### Linting

```bash
npm run lint
```

### Type Checking

```bash
npx tsc --noEmit
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new features
4. Ensure all tests pass: `npm run test:run`
5. Run linter: `npm run lint`
6. Submit a pull request

## License

MIT License - see LICENSE file for details
