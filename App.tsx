import React, { useState } from 'react';
import { HashRouter, Routes, Route, useLocation, useNavigate, Outlet, Navigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  BarChart3,
  Home as HomeIcon,
  FileText,
  Settings,
  LogOut,
  User,
  Menu,
  X
} from 'lucide-react';
import AnalyticsDashboard from './pages/Analytics';
import Home from './pages/Home';
import Review from './pages/Review';
import ControlHub from './pages/ControlHub';
import Events from './pages/Events';
import Mindmap from './pages/Mindmap';
import AnimatedNavTabs, { TabItem } from './components/AnimatedNavTabs';
import RouteGuard from './components/RouteGuard';
import ErrorBoundary from './components/ErrorBoundary';
import Login from './pages/Login';
import { AuthProvider } from './contexts/AuthContext';
import { ConfigProvider } from './contexts/ConfigContext';
import useAuth from './hooks/useAuth';

const Layout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const tabs: TabItem[] = [
    { path: '/', label: 'एनालिटिक्स', icon: BarChart3 },
    { path: '/home', label: 'होम', icon: HomeIcon, protected: true },
    { path: '/review', label: 'समीक्षा', icon: FileText, protected: true },
    { path: '/control', label: 'कंट्रोल हब', icon: Settings, protected: true },
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleLoginNavigate = () => {
    navigate('/login');
  };

  return (
    <div className="min-h-screen w-full bg-[#2e1065] bg-gradient-to-br from-[#1e1b4b] via-[#2e1065] to-[#4c1d95] text-white overflow-x-hidden font-sans selection:bg-[#8BF5E6] selection:text-[#2e1065]">

      {/* Ambient Background Effects - Aurora Style */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
        className="fixed top-[-20%] left-[-10%] w-[800px] h-[800px] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none z-0"
      />
      <motion.div
        animate={{
          scale: [1, 1.1, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 2 }}
        className="fixed bottom-[-20%] right-[-10%] w-[600px] h-[600px] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none z-0"
      />

      {/* Header Section - ULTRA MODERN, CENTERED */}
      <header className="relative z-50 py-12 md:py-16 px-6">

        {/* Admin Button - Absolute Positioning to prevent centering offset */}
        {/* Admin Button - Responsive Positioning */}
        <div className="absolute right-4 top-4 md:right-6 md:top-6 z-50 flex items-center gap-2">
          {isAuthenticated ? (
            <>
              {/* Desktop: Full Button */}
              <button
                onClick={handleLogout}
                className="hidden md:flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/10 hover:bg-red-500/20 text-red-200 border border-red-500/20 transition-all text-xs font-hindi backdrop-blur-md"
              >
                <LogOut size={14} />
                <span>लॉग आउट</span>
              </button>
              {/* Mobile: Icon Only */}
              <button
                onClick={handleLogout}
                className="md:hidden p-2 rounded-full bg-red-500/10 text-red-200 border border-red-500/20 backdrop-blur-md"
              >
                <LogOut size={18} />
              </button>
            </>
          ) : (
            <>
              {/* Desktop: Full Button */}
              <button
                onClick={handleLoginNavigate}
                className="hidden md:flex items-center gap-2 px-4 py-2 rounded-full bg-[#8BF5E6]/10 hover:bg-[#8BF5E6]/20 text-[#8BF5E6] border border-[#8BF5E6]/20 transition-all text-xs font-hindi backdrop-blur-md shadow-[0_0_15px_rgba(139,245,230,0.1)]"
              >
                <User size={14} />
                <span>एडमिन लॉगिन</span>
              </button>
              {/* Mobile: Icon Only */}
              <button
                onClick={handleLoginNavigate}
                className="md:hidden p-2 rounded-full bg-[#8BF5E6]/10 text-[#8BF5E6] border border-[#8BF5E6]/20 backdrop-blur-md"
              >
                <User size={18} />
              </button>
            </>
          )}
        </div>

        <div className="max-w-[1600px] mx-auto flex flex-col items-center justify-center relative">

          {/* Title - Massive & Centered */}
          <motion.div
            initial={{ y: -50, opacity: 0, scale: 0.9 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, type: "spring" }}
            className="text-center z-10 relative"
          >
            <h1 className="text-5xl md:text-7xl font-bold text-white drop-shadow-[0_0_35px_rgba(139,245,230,0.4)] tracking-tight mb-4 font-hindi leading-tight">
              सोशल मीडिया एनालिटिक्स डैशबोर्ड
            </h1>

            {/* Animated Gradient Underline */}
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: "200px", opacity: 1 }}
              transition={{ delay: 0.6, duration: 1 }}
              className="h-[3px] bg-gradient-to-r from-transparent via-[#8BF5E6] to-transparent mx-auto rounded-full shadow-[0_0_10px_#8BF5E6]"
            />
          </motion.div>

          {/* Mobile Menu Toggle */}
          <div className="absolute right-0 top-2 md:hidden z-20">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-full bg-white/10 border border-white/20 text-white"
            >
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Navigation Tabs - Liquid Animation */}
        <div className="hidden md:flex justify-center mt-10">
          <AnimatedNavTabs
            tabs={tabs}
            activePath={location.pathname}
            isAuthenticated={isAuthenticated}
          />
        </div>
      </header>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="md:hidden relative z-40 px-4 overflow-hidden"
          >
            <div className="bg-[#1e1b4b]/95 backdrop-blur-xl border border-white/10 rounded-2xl p-4 space-y-2">
              {tabs.map((tab) => (
                (!tab.protected || isAuthenticated) && (
                  <div
                    key={tab.path}
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <AnimatedNavTabs
                      tabs={[tab]}
                      activePath={location.pathname}
                      isAuthenticated={isAuthenticated}
                    />
                  </div>
                )
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Content Area with Page Transitions */}
      <main className="relative z-10 p-4 md:p-6 lg:p-8 max-w-[1600px] mx-auto min-h-[calc(100vh-300px)]">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 20, filter: "blur(5px)" }}
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            exit={{ opacity: 0, y: -20, filter: "blur(5px)" }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          >
            <Outlet />
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="relative z-10 py-8 text-center text-slate-500 text-sm border-t border-white/5 mt-10 font-hindi">
        <p>© 2024 प्रोजेक्ट ध्रुव | सर्वाधिकार सुरक्षित</p>
      </footer>
    </div>
  );
};

const App = () => {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <ConfigProvider>
          <HashRouter>
            <Routes>
              <Route element={<Layout />}>
                <Route path="/" element={<AnalyticsDashboard />} />
                <Route
                  path="/home"
                  element={
                    <RouteGuard>
                      <Home />
                    </RouteGuard>
                  }
                />
                <Route
                  path="/review"
                  element={
                    <RouteGuard>
                      <Review />
                    </RouteGuard>
                  }
                />
                <Route
                  path="/control"
                  element={
                    <RouteGuard>
                      <ControlHub />
                    </RouteGuard>
                  }
                />
                <Route
                  path="/events"
                  element={
                    <RouteGuard>
                      <Events />
                    </RouteGuard>
                  }
                />
                <Route
                  path="/mindmap"
                  element={
                    <RouteGuard>
                      <Mindmap />
                    </RouteGuard>
                  }
                />
              </Route>
              <Route path="/login" element={<Login />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </HashRouter>
        </ConfigProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
