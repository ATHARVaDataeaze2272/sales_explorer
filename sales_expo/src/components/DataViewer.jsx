
// import { useState, useEffect } from 'react';
// import {
//   Users,
//   Database,
//   FileText,
//   Search,
//   Filter,
//   RefreshCw,
//   Edit2,
//   X,
//   Loader2,
//   Save,
//   Building2,
//   Target,
//   Briefcase,
//   ChevronDown,
//   Check,
// } from 'lucide-react';

// function DataViewer() {
//   const [dataType, setDataType] = useState('clients');
//   const [documents, setDocuments] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [selectedDocument, setSelectedDocument] = useState(null);
//   const [companies, setCompanies] = useState([]);
//   const [profile, setProfile] = useState(null);
//   const [editingCompany, setEditingCompany] = useState(null);
//   const [editingProfile, setEditingProfile] = useState(false);
//   const [searchTerm, setSearchTerm] = useState('');
//   const [filterCountry, setFilterCountry] = useState('');

//   const fetchDocuments = async () => {
//     setLoading(true);
//     try {
//       const response = await fetch(`http://localhost:8000/api/documents?document_type=${dataType}`);
//       const data = await response.json();
//       setDocuments(data.documents || []);
//     } catch (err) {
//       console.error('Failed to fetch documents:', err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const fetchDocumentDetails = async (docId) => {
//     try {
//       const response = await fetch(`http://localhost:8000/api/documents/${docId}`);
//       const data = await response.json();
//       setSelectedDocument(data.document);
//       setCompanies(data.companies || []);
      
//       // Fetch profile data
//       const profileEndpoint = dataType === 'clients' 
//         ? `http://localhost:8000/api/profiles/client/${docId}`
//         : `http://localhost:8000/api/profiles/prospect/${docId}`;
      
//       const profileResponse = await fetch(profileEndpoint);
//       const profileData = await profileResponse.json();
//       setProfile(profileData.profile);
//     } catch (err) {
//       console.error('Failed to fetch document details:', err);
//     }
//   };

//   const updateCompany = async (companyId, updatedData) => {
//     try {
//       const endpoint = dataType === 'clients'
//         ? `http://localhost:8000/api/companies/client/${companyId}`
//         : `http://localhost:8000/api/companies/prospect/${companyId}`;
      
//       const response = await fetch(endpoint, {
//         method: 'PUT',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(updatedData),
//       });

//       if (!response.ok) throw new Error('Failed to update company');

//       if (selectedDocument) {
//         fetchDocumentDetails(selectedDocument.id);
//       }
//       setEditingCompany(null);
//     } catch (err) {
//       console.error('Failed to update company:', err);
//       alert('Failed to update company data');
//     }
//   };

//   const updateProfile = async (profileId, updatedData) => {
//     try {
//       const endpoint = dataType === 'clients'
//         ? `http://localhost:8000/api/profiles/client/${profileId}`
//         : `http://localhost:8000/api/profiles/prospect/${profileId}`;
      
//       const response = await fetch(endpoint, {
//         method: 'PUT',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(updatedData),
//       });

//       if (!response.ok) throw new Error('Failed to update profile');

//       if (selectedDocument) {
//         fetchDocumentDetails(selectedDocument.id);
//       }
//       setEditingProfile(false);
//     } catch (err) {
//       console.error('Failed to update profile:', err);
//       alert('Failed to update profile data');
//     }
//   };

//   const deleteCompany = async (companyId) => {
//     if (!confirm('Are you sure you want to delete this company?')) return;

//     try {
//       const endpoint = dataType === 'clients'
//         ? `http://localhost:8000/api/companies/client/${companyId}`
//         : `http://localhost:8000/api/companies/prospect/${companyId}`;
      
//       const response = await fetch(endpoint, {
//         method: 'DELETE',
//       });

//       if (!response.ok) throw new Error('Failed to delete company');

//       if (selectedDocument) {
//         fetchDocumentDetails(selectedDocument.id);
//       }
//     } catch (err) {
//       console.error('Failed to delete company:', err);
//       alert('Failed to delete company');
//     }
//   };

//   const filteredCompanies = companies.filter(company => {
//     const matchesSearch =
//       !searchTerm ||
//       company.company_name?.toLowerCase().includes(searchTerm.toLowerCase());

//     const matchesCountry =
//       !filterCountry || company.country?.toLowerCase().includes(filterCountry.toLowerCase());

//     return matchesSearch && matchesCountry;
//   });

