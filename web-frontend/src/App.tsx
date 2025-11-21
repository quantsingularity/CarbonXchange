import { ThemeProvider } from "./components/theme-provider";
import Dashboard from "./components/Dashboard";

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="carbonxchange-theme">
      <div className="min-h-screen bg-background">
        <header className="border-b">
          <div className="container mx-auto py-4 px-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <span className="text-primary-foreground font-bold">CX</span>
              </div>
              <h1 className="text-xl font-bold">CarbonXchange</h1>
            </div>
            <nav>
              <ul className="flex space-x-6">
                <li className="font-medium text-primary">Dashboard</li>
                <li className="text-muted-foreground hover:text-foreground transition-colors">
                  Market
                </li>
                <li className="text-muted-foreground hover:text-foreground transition-colors">
                  Trade
                </li>
                <li className="text-muted-foreground hover:text-foreground transition-colors">
                  Portfolio
                </li>
              </ul>
            </nav>
          </div>
        </header>
        <main className="py-6">
          <Dashboard />
        </main>
        <footer className="border-t py-6">
          <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
            <p>© 2025 CarbonXchange. All rights reserved.</p>
          </div>
        </footer>
      </div>
    </ThemeProvider>
  );
}

export default App;
