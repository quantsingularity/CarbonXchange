import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './components/theme-provider';
import { AuthProvider } from './contexts/AuthContext';
import Layout from './components/layout/Layout';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './components/Dashboard';
import Market from './pages/Market';
import Trade from './pages/Trade';
import Portfolio from './pages/Portfolio';

function App() {
    return (
        <ThemeProvider defaultTheme="system" storageKey="carbonxchange-theme">
            <AuthProvider>
                <Router>
                    <Layout>
                        <Routes>
                            <Route path="/login" element={<Login />} />
                            <Route path="/register" element={<Register />} />

                            <Route
                                path="/dashboard"
                                element={
                                    <ProtectedRoute>
                                        <Dashboard />
                                    </ProtectedRoute>
                                }
                            />

                            <Route
                                path="/market"
                                element={
                                    <ProtectedRoute>
                                        <Market />
                                    </ProtectedRoute>
                                }
                            />

                            <Route
                                path="/trade"
                                element={
                                    <ProtectedRoute>
                                        <Trade />
                                    </ProtectedRoute>
                                }
                            />

                            <Route
                                path="/portfolio"
                                element={
                                    <ProtectedRoute>
                                        <Portfolio />
                                    </ProtectedRoute>
                                }
                            />

                            <Route path="/" element={<Navigate to="/dashboard" replace />} />
                            <Route path="*" element={<Navigate to="/dashboard" replace />} />
                        </Routes>
                    </Layout>
                </Router>
            </AuthProvider>
        </ThemeProvider>
    );
}

export default App;
