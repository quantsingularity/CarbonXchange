import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import TradingDashboard from './components/TradingDashboard';
import CreditVisualization from './components/CreditVisualization';
import MarketAnalysis from './components/MarketAnalysis';

function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={TradingDashboard} />
        <Route path="/visualization" component={CreditVisualization} />
        <Route path="/analysis" component={MarketAnalysis} />
      </Switch>
    </Router>
  );
}

export default App;