//   useEffect(() => {
//     fetchDocuments();
//   }, [dataType]);

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6 space-y-6">
//       {/* Type Selector */}
//       <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//         <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
//           <Database className="w-5 h-5 text-blue-600" />
//           Select Data Type
//         </h2>
//         <div className="flex gap-4">
//           <button
//             onClick={() => {
//               setDataType('clients');
//               setSelectedDocument(null);
//               setCompanies([]);
//               setProfile(null);
//             }}
//             className={`flex-1 px-6 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 ${
//               dataType === 'clients'
//                 ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg'
//                 : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
//             }`}
//           >
//             <Users className="w-5 h-5" />
//             <div className="text-left">
//               <div className="font-bold">Clients</div>
//               <div className="text-xs opacity-90">View & edit client data</div>
//             </div>
//           </button>
//           <button
//             onClick={() => {
//               setDataType('prospects');
//               setSelectedDocument(null);
//               setCompanies([]);
//               setProfile(null);
//             }}
//             className={`flex-1 px-6 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 ${
//               dataType === 'prospects'
//                 ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
//                 : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
//             }`}
//           >
//             <Users className="w-5 h-5" />
//             <div className="text-left">
//               <div className="font-bold">Prospects</div>
//               <div className="text-xs opacity-90">View & edit prospect data</div>
//             </div>
//           </button>
//         </div>
//         <button
//           onClick={fetchDocuments}
//           disabled={loading}
//           className="w-full mt-4 px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-cyan-700 shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
//         >
//           {loading ? (
//             <>
//               <Loader2 className="w-5 h-5 animate-spin" />
//               Loading...
//             </>
//           ) : (
//             <>
//               <RefreshCw className="w-5 h-5" />
//               Load {dataType === 'clients' ? 'Client' : 'Prospect'} Documents
//             </>
//           )}
//         </button>
//       </div>

//       {/* Documents List */}
//       {documents.length > 0 && !selectedDocument && (
//         <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//           <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
//             <Database className="w-5 h-5 text-blue-600" />
//             Available Documents ({documents.length})
//           </h2>
//           <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
//             {documents.map(doc => (
//               <div
//                 key={doc.id}
//                 className="border border-gray-200 rounded-xl p-4 hover:shadow-lg transition-all cursor-pointer hover:border-blue-300 bg-gradient-to-br from-white to-blue-50"
//                 onClick={() => fetchDocumentDetails(doc.id)}
//               >
//                 <div className="flex items-start gap-3 mb-3">
//                   <div className="p-2 bg-blue-100 rounded-lg">
//                     <FileText className="w-4 h-4 text-blue-600" />
//                   </div>
//                   <div className="flex-1 min-w-0">
//                     <p className="font-semibold text-gray-900 text-sm truncate">{doc.filename}</p>
//                     <p className="text-xs text-gray-500 mt-1">
//                       {new Date(doc.uploaded_at).toLocaleDateString()}
//                     </p>
//                   </div>
//                 </div>
//                 <div className="flex items-center justify-between text-xs">
//                   <span
//                     className={`px-2 py-1 rounded-full ${
//                       doc.status === 'completed'
//                         ? 'bg-green-100 text-green-700'
//                         : 'bg-gray-100 text-gray-700'
//                     }`}
//                   >
//                     {doc.status}
//                   </span>
//                   <span className="font-semibold text-gray-700">
//                     {doc.entities_extracted} records
//                   </span>
//                 </div>
//               </div>
//             ))}
//           </div>
//         </div>
//       )}

//       {/* Document Details View */}
//       {selectedDocument && (
//         <div className="space-y-6">
//           {/* Document Header */}
//           <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//             <div className="flex items-center justify-between">
//               <div className="flex items-center gap-3">
//                 <div className="p-2 bg-blue-100 rounded-lg">
//                   <FileText className="w-5 h-5 text-blue-600" />
//                 </div>
//                 <div>
//                   <h2 className="text-lg font-bold text-gray-900">{selectedDocument.filename}</h2>
//                   <p className="text-sm text-gray-600">
//                     {companies.length} companies • Uploaded{' '}
//                     {new Date(selectedDocument.uploaded_at).toLocaleDateString()}
//                   </p>
//                 </div>
//               </div>
//               <button
//                 onClick={() => {
//                   setSelectedDocument(null);
//                   setCompanies([]);
//                   setProfile(null);
//                   setEditingCompany(null);
//                   setEditingProfile(false);
//                 }}
//                 className="px-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all"
//               >
//                 Back to Documents
//               </button>
//             </div>
//           </div>

//           {/* Profile Information Card */}
//           {profile && (
//             <ProfileCard
//               profile={profile}
//               dataType={dataType}
//               isEditing={editingProfile}
//               onEdit={() => setEditingProfile(true)}
//               onSave={(data) => updateProfile(profile.id, data)}
//               onCancel={() => setEditingProfile(false)}
//             />
//           )}

//           {/* Search & Filter */}
//           <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//             <h3 className="text-md font-bold text-gray-900 mb-4 flex items-center gap-2">
//               <Building2 className="w-4 h-4 text-blue-600" />
//               Company Records
//             </h3>
//             <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//               <div className="relative">
//                 <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
//                 <input
//                   type="text"
//                   placeholder="Search by company name..."
//                   value={searchTerm}
//                   onChange={e => setSearchTerm(e.target.value)}
//                   className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
//                 />
//               </div>
//               <div className="relative">
//                 <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
//                 <input
//                   type="text"
//                   placeholder="Filter by country..."
//                   value={filterCountry}
//                   onChange={e => setFilterCountry(e.target.value)}
//                   className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
//                 />
//               </div>
//             </div>
//           </div>

