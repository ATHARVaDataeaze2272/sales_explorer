import { NavLink } from 'react-router-dom';
import { Home, FileText, Database, GitMerge, Settings } from 'lucide-react';
import logo from '../assets/sales_explorers.jpg';

export default function Navbar() {
  return (
    <nav className="h-24 bg-white border-b border-gray-200 flex items-center justify-between px-8 sticky top-0 z-50 shadow-md">
      {/* Logo Section */}
      <NavLink to="/" className="flex items-center gap-3 hover:opacity-90 transition-opacity">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500 to-orange-500 rounded-xl blur-sm opacity-30"></div>
          <img 
            src={logo} 
            alt="Logo" 
            className="relative w-14 h-14 rounded-xl object-cover shadow-lg border-2 border-white" 
          />
        </div>
        <div className="flex flex-col">
          <div className="text-xl font-bold leading-tight tracking-tight">
            <span className="text-blue-700">Sales</span>
            <span className="text-orange-500 text">Explorers</span>
          </div>
          <div className="text-[10px] text-gray-500 font-medium tracking-wide uppercase mt-0.5">
            Document Processing
          </div>
        </div>
      </NavLink>

      {/* Navigation Links */}
      <div className="flex gap-1">
        <NavLink
          to="/"
          className={({ isActive }) =>
            `flex items-center gap-2 px-5 py-2.5 rounded-lg transition-all ${
              isActive
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md'
                : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
            }`
          }
        >
          <Home className="w-4 h-4" />
          <span className="font-medium">Home</span>
        </NavLink>
        
        <NavLink
          to="/documents"
          className={({ isActive }) =>
            `flex items-center gap-2 px-5 py-2.5 rounded-lg transition-all ${
              isActive
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md'
                : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
            }`
          }
        >
          <FileText className="w-4 h-4" />
          <span className="font-medium">Documents</span>
        </NavLink>
        
        <NavLink
          to="/data-viewer"
          className={({ isActive }) =>
            `flex items-center gap-2 px-5 py-2.5 rounded-lg transition-all ${
              isActive
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md'
                : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
            }`
          }
        >
          <Database className="w-4 h-4" />
          <span className="font-medium">Data Viewer</span>
        </NavLink>
        
        <NavLink
          to="/mappings"
          className={({ isActive }) =>
            `flex items-center gap-2 px-5 py-2.5 rounded-lg transition-all ${
              isActive
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md'
                : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
            }`
          }
        >
          <GitMerge className="w-4 h-4" />
          <span className="font-medium">Mappings</span>
        </NavLink>
        
        <NavLink
          to="/admin"
          className={({ isActive }) =>
            `flex items-center gap-2 px-5 py-2.5 rounded-lg transition-all ${
              isActive
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-md'
                : 'text-gray-700 hover:bg-blue-50 hover:text-blue-600'
            }`
          }
        >
          <Settings className="w-4 h-4" />
          <span className="font-medium">Admin</span>
        </NavLink>
      </div>
    </nav>
  );
}