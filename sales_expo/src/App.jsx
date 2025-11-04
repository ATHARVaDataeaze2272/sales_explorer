import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar.jsx';
import Home from './components/Home.jsx';
import DocumentUploader from './components/DocumentUploader.jsx';
import DataViewer from './components/DataViewer.jsx';
import MatchingDashboard from './components/MatchingDashboard.jsx';

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-cyan-50">
        <Navbar />
        <div className="max-w-[1800px] mx-auto px-6 py-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/documents" element={<DocumentUploader />} />
            <Route path="/data-viewer" element={<DataViewer />} />
            <Route path="/mappings" element={<MatchingDashboard />} />
            <Route path="/admin" element={<div>Admin Page (To be implemented)</div>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}