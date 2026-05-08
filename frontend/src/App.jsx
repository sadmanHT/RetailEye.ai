import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, useParams } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { Sidebar } from './components/layout/Sidebar.jsx';
import { TopBar } from './components/layout/TopBar.jsx';
import { Dashboard } from './pages/Dashboard.jsx';
import { Upload } from './pages/Upload.jsx';
import { Analytics } from './pages/Analytics.jsx';

const DashboardRoute = () => {
  const { jobId } = useParams();
  return <Dashboard jobId={jobId} />;
};

const AnimatedRoutes = () => {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<PageWrapper><Upload /></PageWrapper>} />
        <Route path="/dashboard/:jobId" element={<PageWrapper><DashboardRoute /></PageWrapper>} />
        <Route path="/analytics/:jobId" element={<PageWrapper><Analytics /></PageWrapper>} />
      </Routes>
    </AnimatePresence>
  );
};

const PageWrapper = ({ children }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    transition={{ duration: 0.3 }}
    className="w-full h-full"
  >
    {children}
  </motion.div>
);

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-[#08060d] text-white w-full overflow-hidden">
        <Sidebar />
        <div className="flex-1 ml-[240px] flex flex-col h-full overflow-hidden">
          <TopBar />
          <main className="flex-1 p-[32px] overflow-y-auto relative">
            <AnimatedRoutes />
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;