//           {/* Companies Table */}
//           <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
//             <div className="overflow-x-auto">
//               <table className="w-full">
//                 <thead className="bg-gradient-to-r from-blue-50 to-cyan-50">
//                   <tr>
//                     <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
//                       Company Name
//                     </th>
//                     <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
//                       Country
//                     </th>
//                     <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
//                       City
//                     </th>
//                     <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">
//                       Actions
//                     </th>
//                   </tr>
//                 </thead>
//                 <tbody>
//                   {filteredCompanies.length === 0 ? (
//                     <tr>
//                       <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
//                         No companies match the current filters
//                       </td>
//                     </tr>
//                   ) : (
//                     filteredCompanies.map((company, idx) => (
//                       <CompanyRow
//                         key={company.id}
//                         company={company}
//                         isEven={idx % 2 === 0}
//                         isEditing={editingCompany?.id === company.id}
//                         onEdit={() => setEditingCompany(company)}
//                         onSave={data => updateCompany(company.id, data)}
//                         onCancel={() => setEditingCompany(null)}
//                         onDelete={() => deleteCompany(company.id)}
//                       />
//                     ))
//                   )}
//                 </tbody>
//               </table>
//             </div>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// }

// function ProfileCard({ profile, dataType, isEditing, onEdit, onSave, onCancel }) {
//   const [formData, setFormData] = useState({
//     business_areas: profile.business_areas || '',
//     company_main_activities: profile.company_main_activities || '',
//     key_interests: profile.key_interests || '',
//     target_job_titles: profile.target_job_titles || [],
//     companies_to_exclude: profile.companies_to_exclude || '',
//     excluded_countries: profile.excluded_countries || '',
//   });

//   const handleSave = () => {
//     onSave(formData);
//   };

//   return (
//     <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//       <div className="flex items-center justify-between mb-6">
//         <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
//           <Target className="w-5 h-5 text-purple-600" />
//           Profile Information
//         </h3>
//         {!isEditing ? (
//           <button
//             onClick={onEdit}
//             className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all flex items-center gap-2"
//           >
//             <Edit2 className="w-4 h-4" />
//             Edit Profile
//           </button>
//         ) : (
//           <div className="flex gap-2">
//             <button
//               onClick={handleSave}
//               className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-all flex items-center gap-2"
//             >
//               <Save className="w-4 h-4" />
//               Save
//             </button>
//             <button
//               onClick={onCancel}
//               className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-400 transition-all flex items-center gap-2"
//             >
//               <X className="w-4 h-4" />
//               Cancel
//             </button>
//           </div>
//         )}
//       </div>

//       <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
//         {/* Business Areas */}
//         <div>
//           <label className="block text-sm font-semibold text-gray-700 mb-2">
//             <Briefcase className="w-4 h-4 inline mr-1" />
//             Business Areas
//           </label>
//           {isEditing ? (
//             <MultiSelectDropdown
//               value={formData.business_areas}
//               onChange={(val) => setFormData({ ...formData, business_areas: val })}
//               placeholder="Select business areas..."
//             />
//           ) : (
//             <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg min-h-[42px]">
//               {profile.business_areas || 'Not specified'}
//             </p>
//           )}
//         </div>

//         {/* Company Main Activities */}
//         <div>
//           <label className="block text-sm font-semibold text-gray-700 mb-2">
//             <Building2 className="w-4 h-4 inline mr-1" />
//             Company Main Activities
//           </label>
//           {isEditing ? (
//             <MultiSelectDropdown
//               value={formData.company_main_activities}
//               onChange={(val) => setFormData({ ...formData, company_main_activities: val })}
//               placeholder="Select activities..."
//             />
//           ) : (
//             <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg min-h-[42px]">
//               {profile.company_main_activities || 'Not specified'}
//             </p>
//           )}
//         </div>

//         {/* Key Interests */}
//         <div className="md:col-span-2">
//           <label className="block text-sm font-semibold text-gray-700 mb-2">
//             Key Interests
//           </label>
//           {isEditing ? (
//             <textarea
//               value={formData.key_interests}
//               onChange={(e) => setFormData({ ...formData, key_interests: e.target.value })}
//               className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
//               rows={3}
//             />
//           ) : (
//             <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
//               {profile.key_interests || 'Not specified'}
//             </p>
//           )}
//         </div>

//         {/* Companies to Exclude */}
//         <div>
//           <label className="block text-sm font-semibold text-gray-700 mb-2">
//             Companies to Exclude
//           </label>
//           {isEditing ? (
//             <textarea
//               value={formData.companies_to_exclude}
//               onChange={(e) => setFormData({ ...formData, companies_to_exclude: e.target.value })}
//               className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
//               rows={2}
//             />
//           ) : (
//             <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
//               {profile.companies_to_exclude || 'None'}
//             </p>
//           )}
//         </div>

//         {/* Excluded Countries */}
//         <div>
//           <label className="block text-sm font-semibold text-gray-700 mb-2">
//             Excluded Countries
//           </label>
//           {isEditing ? (
//             <textarea
//               value={formData.excluded_countries}
//               onChange={(e) => setFormData({ ...formData, excluded_countries: e.target.value })}
//               className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
//               rows={2}
//             />
//           ) : (
//             <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
//               {profile.excluded_countries || 'None'}
//             </p>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// }

