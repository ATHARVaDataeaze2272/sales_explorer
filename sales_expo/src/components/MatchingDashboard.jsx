


import React, { useState, useEffect } from 'react';
import { RefreshCw, Users, Search, Edit, Trash2, CheckCircle, AlertCircle, Info, Eye, X, Play, PlayCircle } from 'lucide-react';

const API_BASE_URL = '/api/matching';

const MatchingDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  
  // Active view state
  const [activeView, setActiveView] = useState('dashboard'); // dashboard, single, all, results
  
  // Modal states
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [matchDetail, setMatchDetail] = useState(null);
  
  const [documents, setDocuments] = useState([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState('');
  const [profileId, setProfileId] = useState(''); // Store profile_id from document
  const [matchResults, setMatchResults] = useState([]);
  const [allMatches, setAllMatches] = useState([]); // Store all matches

  const [singleMatchForm, setSingleMatchForm] = useState({
    max_matches: 15,
    max_per_company: 3,
    min_score: 0.5,
    force_rematch: false,
    weight_job_title: 0.4,
    weight_business_area: 0.3,
    weight_activity: 0.3,
  });

  const [allMatchForm, setAllMatchForm] = useState({
    max_matches: 15,
    max_per_company: 3,
    min_score: 0.5,
    force_rematch: false,
  });

  const [updateStatusForm, setUpdateStatusForm] = useState({
    status: 'pending',
    notes: '',
    rejection_reason: '',
  });

  useEffect(() => {
    fetchDocuments();
    fetchStats();
    fetchHealth();
    const handleClickOutside = (event) => {
      const menu = document.getElementById('download-menu');
      if (menu && !menu.contains(event.target) && !event.target.closest('button')) {
        menu.classList.add('hidden');
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

 

  const showSuccess = (msg) => {
    setSuccess(msg);
    setTimeout(() => setSuccess(null), 5000);
  };

  const showError = (msg) => {
    setError(msg);
    setTimeout(() => setError(null), 5000);
  };

  const fetchDocuments = async () => {
    try {
      const res = await fetch('/api/documents?status=completed&limit=100');
      if (!res.ok) throw new Error('Failed to fetch documents');
      const data = await res.json();
      const clientDocuments = (data.documents || []).filter(doc => doc.document_type === 'clients');
      setDocuments(clientDocuments);
    } catch (err) {
      showError(err.message);
      setDocuments([]);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/stats`);
      if (!res.ok) throw new Error('Failed to fetch stats');
      const data = await res.json();
      setStats(data);
    } catch (err) {
      showError(err.message);
    }
  };

  const fetchHealth = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      if (!res.ok) throw new Error('Failed to fetch health');
      const data = await res.json();
      setHealth(data);
    } catch (err) {
      showError(err.message);
    }
  };

  const fetchProfileAndResults = async (documentId) => {
    if (!documentId) {
      setProfileId('');
      setMatchResults([]);
      setAllMatches([]);
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`/api/documents/${documentId}`);
      if (!res.ok) throw new Error('Failed to fetch document details');
      const data = await res.json();
      
      // Extract profile_id from the first company (all companies share the same profile_id)
      const profileId = data.companies && data.companies.length > 0 ? data.companies[0].profile_id : null;
      
      if (!profileId) {
        throw new Error('No profile ID found in document');
      }
      
      setProfileId(profileId);
      // Fetch match results using profile_id
      await fetchMatchResults(profileId);
    } catch (err) {
      showError(err.message);
      setProfileId('');
      setMatchResults([]);
      setAllMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchMatchResults = async (profileId) => {
    if (!profileId) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/results/${profileId}`);
      if (!res.ok) throw new Error('Failed to fetch results');
      const data = await res.json();
      
      // Combine priority and discovery matches
      const allMatches = [
        ...(data.priority_matches || []),
        ...(data.discovery_matches || [])
      ];
      
      setAllMatches(allMatches);
      setMatchResults(allMatches);
    } catch (err) {
      showError(err.message);
      setMatchResults([]);
      setAllMatches([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchMatchDetail = async (matchId) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/match-detail/${matchId}`);
      if (!res.ok) throw new Error('Failed to fetch match details');
      const data = await res.json();
      setMatchDetail(data);
      setShowDetailModal(true);
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runSingleMatching = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...singleMatchForm,
          client_id: profileId // Use profileId instead of form client_id
        }),
      });
      if (!res.ok) throw new Error('Failed to run matching');
      const data = await res.json();
      showSuccess(data.message);
      fetchStats();
      // Refresh results for the current profile
      if (profileId) {
        fetchMatchResults(profileId);
      }
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const runAllMatching = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/run-all`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...allMatchForm, use_background: true }),
      });
      if (!res.ok) throw new Error('Failed to run all matching');
      const data = await res.json();
      showSuccess(data.message);
      fetchStats();
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateMatchStatus = async () => {
    if (!selectedMatch) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/results/${selectedMatch.match_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateStatusForm),
      });
      if (!res.ok) throw new Error('Failed to update status');
      const data = await res.json();
      showSuccess(data.message);
      setShowStatusModal(false);
      if (profileId) {
        fetchMatchResults(profileId); // Refresh results using profile_id
      }
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteMatch = async (matchId) => {
    if (!confirm('Are you sure you want to delete this match?')) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/results/${matchId}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error('Failed to delete match');
      const data = await res.json();
      showSuccess(data.message);
      if (profileId) {
        fetchMatchResults(profileId); // Refresh results using profile_id
      }
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteClientMatches = async () => {
    if (!profileId || !confirm('Delete all matches for this profile?')) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/results/client/${profileId}`, {
        method: 'DELETE',
      });
      if (!res.ok) throw new Error('Failed to delete profile matches');
      const data = await res.json();
      showSuccess(data.message);
      if (profileId) {
        fetchMatchResults(profileId); // Refresh results using profile_id
      }
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const openStatusModal = (match) => {
    setSelectedMatch(match);
    setUpdateStatusForm({
      status: match.status,
      notes: match.notes || '',
      rejection_reason: match.rejection_reason || '',
    });
    setShowStatusModal(true);
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      contacted: 'bg-blue-100 text-blue-800',
      meeting_scheduled: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };


  const downloadMatches = async (matchType = 'all') => {
    if (!profileId) {
      showError('Please select a document first');
      return;
    }
    
    setLoading(true);
    try {
      const url = `${API_BASE_URL}/export/${profileId}${matchType !== 'all' ? `?match_type=${matchType}` : ''}`;
      
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to download matches');
      
      // Get filename from Content-Disposition header
      const contentDisposition = res.headers.get('Content-Disposition');
      let filename = `matches_${profileId}.csv`; // fallback
      
      if (contentDisposition) {
        // Extract filename from header, handling both quoted and unquoted filenames
        const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/['"]/g, '').trim();
        }
      }
      
      // Download file
      const blob = await res.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);
      
      showSuccess('Matches exported successfully!');
    } catch (err) {
      showError(err.message);
    } finally {
      setLoading(false);
    }
  };
  

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Client-Prospect Matching System</h1>
          <p className="text-gray-600">Manage and monitor client-prospect matching operations</p>
        </div>

        {/* Notifications */}
        {success && (
          <div className="mb-6 bg-green-50 border-l-4 border-green-400 p-4 rounded">
            <div className="flex items-center">
              <CheckCircle className="text-green-400 mr-3" size={20} />
              <p className="text-green-700">{success}</p>
            </div>
          </div>
        )}
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-400 p-4 rounded">
            <div className="flex items-center">
              <AlertCircle className="text-red-400 mr-3" size={20} />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="mb-6 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="flex space-x-1 p-2">
            <button
              onClick={() => setActiveView('dashboard')}
              className={`flex-1 px-4 py-3 rounded-md font-medium transition-colors ${
                activeView === 'dashboard'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Info className="inline mr-2" size={18} />
              Dashboard
            </button>
            <button
              onClick={() => setActiveView('single')}
              className={`flex-1 px-4 py-3 rounded-md font-medium transition-colors ${
                activeView === 'single'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Play className="inline mr-2" size={18} />
              Single Match
            </button>
            <button
              onClick={() => setActiveView('all')}
              className={`flex-1 px-4 py-3 rounded-md font-medium transition-colors ${
                activeView === 'all'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <PlayCircle className="inline mr-2" size={18} />
              Batch Match
            </button>
            <button
              onClick={() => setActiveView('results')}
              className={`flex-1 px-4 py-3 rounded-md font-medium transition-colors ${
                activeView === 'results'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              <Search className="inline mr-2" size={18} />
              View Results
            </button>
          </div>
        </div>

        {/* Dashboard View */}
        {activeView === 'dashboard' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                  <Info className="mr-2 text-blue-600" size={24} />
                  System Health
                </h2>
                <button
                  onClick={fetchHealth}
                  className="text-blue-600 hover:text-blue-700"
                  disabled={loading}
                >
                  <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                </button>
              </div>
              {health ? (
                <div className="space-y-3">
                  <div className="flex justify-between items-center py-2 border-b">
                    <span className="text-gray-600">Status</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      health.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {health.status}
                    </span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Client Embeddings</span>
                    <span className="font-semibold">{health.client_embeddings}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Prospect Embeddings</span>
                    <span className="font-semibold">{health.prospect_embeddings}</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-gray-600">Total Matches</span>
                    <span className="font-semibold">{health.total_matches}</span>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">Loading health data...</p>
              )}
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center">
                  <Users className="mr-2 text-purple-600" size={24} />
                  Matching Statistics
                </h2>
                <button
                  onClick={fetchStats}
                  className="text-blue-600 hover:text-blue-700"
                  disabled={loading}
                >
                  <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                </button>
              </div>
              {stats ? (
                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Total Matches</span>
                    <span className="font-semibold">{stats.total_matches}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span className="text-gray-600">Average Score</span>
                    <span className="font-semibold">{stats.average_score?.toFixed(4) || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between py-2">
                    <span className="text-gray-600">Clients with Matches</span>
                    <span className="font-semibold">{stats.clients_with_matches}</span>
                  </div>
                </div>
              ) : (
                <p className="text-gray-500">Loading statistics...</p>
              )}
            </div>
          </div>
        )}
        {/* Single Match View */}
{activeView === 'single' && (
  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <h2 className="text-2xl font-semibold mb-6 text-gray-900">Run Matching for Single Client</h2>
    
    {/* Document Selector */}
    <div className="mb-6">
      <label className="block text-sm font-medium text-gray-700 mb-2">Select Client Document *</label>
      <select
        value={selectedDocumentId}
        onChange={(e) => {
          const docId = e.target.value;
          setSelectedDocumentId(docId);
          fetchProfileAndResults(docId);
          // Update form with profile_id
          if (docId) {
            // Profile ID will be set after fetchProfileAndResults completes
          } else {
            setSingleMatchForm({...singleMatchForm, client_id: ''});
          }
        }}
        className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <option value="">Select a document</option>
        {documents.map((doc) => (
          <option key={doc.id} value={doc.id}>
            {doc.filename}
          </option>
        ))}
      </select>
      {profileId && (
        <p className="mt-2 text-sm text-gray-600">Profile ID: {profileId}</p>
      )}
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Max Matches</label>
        <input
          type="number"
          name="max_matches"
          value={singleMatchForm.max_matches}
          onChange={(e) => setSingleMatchForm({...singleMatchForm, max_matches: parseInt(e.target.value)})}
          className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Max Per Company</label>
        <input
          type="number"
          name="max_per_company"
          value={singleMatchForm.max_per_company}
          onChange={(e) => setSingleMatchForm({...singleMatchForm, max_per_company: parseInt(e.target.value)})}
          className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Min Score</label>
        <input
          type="number"
          step="0.01"
          name="min_score"
          value={singleMatchForm.min_score}
          onChange={(e) => setSingleMatchForm({...singleMatchForm, min_score: parseFloat(e.target.value)})}
          className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Weight: Job Title (0-100%)
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            step="1"
            min="0"
            max="100"
            name="weight_job_title"
            value={(singleMatchForm.weight_job_title * 100).toFixed(0)}
            onChange={(e) => {
              const percentage = Math.min(100, Math.max(0, parseInt(e.target.value) || 0));
              setSingleMatchForm({...singleMatchForm, weight_job_title: percentage / 100});
            }}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="flex items-center text-gray-600 font-medium">%</span>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Weight: Business Area (0-100%)
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            step="1"
            min="0"
            max="100"
            name="weight_business_area"
            value={(singleMatchForm.weight_business_area * 100).toFixed(0)}
            onChange={(e) => {
              const percentage = Math.min(100, Math.max(0, parseInt(e.target.value) || 0));
              setSingleMatchForm({...singleMatchForm, weight_business_area: percentage / 100});
            }}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="flex items-center text-gray-600 font-medium">%</span>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Weight: Activity (0-100%)
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            step="1"
            min="0"
            max="100"
            name="weight_activity"
            value={(singleMatchForm.weight_activity * 100).toFixed(0)}
            onChange={(e) => {
              const percentage = Math.min(100, Math.max(0, parseInt(e.target.value) || 0));
              setSingleMatchForm({...singleMatchForm, weight_activity: percentage / 100});
            }}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="flex items-center text-gray-600 font-medium">%</span>
        </div>
      </div>
      <div className="flex items-end">
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            name="force_rematch"
            checked={singleMatchForm.force_rematch}
            onChange={(e) => setSingleMatchForm({...singleMatchForm, force_rematch: e.target.checked})}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm font-medium text-gray-700">Force Rematch</span>
        </label>
      </div>
    </div>
    
    {/* Weight validation warning */}
    {(() => {
      const total = singleMatchForm.weight_job_title + singleMatchForm.weight_business_area + singleMatchForm.weight_activity;
      const isValid = Math.abs(total - 1.0) < 0.01;
      return !isValid ? (
        <div className="mb-4 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <p className="text-yellow-700 text-sm">
            <strong>Warning:</strong> Weights must sum to 100% (currently {(total * 100).toFixed(0)}%)
          </p>
        </div>
      ) : null;
    })()}
    
    <button
      onClick={() => {
        const total = singleMatchForm.weight_job_title + singleMatchForm.weight_business_area + singleMatchForm.weight_activity;
        if (Math.abs(total - 1.0) >= 0.01) {
          showError('Weights must sum to 100%');
          return;
        }
        // Use profileId instead of client_id
        runSingleMatching();
      }}
      disabled={loading || !profileId}
      className="w-full md:w-auto bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
    >
      {loading ? 'Running...' : 'Run Matching'}
    </button>
  </div>
)}
        {/* Single Match View
        {activeView === 'single' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-2xl font-semibold mb-6 text-gray-900">Run Matching for Single Client</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Client ID *</label>
                <input
                  type="number"
                  name="client_id"
                  value={singleMatchForm.client_id}
                  onChange={(e) => setSingleMatchForm({...singleMatchForm, client_id: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter client ID"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Max Matches</label>
                <input
                  type="number"
                  name="max_matches"
                  value={singleMatchForm.max_matches}
                  onChange={(e) => setSingleMatchForm({...singleMatchForm, max_matches: parseInt(e.target.value)})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Max Per Company</label>
                <input
                  type="number"
                  name="max_per_company"
                  value={singleMatchForm.max_per_company}
                  onChange={(e) => setSingleMatchForm({...singleMatchForm, max_per_company: parseInt(e.target.value)})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Min Score</label>
                <input
                  type="number"
                  step="0.01"
                  name="min_score"
                  value={singleMatchForm.min_score}
                  onChange={(e) => setSingleMatchForm({...singleMatchForm, min_score: parseFloat(e.target.value)})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Weight: Job Title</label>
                <input
                  type="number"
                  step="0.01"
                  name="weight_job_title"
                  value={singleMatchForm.weight_job_title}
                  onChange={(e) => setSingleMatchForm({...singleMatchForm, weight_job_title: parseFloat(e.target.value)})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Weight: Business Area</label>
                <input
                  type="number"
                  step="0.01"
                  name="weight_business_area"
                  value={singleMatchForm.weight_business_area}
                  onChange={(e) => setSingleMatchForm({...singleMatchForm, weight_business_area: parseFloat(e.target.value)})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Weight: Activity</label>
                <input
                  type="number"
                  step="0.01"
                  name="weight_activity"
                  value={singleMatchForm.weight_activity}
                  onChange={(e) => setSingleMatchForm({...singleMatchForm, weight_activity: parseFloat(e.target.value)})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex items-end">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    name="force_rematch"
                    checked={singleMatchForm.force_rematch}
                    onChange={(e) => setSingleMatchForm({...singleMatchForm, force_rematch: e.target.checked})}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700">Force Rematch</span>
                </label>
              </div>
            </div>
            <button
              onClick={runSingleMatching}
              disabled={loading || !singleMatchForm.client_id}
              className="w-full md:w-auto bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {loading ? 'Running...' : 'Run Matching'}
            </button>
          </div>
        )} */}

        {/* Batch Match View
        {activeView === 'all' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-2xl font-semibold mb-6 text-gray-900">Run Matching for All Clients</h2>
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
              <p className="text-yellow-700 text-sm">
                <strong>Note:</strong> This operation will run in the background and may take several minutes to complete for large datasets.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Max Matches</label>
                <input
                  type="number"
                  name="max_matches"
                  value={allMatchForm.max_matches}
                  onChange={(e) => setAllMatchForm({...allMatchForm, max_matches: parseInt(e.target.value)})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Max Per Company</label>
                <input
                  type="number"
                  name="max_per_company"
                  value={allMatchForm.max_per_company}
                  onChange={(e) => setAllMatchForm({...allMatchForm, max_per_company: parseInt(e.target.value)})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Min Score</label>
                <input
                  type="number"
                  step="0.01"
                  name="min_score"
                  value={allMatchForm.min_score}
                  onChange={(e) => setAllMatchForm({...allMatchForm, min_score: parseFloat(e.target.value)})}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex items-end">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    name="force_rematch"
                    checked={allMatchForm.force_rematch}
                    onChange={(e) => setAllMatchForm({...allMatchForm, force_rematch: e.target.checked})}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="text-sm font-medium text-gray-700">Force Rematch</span>
                </label>
              </div>
            </div>
            <button
              onClick={runAllMatching}
              disabled={loading}
              className="w-full md:w-auto bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
            >
              {loading ? 'Starting...' : 'Run Batch Matching'}
            </button>
          </div>
        )} */}

        {/* Batch Match View */}
{activeView === 'all' && (
  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <h2 className="text-2xl font-semibold mb-6 text-gray-900">Run Matching for All Clients</h2>
    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
      <p className="text-yellow-700 text-sm">
        <strong>Note:</strong> This operation will run in the background and may take several minutes to complete for large datasets.
      </p>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Max Matches</label>
        <input
          type="number"
          name="max_matches"
          value={allMatchForm.max_matches}
          onChange={(e) => setAllMatchForm({...allMatchForm, max_matches: parseInt(e.target.value)})}
          className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Max Per Company</label>
        <input
          type="number"
          name="max_per_company"
          value={allMatchForm.max_per_company}
          onChange={(e) => setAllMatchForm({...allMatchForm, max_per_company: parseInt(e.target.value)})}
          className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Min Score</label>
        <input
          type="number"
          step="0.01"
          name="min_score"
          value={allMatchForm.min_score}
          onChange={(e) => setAllMatchForm({...allMatchForm, min_score: parseFloat(e.target.value)})}
          className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Weight: Job Title (0-100%)
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            step="1"
            min="0"
            max="100"
            name="weight_job_title"
            value={(allMatchForm.weight_job_title * 100).toFixed(0)}
            onChange={(e) => {
              const percentage = Math.min(100, Math.max(0, parseInt(e.target.value) || 0));
              setAllMatchForm({...allMatchForm, weight_job_title: percentage / 100});
            }}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="flex items-center text-gray-600 font-medium">%</span>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Weight: Business Area (0-100%)
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            step="1"
            min="0"
            max="100"
            name="weight_business_area"
            value={(allMatchForm.weight_business_area * 100).toFixed(0)}
            onChange={(e) => {
              const percentage = Math.min(100, Math.max(0, parseInt(e.target.value) || 0));
              setAllMatchForm({...allMatchForm, weight_business_area: percentage / 100});
            }}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="flex items-center text-gray-600 font-medium">%</span>
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Weight: Activity (0-100%)
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            step="1"
            min="0"
            max="100"
            name="weight_activity"
            value={(allMatchForm.weight_activity * 100).toFixed(0)}
            onChange={(e) => {
              const percentage = Math.min(100, Math.max(0, parseInt(e.target.value) || 0));
              setAllMatchForm({...allMatchForm, weight_activity: percentage / 100});
            }}
            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
          <span className="flex items-center text-gray-600 font-medium">%</span>
        </div>
      </div>
      <div className="flex items-end">
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            name="force_rematch"
            checked={allMatchForm.force_rematch}
            onChange={(e) => setAllMatchForm({...allMatchForm, force_rematch: e.target.checked})}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm font-medium text-gray-700">Force Rematch</span>
        </label>
      </div>
    </div>
    
    {/* Weight validation warning */}
    {(() => {
      const total = allMatchForm.weight_job_title + allMatchForm.weight_business_area + allMatchForm.weight_activity;
      const isValid = Math.abs(total - 1.0) < 0.01;
      return !isValid ? (
        <div className="mb-4 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <p className="text-yellow-700 text-sm">
            <strong>Warning:</strong> Weights must sum to 100% (currently {(total * 100).toFixed(0)}%)
          </p>
        </div>
      ) : null;
    })()}
    
    <button
      onClick={() => {
        const total = allMatchForm.weight_job_title + allMatchForm.weight_business_area + allMatchForm.weight_activity;
        if (Math.abs(total - 1.0) >= 0.01) {
          showError('Weights must sum to 100%');
          return;
        }
        runAllMatching();
      }}
      disabled={loading}
      className="w-full md:w-auto bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
    >
      {loading ? 'Starting...' : 'Run Batch Matching'}
    </button>
  </div>
)}

        {/* Results View */}
        {activeView === 'results' && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-2xl font-semibold mb-6 text-gray-900">View Match Results</h2>
            
            {/* Document Selector */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Select Document</label>
              <select
                value={selectedDocumentId}
                onChange={(e) => {
                  const docId = e.target.value;
                  setSelectedDocumentId(docId);
                  fetchProfileAndResults(docId); // Fetch profile and results on document selection
                }}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select a document</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.filename}
                  </option>
                ))}
              </select>
            </div>

            {/* Filter and Delete Buttons */}
            {/* Filter and Action Buttons */}
<div className="flex flex-wrap gap-4 mb-6 items-center justify-between">
  {/* Filter Buttons */}
  <div className="flex gap-2">
    <button
      onClick={() => setMatchResults(allMatches.filter(m => m.match_type === 'priority'))}
      className="px-4 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200"
      disabled={!profileId || loading}
    >
      Priority Only
    </button>
    <button
      onClick={() => setMatchResults(allMatches.filter(m => m.match_type === 'discovery'))}
      className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
      disabled={!profileId || loading}
    >
      Discovery Only
    </button>
    <button
      onClick={() => setMatchResults(allMatches)}
      className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200"
      disabled={!profileId || loading}
    >
      Show All
    </button>
  </div>
  
  {/* Action Buttons */}
  <div className="flex gap-2">
    {/* Download Dropdown */}
    <div className="relative inline-block text-left">
      <button
        onClick={() => document.getElementById('download-menu').classList.toggle('hidden')}
        disabled={loading || !profileId}
        className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
      >
        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        Download Excel
      </button>
      <div id="download-menu" className="hidden absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
        <div className="py-1" role="menu">
          <button
            onClick={() => {
              document.getElementById('download-menu').classList.add('hidden');
              downloadMatches('all');
            }}
            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            Download All Matches
          </button>
          <button
            onClick={() => {
              document.getElementById('download-menu').classList.add('hidden');
              downloadMatches('priority');
            }}
            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            Download Priority Only
          </button>
          <button
            onClick={() => {
              document.getElementById('download-menu').classList.add('hidden');
              downloadMatches('discovery');
            }}
            className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
          >
            Download Discovery Only
          </button>
        </div>
      </div>
    </div>
    
    <button
      onClick={deleteClientMatches}
      disabled={loading || !profileId}
      className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center"
    >
      <Trash2 className="mr-2" size={18} />
      Delete All
    </button>
  </div>
</div>

            {matchResults.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Prospect</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {matchResults.map((match) => (
                      <tr key={match.match_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="font-medium text-gray-900">{match.prospect_name}</div>
                            <div className="text-sm text-gray-500">{match.job_title}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{match.company_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                            match.match_type === 'priority' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {match.match_type === 'priority' ? '⭐ Priority' : 'Discovery'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                            {match.overall_score.toFixed(3)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(match.status)}`}>
                            {match.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <div className="flex space-x-3">
                            <button
                              onClick={() => fetchMatchDetail(match.match_id)}
                              className="text-purple-600 hover:text-purple-900 flex items-center"
                            >
                              <Eye size={16} className="mr-1" /> View
                            </button>
                            <button
                              onClick={() => openStatusModal(match)}
                              className="text-blue-600 hover:text-blue-900 flex items-center"
                            >
                              <Edit size={16} className="mr-1" /> Edit
                            </button>
                            <button
                              onClick={() => deleteMatch(match.match_id)}
                              className="text-red-600 hover:text-red-900 flex items-center"
                            >
                              <Trash2 size={16} className="mr-1" /> Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12">
                <Search className="mx-auto text-gray-400 mb-4" size={48} />
                <p className="text-gray-500">No matches found. Select a document to fetch results.</p>
              </div>
            )}
          </div>
        )}

        {/* Status Update Modal */}
        {showStatusModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="flex items-center justify-between p-6 border-b">
                <h3 className="text-lg font-semibold text-gray-900">Update Match Status</h3>
                <button onClick={() => setShowStatusModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X size={24} />
                </button>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
                  <select
                    value={updateStatusForm.status}
                    onChange={(e) => setUpdateStatusForm({...updateStatusForm, status: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="pending">Pending</option>
                    <option value="contacted">Contacted</option>
                    <option value="meeting_scheduled">Meeting Scheduled</option>
                    <option value="rejected">Rejected</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Notes</label>
                  <textarea
                    value={updateStatusForm.notes}
                    onChange={(e) => setUpdateStatusForm({...updateStatusForm, notes: e.target.value})}
                    rows={3}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Add any notes..."
                  />
                </div>
                {updateStatusForm.status === 'rejected' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Rejection Reason</label>
                    <input
                      type="text"
                      value={updateStatusForm.rejection_reason}
                      onChange={(e) => setUpdateStatusForm({...updateStatusForm, rejection_reason: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Why was this match rejected?"
                    />
                  </div>
                )}
              </div>
              <div className="flex justify-end space-x-3 p-6 border-t bg-gray-50">
                <button
                  onClick={() => setShowStatusModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100"
                >
                  Cancel
                </button>
                <button
                  onClick={updateMatchStatus}
                  disabled={loading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
                >
                  {loading ? 'Updating...' : 'Update Status'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Detail View Modal */}
        {showDetailModal && matchDetail && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
              <div className="flex items-center justify-between p-6 border-b">
                <h3 className="text-xl font-semibold text-gray-900">Match Details</h3>
                <button onClick={() => setShowDetailModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X size={24} />
                </button>
              </div>
              
              <div className="flex-1 overflow-y-auto p-6">
                {/* Match Overview */}
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mb-6">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Overall Score</p>
                      <p className="text-3xl font-bold text-blue-600">{matchDetail.overall_score.toFixed(3)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Match Rank</p>
                      <p className="text-3xl font-bold text-purple-600">#{matchDetail.match_rank}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1">Status</p>
                      <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${getStatusColor(matchDetail.status)}`}>
                        {matchDetail.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Score Breakdown */}
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4">Score Breakdown</h4>
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">Job Title Similarity</span>
                        <span className="text-sm font-semibold text-gray-900">{matchDetail.job_title_score.toFixed(3)}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{width: `${matchDetail.job_title_score * 100}%`}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">Business Area Similarity</span>
                        <span className="text-sm font-semibold text-gray-900">{matchDetail.business_area_score.toFixed(3)}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{width: `${matchDetail.business_area_score * 100}%`}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium text-gray-700">Activity Similarity</span>
                        <span className="text-sm font-semibold text-gray-900">{matchDetail.activity_score.toFixed(3)}</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-purple-600 h-2 rounded-full" style={{width: `${matchDetail.activity_score * 100}%`}}></div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Scrollable profile cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-h-[38rem] overflow-y-auto">
                  {/* Client card */}
                  <div className="border border-gray-200 rounded-lg p-6 flex flex-col">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center shrink-0">
                      <Users className="mr-2 text-blue-600" size={20} />
                      Client Profile
                    </h4>
                    <div className="space-y-3 overflow-y-auto">
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Profile ID</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.client.client_id}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Key Interests</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.client.key_interests || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Target Job Titles</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">
                          {Array.isArray(matchDetail.client.target_job_titles)
                            ? matchDetail.client.target_job_titles.join(', ')
                            : matchDetail.client.target_job_titles || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Business Areas</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.client.business_areas || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Company Activities</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.client.company_main_activities || 'N/A'}</p>
                      </div>
                      {matchDetail.client.companies_to_exclude && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase">Excluded Companies</p>
                          <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.client.companies_to_exclude}</p>
                        </div>
                      )}
                      {matchDetail.client.excluded_countries && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase">Excluded Countries</p>
                          <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.client.excluded_countries}</p>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Prospect card */}
                  <div className="border border-gray-200 rounded-lg p-6 flex flex-col">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center shrink-0">
                      <Users className="mr-2 text-green-600" size={20} />
                      Prospect Profile
                    </h4>
                    <div className="space-y-3 overflow-y-auto">
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Name</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">
                          {[matchDetail.prospect.first_name, matchDetail.prospect.last_name].filter(Boolean).join(' ') || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Email</p>
                        <p className="text-sm text-blue-600 mt-1 break-all">{matchDetail.prospect.attendee_email || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Job Title</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.prospect.job_title || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Company</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.prospect.company_name}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Location</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">
                          {[matchDetail.prospect.country, matchDetail.prospect.region].filter(Boolean).join(', ') || 'N/A'}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Job Function</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.prospect.job_function || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Responsibility</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.prospect.responsibility || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase">Company Activity</p>
                        <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.prospect.company_main_activity || 'N/A'}</p>
                      </div>
                      {matchDetail.prospect.area_of_interests && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase">Areas of Interest</p>
                          <p className="text-sm text-gray-900 mt-1 break-words">{matchDetail.prospect.area_of_interests}</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Match Metadata */}
                {(matchDetail.notes || matchDetail.matched_at) && (
                  <div className="mt-6 border border-gray-200 rounded-lg p-6">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4">Match Information</h4>
                    <div className="space-y-3">
                      {matchDetail.matched_at && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase">Matched At</p>
                          <p className="text-sm text-gray-900 mt-1">{new Date(matchDetail.matched_at).toLocaleString()}</p>
                        </div>
                      )}
                      {matchDetail.notes && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase">Notes</p>
                          <p className="text-sm text-gray-900 mt-1">{matchDetail.notes}</p>
                        </div>
                      )}
                      {matchDetail.rejection_reason && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase">Rejection Reason</p>
                          <p className="text-sm text-red-600 mt-1">{matchDetail.rejection_reason}</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex justify-end space-x-3 p-6 border-t bg-gray-50">
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MatchingDashboard;






