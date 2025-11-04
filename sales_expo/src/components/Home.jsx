import { useNavigate } from 'react-router-dom';
import { FileText, Database, GitMerge, ArrowRight, Upload, Eye, Zap } from 'lucide-react';

export default function Home() {
  const navigate = useNavigate();

  const features = [
    {
      icon: Upload,
      title: 'Upload Documents',
      description: 'Easily upload and manage your documents with our intuitive interface.',
      action: () => navigate('/documents'),
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Eye,
      title: 'View Data',
      description: 'Visualize and analyze your processed data with powerful tools.',
      action: () => navigate('/data-viewer'),
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: Zap,
      title: 'Smart Mappings',
      description: 'Create intelligent mappings between different data sources.',
      action: () => navigate('/mappings'),
      color: 'from-orange-500 to-red-500'
    }
  ];

  return (
    <div className="min-h-[calc(100vh-5rem)]">
      {/* Hero Section */}
      <div className="text-center py-20 px-4">
        <div className="inline-block mb-6">
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-2xl blur-xl opacity-50"></div>
            <div className="relative p-6 bg-gradient-to-br from-blue-600 via-blue-500 to-cyan-600 rounded-2xl shadow-2xl">
              <FileText className="w-16 h-16 text-white" />
            </div>
          </div>
        </div>
        
        <h1 className="text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 via-cyan-600 to-blue-600 bg-clip-text text-transparent">
          Welcome to DocuFlow
        </h1>
        
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-12">
          Your comprehensive document processing system for efficient data management, 
          intelligent mapping, and seamless workflow automation.
        </p>

        <button
          onClick={() => navigate('/documents')}
          className="group inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-semibold text-lg shadow-lg hover:shadow-xl hover:scale-105 transition-all"
        >
          Get Started
          <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>

      {/* Features Grid */}
      <div className="max-w-6xl mx-auto px-4 pb-20">
        <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
          Powerful Features
        </h2>
        
        <div className="grid md:grid-cols-3 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="group bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all cursor-pointer border border-gray-100 hover:border-transparent hover:-translate-y-2"
                onClick={feature.action}
              >
                <div className={`inline-flex p-4 rounded-xl bg-gradient-to-br ${feature.color} mb-6 shadow-lg`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>
                
                <h3 className="text-xl font-bold mb-3 text-gray-800 group-hover:text-blue-600 transition-colors">
                  {feature.title}
                </h3>
                
                <p className="text-gray-600 mb-6 leading-relaxed">
                  {feature.description}
                </p>
                
                <div className="flex items-center text-blue-600 font-semibold group-hover:gap-3 gap-2 transition-all">
                  Learn more
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-gradient-to-r from-blue-600 to-cyan-600 py-16">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 text-center text-white">
            <div>
              <div className="text-5xl font-bold mb-2">Fast</div>
              <div className="text-blue-100">Lightning-fast processing</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">Secure</div>
              <div className="text-blue-100">Enterprise-grade security</div>
            </div>
            <div>
              <div className="text-5xl font-bold mb-2">Reliable</div>
              <div className="text-blue-100">99.9% uptime guarantee</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}