// function MultiSelectDropdown({ value, onChange, placeholder }) {
//   const [isOpen, setIsOpen] = useState(false);
//   const [selectedItems, setSelectedItems] = useState([]);

//   useEffect(() => {
//     if (value) {
//       setSelectedItems(value.split(',').map(item => item.trim()).filter(Boolean));
//     }
//   }, [value]);

//   const options = [
//     'ADVISORY/STRATEGY/PLANNING/PERFORMANCE',
//     'BUSINESS DEVELOPMENT/SALES/PRODUCT MGMT',
//     'CLIENT/CUSTOMER SERVICE',
//     'CONTENT DEVELOPMENT/DISTRIBUTION',
//     'FINANCE/ACCOUNTING',
//     'GOVERNMENT/REGULATORY',
//     'HR/TALENT/DIVERSITY',
//     'INFORMATION/DIGITAL/ANALYTICS',
//     'INVESTMENT/VENTURE CAPITAL/M&A',
//     'LEGAL/IP',
//     'MANUFACTURING',
//     'MARKETING/ADVERTISING/PR',
//     'OPERATIONS MGMT',
//     'PRESS/MEDIA',
//     'RESEARCH/DEVELOPMENT/INNOVATION',
//     'SOFTWARE/DEVELOPER',
//     'SOURCING/PROCUREMENT',
//     'SUPPLY CHAIN MGMT/DISTRIBUTION',
//     'TECHNICAL/ENGINEERING',
//     'TRAINING/EDUCATION',
//     'Other',
//   ];

//   const toggleItem = (item) => {
//     let newSelected;
//     if (selectedItems.includes(item)) {
//       newSelected = selectedItems.filter(i => i !== item);
//     } else {
//       newSelected = [...selectedItems, item];
//     }
//     setSelectedItems(newSelected);
//     onChange(newSelected.join(', '));
//   };

//   return (
//     <div className="relative">
//       <button
//         type="button"
//         onClick={() => setIsOpen(!isOpen)}
//         className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-left flex items-center justify-between"
//       >
//         <span className="text-sm text-gray-700 truncate">
//           {selectedItems.length > 0
//             ? `${selectedItems.length} selected`
//             : placeholder}
//         </span>
//         <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
//       </button>

//       {isOpen && (
//         <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
//           {options.map((option) => (
//             <div
//               key={option}
//               onClick={() => toggleItem(option)}
//               className="px-3 py-2 hover:bg-blue-50 cursor-pointer flex items-center justify-between text-sm"
//             >
//               <span className={selectedItems.includes(option) ? 'font-semibold text-blue-600' : 'text-gray-700'}>
//                 {option}
//               </span>
//               {selectedItems.includes(option) && (
//                 <Check className="w-4 h-4 text-blue-600" />
//               )}
//             </div>
//           ))}
//         </div>
//       )}

//       {selectedItems.length > 0 && (
//         <div className="mt-2 flex flex-wrap gap-2">
//           {selectedItems.map((item) => (
//             <span
//               key={item}
//               className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs"
//             >
//               {item}
//               <button
//                 onClick={() => toggleItem(item)}
//                 className="hover:bg-blue-200 rounded-full p-0.5"
//               >
//                 <X className="w-3 h-3" />
//               </button>
//             </span>
//           ))}
//         </div>
//       )}
//     </div>
//   );
// }

// function CompanyRow({ company, isEven, isEditing, onEdit, onSave, onCancel, onDelete }) {
//   const [formData, setFormData] = useState({
//     company_name: company.company_name || '',
//     country: company.country || '',
//     city: company.city || '',
//   });

//   const handleSave = () => {
//     onSave(formData);
//   };

//   return (
//     <tr className={`${isEven ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors`}>
//       <td className="px-6 py-4">
//         {isEditing ? (
//           <input
//             type="text"
//             value={formData.company_name}
//             onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
//             className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
//           />
//         ) : (
//           <span className="text-sm font-medium text-gray-900">{company.company_name}</span>
//         )}
//       </td>
//       <td className="px-6 py-4">
//         {isEditing ? (
//           <input
//             type="text"
//             value={formData.country}
//             onChange={(e) => setFormData({ ...formData, country: e.target.value })}
//             className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
//           />
//         ) : (
//           <span className="text-sm text-gray-700">{company.country}</span>
//         )}
//       </td>
//       <td className="px-6 py-4">
//         {isEditing ? (
//           <input
//             type="text"
//             value={formData.city}
//             onChange={(e) => setFormData({ ...formData, city: e.target.value })}
//             className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
//           />
//         ) : (
//           <span className="text-sm text-gray-700">{company.city || '-'}</span>
//         )}
//       </td>
//       <td className="px-6 py-4">
//         {isEditing ? (
//           <div className="flex gap-2">
//             <button
//               onClick={handleSave}
//               className="p-1 bg-green-600 text-white rounded hover:bg-green-700"
//             >
//               <Save className="w-4 h-4" />
//             </button>
//             <button
//               onClick={onCancel}
//               className="p-1 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
//             >
//               <X className="w-4 h-4" />
//             </button>
//           </div>
//         ) : (
//           <div className="flex gap-2">
//             <button
//               onClick={onEdit}
//               className="p-1 bg-blue-600 text-white rounded hover:bg-blue-700"
//             >
//               <Edit2 className="w-4 h-4" />
//             </button>
//             <button
//               onClick={onDelete}
//               className="p-1 bg-red-600 text-white rounded hover:bg-red-700"
//             >
//               <X className="w-4 h-4" />
//             </button>
//           </div>
//         )}
//       </td>
//     </tr>
//   );
// }

// export default DataViewer;




















import { useState, useEffect } from 'react';
import { FileText, Trash2, Edit, Search, Loader2, AlertCircle, Users, Database, RefreshCw, Save, X, Building2, Target, Briefcase, ChevronDown, Check, Filter } from 'lucide-react';

function DataViewer() {
  const [dataType, setDataType] = useState('clients');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [filterCountry, setFilterCountry] = useState('');
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [documentDetails, setDocumentDetails] = useState(null);
  const [profile, setProfile] = useState(null);
  const [editingCompany, setEditingCompany] = useState(null);
  const [editingProfile, setEditingProfile] = useState(null);

  useEffect(() => {
    fetchDocuments();
  }, [dataType]);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/documents?document_type=${dataType}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to fetch documents');
      console.log('Fetched documents:', data);
      setDocuments(data.documents || []);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchDocumentDetails = async (documentId) => {
    setLoading(true);
    setError(null);
    try {
      // Fetch document details
      const response = await fetch(`http://localhost:8000/api/documents/${documentId}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to fetch document details');
      console.log('Document details:', data);
      setDocumentDetails(data);
      setSelectedDocument(documentId);

      // Fetch profile data for client documents
      if (data.document.document_type === 'clients') {
        try {
          const profileResponse = await fetch(`http://localhost:8000/api/profiles/client/${documentId}`);
          const profileData = await profileResponse.json();
          if (!profileResponse.ok) throw new Error(profileData.detail || 'Failed to fetch profile');
          console.log('Profile data:', profileData);
          setProfile(profileData.profile || null);
        } catch (profileErr) {
          console.error('Error fetching profile:', profileErr);
          setError(`Failed to load profile: ${profileErr.message}`);
          setProfile(null);
        }
      } else {
        setProfile(null);
      }
    } catch (err) {
      console.error('Error fetching document details:', err);
      setError(err.message);
      setDocumentDetails(null);
      setSelectedDocument(null);
    } finally {
      setLoading(false);
    }
  };

  const deleteDocument = async (documentId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/documents/${documentId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to delete document');
      setDocuments(documents.filter((doc) => doc.id !== documentId));
      if (selectedDocument === documentId) {
        setSelectedDocument(null);
        setDocumentDetails(null);
        setProfile(null);
      }
    } catch (err) {
      console.error('Error deleting document:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const searchCompanies = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/companies/search?company_name=${encodeURIComponent(search)}&document_type=${dataType}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to search companies');
      console.log('Search results:', data);
      setDocumentDetails({ document: {}, companies: data.companies });
      setProfile(null);
    } catch (err) {
      console.error('Error searching companies:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateClientCompany = async (companyId, updatedData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/companies/client/${companyId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to update company');
      console.log('Updated company:', data);
      setDocumentDetails({
        ...documentDetails,
        companies: documentDetails.companies.map((c) =>
          c.id === companyId ? { ...c, ...data.company } : c
        ),
      });
      setEditingCompany(null);
    } catch (err) {
      console.error('Error updating company:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteClientCompany = async (companyId) => {
    if (!window.confirm('Are you sure you want to delete this company?')) return;
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/companies/client/${companyId}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to delete company');
      setDocumentDetails({
        ...documentDetails,
        companies: documentDetails.companies.filter((c) => c.id !== companyId),
        companies_count: documentDetails.companies_count - 1,
      });
    } catch (err) {
      console.error('Error deleting company:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateClientProfile = async (profileId, updatedData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`http://localhost:8000/api/profiles/client/${profileId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updatedData),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to update profile');
      console.log('Updated profile:', data);
      setProfile(data.profile);
      setEditingProfile(null);
    } catch (err) {
      console.error('Error updating profile:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredCompanies = documentDetails?.companies?.filter(company => {
    const matchesSearch = !search || company.company_name?.toLowerCase().includes(search.toLowerCase());
    const matchesCountry = !filterCountry || company.country?.toLowerCase().includes(filterCountry.toLowerCase());
    return matchesSearch && matchesCountry;
  }) || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6 space-y-6">
      {/* Type Selector */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <Database className="w-5 h-5 text-blue-600" />
          Select Data Type
        </h2>
        <div className="flex gap-4">
          <button
            onClick={() => {
              setDataType('clients');
              setSelectedDocument(null);
              setDocumentDetails(null);
              setProfile(null);
              setEditingCompany(null);
              setEditingProfile(null);
            }}
            className={`flex-1 px-6 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 ${
              dataType === 'clients'
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Users className="w-5 h-5" />
            <div className="text-left">
              <div className="font-bold">Clients</div>
              <div className="text-xs opacity-90">View & edit client data</div>
            </div>
          </button>
          <button
            onClick={() => {
              setDataType('prospects');
              setSelectedDocument(null);
              setDocumentDetails(null);
              setProfile(null);
              setEditingCompany(null);
              setEditingProfile(null);
            }}
            className={`flex-1 px-6 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 ${
              dataType === 'prospects'
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Users className="w-5 h-5" />
            <div className="text-left">
              <div className="font-bold">Prospects</div>
              <div className="text-xs opacity-90">View & edit prospect data</div>
            </div>
          </button>
        </div>
        <button
          onClick={fetchDocuments}
          disabled={loading}
          className="w-full mt-4 px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-cyan-700 shadow-lg transition-all disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Loading...
            </>
          ) : (
            <>
              <RefreshCw className="w-5 h-5" />
              Load {dataType === 'clients' ? 'Client' : 'Prospect'} Documents
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg shadow-sm">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-800">Error</p>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Documents List */}
      {documents.length > 0 && !selectedDocument && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-blue-600" />
            Available Documents ({documents.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map(doc => (
              <div
                key={doc.id}
                className="border border-gray-200 rounded-xl p-4 hover:shadow-lg transition-all cursor-pointer hover:border-blue-300 bg-gradient-to-br from-white to-blue-50"
                onClick={() => fetchDocumentDetails(doc.id)}
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <FileText className="w-4 h-4 text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-900 text-sm truncate">{doc.filename}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span
                    className={`px-2 py-1 rounded-full ${
                      doc.status === 'completed'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {doc.status}
                  </span>
                  <span className="font-semibold text-gray-700">
                    {doc.entities_extracted} records
                  </span>
                </div>
                <div className="mt-2 flex justify-end">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteDocument(doc.id);
                    }}
                    className="p-1.5 hover:bg-red-100 rounded-lg"
                    title="Delete document"
                  >
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Document Details View */}
      {documentDetails && (
        <div className="space-y-6">
          {/* Document Header */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <FileText className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-gray-900">{documentDetails.document.filename}</h2>
                  <p className="text-sm text-gray-600">
                    {documentDetails.companies_count || documentDetails.companies?.length || 0} {dataType === 'clients' ? 'companies' : 'records'} • Uploaded{' '}
                    {new Date(documentDetails.document.uploaded_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <button
                onClick={() => {
                  setSelectedDocument(null);
                  setDocumentDetails(null);
                  setProfile(null);
                  setEditingCompany(null);
                  setEditingProfile(null);
                }}
                className="px-4 py-2 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all"
              >
                Back to Documents
              </button>
            </div>
          </div>

          {/* Profile Information Card */}
          {profile && dataType === 'clients' && (
            <ProfileCard
              profile={profile}
              isEditing={editingProfile}
              onEdit={() => setEditingProfile(profile)}
              onSave={(data) => updateClientProfile(profile.id, data)}
              onCancel={() => setEditingProfile(null)}
            />
          )}

          {/* Search & Filter */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h3 className="text-md font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Building2 className="w-4 h-4 text-blue-600" />
              {dataType === 'clients' ? 'Client Companies' : 'Prospect Records'}
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by company name..."
                  value={search}
                  onChange={e => setSearch(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>
              <div className="relative">
                <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Filter by country..."
                  value={filterCountry}
                  onChange={e => setFilterCountry(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                />
              </div>
            </div>
          </div>

          {/* Companies/Prospects Table */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
            <div className="overflow-x-auto">
              {dataType === 'clients' ? (
                <table className="w-full text-sm text-left text-gray-700">
                  <thead className="text-xs text-gray-700 uppercase bg-gradient-to-r from-blue-50 to-cyan-50">
                    <tr>
                      <th className="px-6 py-4">Company Name</th>
                      <th className="px-6 py-4">Country</th>
                      <th className="px-6 py-4">City</th>
                      <th className="px-6 py-4">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCompanies.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                          No companies match the current filters
                        </td>
                      </tr>
                    ) : (
                      filteredCompanies.map((company, idx) => (
                        <CompanyRow
                          key={company.id}
                          company={company}
                          isEven={idx % 2 === 0}
                          isEditing={editingCompany?.id === company.id}
                          onEdit={() => setEditingCompany(company)}
                          onSave={data => updateClientCompany(company.id, data)}
                          onCancel={() => setEditingCompany(null)}
                          onDelete={() => deleteClientCompany(company.id)}
                        />
                      ))
                    )}
                  </tbody>
                </table>
              ) : (
                <table className="w-full text-sm text-left text-gray-700">
                  <thead className="text-xs text-gray-700 uppercase bg-gradient-to-r from-purple-50 to-pink-50">
                    <tr>
                      <th className="px-6 py-4">Reg ID</th>
                      <th className="px-6 py-4">Reg Status</th>
                      <th className="px-6 py-4">Create Account Date</th>
                      <th className="px-6 py-4">First Name</th>
                      <th className="px-6 py-4">Last Name</th>
                      <th className="px-6 py-4">Second Last Name</th>
                      <th className="px-6 py-4">Email</th>
                      <th className="px-6 py-4">Mobile</th>
                      <th className="px-6 py-4">Company</th>
                      <th className="px-6 py-4">Job Title</th>
                      <th className="px-6 py-4">Country</th>
                      <th className="px-6 py-4">Region</th>
                      <th className="px-6 py-4">Continent</th>
                      <th className="px-6 py-4">Pass Type</th>
                      <th className="px-6 py-4">Networking / Show Me</th>
                      <th className="px-6 py-4">Enhanced Networking</th>
                      <th className="px-6 py-4">Job Function</th>
                      <th className="px-6 py-4">Responsibility</th>
                      <th className="px-6 py-4">Company Main Activity</th>
                      <th className="px-6 py-4">Area of Interests</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredCompanies.map((prospect, idx) => (
                      <tr key={prospect.id} className={`${idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'} hover:bg-purple-50 transition-colors`}>
                        <td className="px-6 py-4">{prospect.reg_id || '-'}</td>
                        <td className="px-6 py-4">{prospect.reg_status || '-'}</td>
                        <td className="px-6 py-4">{prospect.create_account_date ? new Date(prospect.create_account_date).toLocaleDateString() : '-'}</td>
                        <td className="px-6 py-4">{prospect.first_name || '-'}</td>
                        <td className="px-6 py-4">{prospect.last_name || '-'}</td>
                        <td className="px-6 py-4">{prospect.second_last_name || '-'}</td>
                        <td className="px-6 py-4">{prospect.attendee_email || '-'}</td>
                        <td className="px-6 py-4">{prospect.mobile || '-'}</td>
                        <td className="px-6 py-4">{prospect.company_name || '-'}</td>
                        <td className="px-6 py-4">{prospect.job_title || '-'}</td>
                        <td className="px-6 py-4">{prospect.country || '-'}</td>
                        <td className="px-6 py-4">{prospect.region || '-'}</td>
                        <td className="px-6 py-4">{prospect.continent || '-'}</td>
                        <td className="px-6 py-4">{prospect.pass_type || '-'}</td>
                        <td className="px-6 py-4">{prospect.networking_show_me || '-'}</td>
                        <td className="px-6 py-4">{prospect.enhanced_networking || '-'}</td>
                        <td className="px-6 py-4">{prospect.job_function || '-'}</td>
                        <td className="px-6 py-4">{prospect.responsibility || '-'}</td>
                        <td className="px-6 py-4">{prospect.company_main_activity || '-'}</td>
                        <td className="px-6 py-4">{prospect.area_of_interests || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ProfileCard({ profile, isEditing, onEdit, onSave, onCancel }) {
  const [formData, setFormData] = useState({
    business_areas: profile.business_areas || '',
    company_main_activities: profile.company_main_activities || '',
    key_interests: profile.key_interests || '',
    target_job_titles: profile.target_job_titles || [],
    companies_to_exclude: profile.companies_to_exclude || '',
    excluded_countries: profile.excluded_countries || '',
  });

  const handleSave = () => {
    onSave(formData);
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
          <Target className="w-5 h-5 text-purple-600" />
          Profile Information
        </h3>
        {!isEditing ? (
          <button
            onClick={onEdit}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all flex items-center gap-2"
          >
            <Edit className="w-4 h-4" />
            Edit Profile
          </button>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-all flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
            <button
              onClick={onCancel}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-400 transition-all flex items-center gap-2"
            >
              <X className="w-4 h-4" />
              Cancel
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Business Areas */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            <Briefcase className="w-4 h-4 inline mr-1" />
            Business Areas
          </label>
          {isEditing ? (
            <MultiSelectDropdown
              value={formData.business_areas}
              onChange={(val) => setFormData({ ...formData, business_areas: val })}
              placeholder="Select business areas..."
            />
          ) : (
            <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg min-h-[42px]">
              {profile.business_areas || 'Not specified'}
            </p>
          )}
        </div>

        {/* Company Main Activities */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            <Building2 className="w-4 h-4 inline mr-1" />
            Company Main Activities
          </label>
          {isEditing ? (
            <MultiSelectDropdown
              value={formData.company_main_activities}
              onChange={(val) => setFormData({ ...formData, company_main_activities: val })}
              placeholder="Select activities..."
            />
          ) : (
            <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg min-h-[42px]">
              {profile.company_main_activities || 'Not specified'}
            </p>
          )}
        </div>

        {/* Key Interests */}
        <div className="md:col-span-2">
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Key Interests
          </label>
          {isEditing ? (
            <textarea
              value={formData.key_interests}
              onChange={(e) => setFormData({ ...formData, key_interests: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          ) : (
            <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
              {profile.key_interests || 'Not specified'}
            </p>
          )}
        </div>

        {/* Companies to Exclude */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Companies to Exclude
          </label>
          {isEditing ? (
            <textarea
              value={formData.companies_to_exclude}
              onChange={(e) => setFormData({ ...formData, companies_to_exclude: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows={2}
            />
          ) : (
            <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
              {profile.companies_to_exclude || 'None'}
            </p>
          )}
        </div>

        {/* Excluded Countries */}
        <div>
          <label className="block text-sm font-semibold text-gray-700 mb-2">
            Excluded Countries
          </label>
          {isEditing ? (
            <textarea
              value={formData.excluded_countries}
              onChange={(e) => setFormData({ ...formData, excluded_countries: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows={2}
            />
          ) : (
            <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
              {profile.excluded_countries || 'None'}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function MultiSelectDropdown({ value, onChange, placeholder }) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);

  useEffect(() => {
    if (value) {
      setSelectedItems(value.split(',').map(item => item.trim()).filter(Boolean));
    } else {
      setSelectedItems([]);
    }
  }, [value]);

  const options = [
    'ADVISORY/STRATEGY/PLANNING/PERFORMANCE',
    'BUSINESS DEVELOPMENT/SALES/PRODUCT MGMT',
    'CLIENT/CUSTOMER SERVICE',
    'CONTENT DEVELOPMENT/DISTRIBUTION',
    'FINANCE/ACCOUNTING',
    'GOVERNMENT/REGULATORY',
    'HR/TALENT/DIVERSITY',
    'INFORMATION/DIGITAL/ANALYTICS',
    'INVESTMENT/VENTURE CAPITAL/M&A',
    'LEGAL/IP',
    'MANUFACTURING',
    'MARKETING/ADVERTISING/PR',
    'OPERATIONS MGMT',
    'PRESS/MEDIA',
    'RESEARCH/DEVELOPMENT/INNOVATION',
    'SOFTWARE/DEVELOPER',
    'SOURCING/PROCUREMENT',
    'SUPPLY CHAIN MGMT/DISTRIBUTION',
    'TECHNICAL/ENGINEERING',
    'TRAINING/EDUCATION',
    'Other',
  ];

  const toggleItem = (item) => {
    let newSelected;
    if (selectedItems.includes(item)) {
      newSelected = selectedItems.filter(i => i !== item);
    } else {
      newSelected = [...selectedItems, item];
    }
    setSelectedItems(newSelected);
    onChange(newSelected.join(', '));
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-left flex items-center justify-between"
      >
        <span className="text-sm text-gray-700 truncate">
          {selectedItems.length > 0
            ? `${selectedItems.length} selected`
            : placeholder}
        </span>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto">
          {options.map((option) => (
            <div
              key={option}
              onClick={() => toggleItem(option)}
              className="px-3 py-2 hover:bg-blue-50 cursor-pointer flex items-center justify-between text-sm"
            >
              <span className={selectedItems.includes(option) ? 'font-semibold text-blue-600' : 'text-gray-700'}>
                {option}
              </span>
              {selectedItems.includes(option) && (
                <Check className="w-4 h-4 text-blue-600" />
              )}
            </div>
          ))}
        </div>
      )}

      {selectedItems.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {selectedItems.map((item) => (
            <span
              key={item}
              className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs"
            >
              {item}
              <button
                onClick={() => toggleItem(item)}
                className="hover:bg-blue-200 rounded-full p-0.5"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function CompanyRow({ company, isEven, isEditing, onEdit, onSave, onCancel, onDelete }) {
  const [formData, setFormData] = useState({
    company_name: company.company_name || '',
    country: company.country || '',
    city: company.city || '',
  });

  const handleSave = () => {
    onSave(formData);
  };

  return (
    <tr className={`${isEven ? 'bg-white' : 'bg-gray-50'} hover:bg-blue-50 transition-colors`}>
      <td className="px-6 py-4">
        {isEditing ? (
          <input
            type="text"
            value={formData.company_name}
            onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
          />
        ) : (
          <span className="text-sm font-medium text-gray-900">{company.company_name || '-'}</span>
        )}
      </td>
      <td className="px-6 py-4">
        {isEditing ? (
          <input
            type="text"
            value={formData.country}
            onChange={(e) => setFormData({ ...formData, country: e.target.value })}
            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
          />
        ) : (
          <span className="text-sm text-gray-700">{company.country || '-'}</span>
        )}
      </td>
      <td className="px-6 py-4">
        {isEditing ? (
          <input
            type="text"
            value={formData.city}
            onChange={(e) => setFormData({ ...formData, city: e.target.value })}
            className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
          />
        ) : (
          <span className="text-sm text-gray-700">{company.city || '-'}</span>
        )}
      </td>
      <td className="px-6 py-4">
        {isEditing ? (
          <div className="flex gap-2">
            <button
              onClick={handleSave}
              className="p-1 bg-green-600 text-white rounded hover:bg-green-700"
            >
              <Save className="w-4 h-4" />
            </button>
            <button
              onClick={onCancel}
              className="p-1 bg-gray-300 text-gray-700 rounded hover:bg-gray-400"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex gap-2">
            <button
              onClick={onEdit}
              className="p-1 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              <Edit className="w-4 h-4" />
            </button>
            <button
              onClick={onDelete}
              className="p-1 bg-red-600 text-white rounded hover:bg-red-700"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        )}
      </td>
    </tr>
  );
}

export default DataViewer;