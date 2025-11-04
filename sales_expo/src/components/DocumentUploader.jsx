

// import { useState, useRef } from 'react';
// import {
//   Upload,
//   FileText,
//   X,
//   Download,
//   Loader2,
//   AlertCircle,
//   CheckCircle2,
//   FolderOpen,
//   Eye,
//   Table,
//   Clock,
//   FileCheck,
//   FileSpreadsheet,
// } from 'lucide-react';
// import JSZip from 'jszip';
// import * as XLSX from 'xlsx';





// // Document Uploader Component (Clients + Prospects)
// function DocumentUploader() {
//   const [uploadType, setUploadType] = useState('clients');
  

//   return (
//     <div className="space-y-6">
//       {/* Upload Type Toggle */}
//       <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//         <h2 className="text-lg font-bold text-gray-900 mb-4">Select Upload Type</h2>
//         <div className="flex gap-4">
//           <button
//             onClick={() => setUploadType('clients')}
//             className={`flex-1 px-6 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 ${
//               uploadType === 'clients'
//                 ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg'
//                 : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
//             }`}
//           >
//             <FileText className="w-5 h-5" />
//             <div className="text-left">
//               <div className="font-bold">Clients</div>
//               <div className="text-xs opacity-90">Upload PDF documents</div>
//             </div>
//           </button>
//           <button
//             onClick={() => setUploadType('prospects')}
//             className={`flex-1 px-6 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 ${
//               uploadType === 'prospects'
//                 ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
//                 : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
//             }`}
//           >
//             <FileSpreadsheet className="w-5 h-5" />
//             <div className="text-left">
//               <div className="font-bold">Prospects</div>
//               <div className="text-xs opacity-90">Upload Excel files</div>
//             </div>
//           </button>
//         </div>
//       </div>

//       {/* Render appropriate uploader */}
//       {uploadType === 'clients' ? <ClientUploader /> : <ProspectUploader />}
//     </div>
//   );
// }

// // Client PDF Uploader Component
// function ClientUploader() {
//   const [files, setFiles] = useState([]);
//   const [excludedPages, setExcludedPages] = useState({});
//   const [processing, setProcessing] = useState(false);
//   const [processingStatus, setProcessingStatus] = useState({});
//   const [results, setResults] = useState({});
//   const [excelData, setExcelData] = useState({});
//   const [viewingFile, setViewingFile] = useState(null);
//   const [error, setError] = useState(null);
//   const [success, setSuccess] = useState(null);
//   const fileInputRef = useRef(null);

//   const handleFileSelect = (e) => {
//     const selectedFiles = Array.from(e.target.files);
//     const newFiles = selectedFiles.map(file => {
//       const fileExt = file.name.toLowerCase();
//       const isPdf = fileExt.endsWith('.pdf');
//       const isDocx = fileExt.endsWith('.docx') || fileExt.endsWith('.doc');
      
//       return {
//         id: Math.random().toString(36).substr(2, 9),
//         file,
//         name: file.name,
//         size: (file.size / 1024).toFixed(2) + ' KB',
//         fileType: isPdf ? 'pdf' : isDocx ? 'docx' : 'unknown', // Track file type
//         pageCount: isPdf ? Math.floor(Math.random() * 20) + 5 : null,
//         status: 'queued',
//         progress: 0,
//       };
//     });
//     setFiles(prev => [...prev, ...newFiles]);
//     setError(null);
//     setSuccess(null);
//   };

//   const removeFile = (id) => {
//     setFiles(prev => prev.filter(f => f.id !== id));
//     const newExcluded = { ...excludedPages };
//     const newStatus = { ...processingStatus };
//     const newResults = { ...results };
//     delete newExcluded[id];
//     delete newStatus[id];
//     delete newResults[id];
//     setExcludedPages(newExcluded);
//     setProcessingStatus(newStatus);
//     setResults(newResults);
//     setError(null);
//   };

//   const handlePageExclusion = (fileId, pages) => {
//     setExcludedPages(prev => ({
//       ...prev,
//       [fileId]: pages,
//     }));
//     setError(null);
//   };

//   const parseExcelToJson = async (blob, filename) => {
//     return new Promise((resolve, reject) => {
//       const reader = new FileReader();
//       reader.onload = (e) => {
//         try {
//           const data = new Uint8Array(e.target.result);
//           const workbook = XLSX.read(data, { type: 'array' });
//           const sheetName = workbook.SheetNames[0];
//           const worksheet = workbook.Sheets[sheetName];
//           const jsonData = XLSX.utils.sheet_to_json(worksheet);
//           resolve({ filename, data: jsonData, workbook });
//         } catch (err) {
//           reject(err);
//         }
//       };
//       reader.onerror = reject;
//       reader.readAsArrayBuffer(blob);
//     });
//   };

//   const updateFileStatus = (fileId, status, progress = 0) => {
//     setProcessingStatus(prev => ({
//       ...prev,
//       [fileId]: { status, progress },
//     }));
//     setFiles(prev =>
//       prev.map(f => (f.id === fileId ? { ...f, status, progress } : f))
//     );
//   };

//   const startProcessing = async () => {
//     if (files.length === 0 || processing) return;
//     setProcessing(true);
//     setError(null);
//     setSuccess(null);
//     setResults({});
//     setExcelData({});

//     files.forEach(f => updateFileStatus(f.id, 'processing', 10));

//     const excludedJson = {};
//     files.forEach(f => {
//       excludedJson[f.name] = excludedPages[f.id] || '';
//     });

//     try {
//       const formData = new FormData();
//       files.forEach(f => {
//         formData.append('files', f.file);
//       });
//       formData.append('bucket', 'clients');
//       formData.append('excluded_pages_json', JSON.stringify(excludedJson));

//       files.forEach(f => updateFileStatus(f.id, 'processing', 30));

//       const response = await fetch('http://localhost:8000/api/process-documents', {
//         method: 'POST',
//         body: formData,
//       });

//       files.forEach(f => updateFileStatus(f.id, 'processing', 60));

//       if (!response.ok) {
//         let errorMsg = 'Failed to process files';
//         try {
//           const errorData = await response.json();
//           errorMsg = errorData.detail || errorMsg;
//         } catch {
//           errorMsg = `Server error: ${response.status} ${response.statusText}`;
//         }
//         throw new Error(errorMsg);
//       }

//       const blob = await response.blob();

//       if (blob.size === 0) {
//         throw new Error('Received empty response from server');
//       }

//       files.forEach(f => updateFileStatus(f.id, 'processing', 80));

//       const zip = await JSZip.loadAsync(blob);
//       const newResults = {};
//       const excelDataMap = {};

//       // In startProcessing function, after loading ZIP
//       for (const relativePath in zip.files) {
//         const zipEntry = zip.files[relativePath];
        
//         if (zipEntry.dir) continue;
        
//         const filename = relativePath.split('/').pop();
        
//         if (filename.endsWith('.xlsx')) {
//             const excelBlob = await zipEntry.async('blob');
            
//             // Parse Excel data
//             try {
//                 const parsedData = await parseExcelToJson(excelBlob, filename);
//                 excelDataMap[filename] = parsedData;
//             } catch (parseErr) {
//                 console.error(`Failed to parse ${filename}:`, parseErr);
//             }
            
//             const url = URL.createObjectURL(excelBlob);
            
//             // Extract base name from report_XXX.xlsx
//             const baseNameMatch = filename.match(/report_(.+)\.xlsx/);
//             const excelBaseName = baseNameMatch ? baseNameMatch[1] : filename.replace('report_', '').replace('.xlsx', '');
            
//             console.log(`🔍 Looking for file matching: ${excelBaseName}`);
            
//             // Find matching file - check both PDF and DOCX extensions
//             const file = files.find(f => {
//                 const fileBaseName = f.name.replace(/\.(pdf|docx|doc)$/i, '');
//                 const match = fileBaseName === excelBaseName;
                
//                 if (match) {
//                     console.log(`✅ Matched: ${f.name} with ${filename}`);
//                 }
                
//                 return match;
//             });
            
//             if (file) {
//                 const processedPages = file.pageCount
//                     ? file.pageCount - (excludedPages[file.id]?.split(',').filter(p => p.trim()).length || 0)
//                     : 'N/A';
                
//                 newResults[file.id] = {
//                     fileId: file.id,
//                     fileName: file.name,
//                     excelFileName: filename,
//                     downloadUrl: url,
//                     processedPages,
//                     excludedPages: excludedPages[file.id] || 'None',
//                     status: 'success',
//                     recordCount: excelDataMap[filename]?.data?.length || 0,
//                 };
                
//                 updateFileStatus(file.id, 'success', 100);
//             } else {
//                 console.warn(`⚠️ No matching file found for ${filename}`);
//             }
//         }
//       }

//       files.forEach(file => {
//         if (!newResults[file.id] && processingStatus[file.id]?.status === 'processing') {
//           const baseName = file.name.replace('.pdf', '');
//           const hasNoDataFile = Object.keys(zip.files).some(path =>
//             path.includes(baseName) && path.includes('NO_DATA_EXTRACTED')
//           );

//           if (hasNoDataFile) {
//             console.warn(`No data extracted for ${file.name}`);
//             updateFileStatus(file.id, 'error', 0);
//             newResults[file.id] = {
//               fileId: file.id,
//               fileName: file.name,
//               status: 'error',
//               error: 'No contact data found',
//               recordCount: 0,
//             };
//           }
//         }
//       });

//       if (Object.keys(newResults).filter(k => newResults[k].downloadUrl).length === 0) {
//         throw new Error('No Excel files generated - check if documents contain contact information');
//       }

//       setResults(newResults);
//       setExcelData(excelDataMap);
//       setSuccess(
//         `Successfully processed ${Object.keys(newResults).length} files with ${Object.values(newResults).reduce(
//           (sum, r) => sum + r.recordCount,
//           0
//         )} records`
//       );
//     } catch (err) {
//       console.error('Processing error:', err);
//       setError(err.message);
//       files.forEach(f => {
//         if (processingStatus[f.id]?.status === 'processing') {
//           updateFileStatus(f.id, 'error', 0);
//         }
//       });
//     } finally {
//       setProcessing(false);
//     }
//   };

//   const downloadFile = (url, filename) => {
//     const a = document.createElement('a');
//     a.href = url;
//     a.download = filename;
//     document.body.appendChild(a);
//     a.click();
//     document.body.removeChild(a);
//   };

//   const downloadAllFiles = () => {
//     Object.values(results).forEach(result => {
//       if (result.downloadUrl) downloadFile(result.downloadUrl, result.excelFileName);
//     });
//   };

//   const viewExcelData = (excelFileName) => {
//     setViewingFile(excelFileName);
//   };

//   const resetApp = () => {
//     Object.values(results).forEach(result => {
//       if (result.downloadUrl) {
//         URL.revokeObjectURL(result.downloadUrl);
//       }
//     });

//     setFiles([]);
//     setExcludedPages({});
//     setProcessingStatus({});
//     setResults({});
//     setExcelData({});
//     setViewingFile(null);
//     setError(null);
//     setSuccess(null);
//     if (fileInputRef.current) fileInputRef.current.value = '';
//   };

//   const getStatusIcon = (status) => {
//     switch (status) {
//       case 'success':
//         return <CheckCircle2 className="w-5 h-5 text-green-600" />;
//       case 'processing':
//         return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
//       case 'error':
//         return <AlertCircle className="w-5 h-5 text-red-600" />;
//       default:
//         return <Clock className="w-5 h-5 text-gray-400" />;
//     }
//   };

//   const getStatusColor = (status) => {
//     switch (status) {
//       case 'success':
//         return 'bg-green-100 text-green-700 border-green-200';
//       case 'processing':
//         return 'bg-blue-100 text-blue-700 border-blue-200';
//       case 'error':
//         return 'bg-red-100 text-red-700 border-red-200';
//       default:
//         return 'bg-gray-100 text-gray-600 border-gray-200';
//     }
//   };

//   return (
//     <>
//       {error && (
//         <div className="mb-4">
//           <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg shadow-sm">
//             <div className="flex items-start gap-3">
//               <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
//               <div>
//                 <p className="font-semibold text-red-800">Processing Error</p>
//                 <p className="text-red-700 text-sm mt-1">{error}</p>
//               </div>
//             </div>
//           </div>
//         </div>
//       )}

//       {success && (
//         <div className="mb-4">
//           <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded-lg shadow-sm">
//             <div className="flex items-start gap-3">
//               <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
//               <div>
//                 <p className="font-semibold text-green-800">Processing Successful</p>
//                 <p className="text-green-700 text-sm mt-1">{success}</p>
//               </div>
//             </div>
//           </div>
//         </div>
//       )}

//       <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
//         <div className="lg:col-span-2 space-y-6">
//           <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//             <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
//               <Upload className="w-5 h-5 text-blue-600" />
//               Upload Client PDFs
//             </h2>

//             <input
//             type="file"
//             multiple
//             onChange={handleFileSelect}
//             className="hidden"
//             id="fileInput"
//             accept=".pdf,.docx,.doc"  // Updated to accept DOCX
//             disabled={processing}
//             ref={fileInputRef}
//           />
//             <label
//               htmlFor="fileInput"
//               className={`block border-2 border-dashed border-blue-300 rounded-xl p-8 text-center transition-all duration-200 ${
//                 processing ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-500 hover:bg-blue-50 cursor-pointer'
//               }`}
//             >
//               <div className="inline-block p-3 bg-blue-100 rounded-full mb-2">
//                 <Upload className="w-6 h-6 text-blue-600" />
//               </div>
//               <p className="text-base font-semibold text-gray-700 mb-1">
//                 Drop PDF/DOCX files or click to browse
//               </p>
//               <p className="text-xs text-gray-500">Multiple files supported( .pdf, .docx)</p>
//             </label>
//           </div>

//           {files.length > 0 && (
//             <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//               <div className="flex items-center justify-between mb-4">
//                 <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
//                   <FileText className="w-5 h-5 text-blue-600" />
//                   Uploaded Files ({files.length})
//                 </h2>
//                 <button
//                   onClick={resetApp}
//                   disabled={processing}
//                   className="px-3 py-1.5 text-sm border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all disabled:opacity-50"
//                 >
//                   Clear All
//                 </button>
//               </div>

//               <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
//                 {files.map(file => (
//                   <div
//                     key={file.id}
//                     className={`rounded-xl p-4 border transition-all ${
//                       file.status === 'success'
//                         ? 'bg-green-50 border-green-200'
//                         : file.status === 'processing'
//                         ? 'bg-blue-50 border-blue-200'
//                         : file.status === 'error'
//                         ? 'bg-red-50 border-red-200'
//                         : 'bg-gray-50 border-gray-200'
//                     }`}
//                   >
//                     <div className="flex items-center justify-between mb-3">
//                       <div className="flex items-center gap-3 flex-1 min-w-0">
//                         <div className="p-2 bg-white rounded-lg shadow-sm">
//                           <FileText className="w-4 h-4 text-blue-600" />
//                         </div>
//                         <div className="flex-1 min-w-0">
//                           <p className="font-semibold text-gray-900 text-sm truncate">{file.name}</p>
//                           <p className="text-xs text-gray-600 mt-0.5">
//                             {file.size}
//                             {file.pageCount && ` • ${file.pageCount} pages`}
//                           </p>
//                         </div>
//                       </div>
//                       <button
//                         onClick={() => removeFile(file.id)}
//                         disabled={processing}
//                         className="p-1.5 hover:bg-red-100 rounded-lg transition-colors disabled:opacity-50"
//                         title="Remove file"
//                       >
//                         <X className="w-4 h-4 text-red-600" />
//                       </button>
//                     </div>

//                     {file.pageCount && file.status !== 'success' && (
//                       <div>
//                         <label className="block text-xs font-medium text-gray-700 mb-1.5">
//                           Exclude pages (optional)
//                         </label>
//                         <input
//                           type="text"
//                           value={excludedPages[file.id] || ''}
//                           onChange={e => handlePageExclusion(file.id, e.target.value)}
//                           placeholder="e.g., 1, 3, 5-7"
//                           disabled={processing}
//                           className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:opacity-50"
//                         />
//                       </div>
//                     )}
//                   </div>
//                 ))}
//               </div>

//               <div className="mt-4 pt-4 border-t border-gray-200">
//                 <button
//                   onClick={startProcessing}
//                   disabled={processing}
//                   className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-cyan-700 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2"
//                 >
//                   {processing ? (
//                     <>
//                       <Loader2 className="w-5 h-5 animate-spin" />
//                       Processing {files.length} files...
//                     </>
//                   ) : (
//                     <>
//                       <Upload className="w-5 h-5" />
//                       Start Processing
//                     </>
//                   )}
//                 </button>
//               </div>
//             </div>
//           )}
//         </div>

//         <div className="lg:col-span-1">
//           <div className="sticky top-6 space-y-4">
//             <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//               <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
//                 <FileCheck className="w-5 h-5 text-blue-600" />
//                 Processing Status
//               </h2>

//               {files.length === 0 ? (
//                 <div className="text-center py-12">
//                   <div className="inline-block p-4 bg-gray-100 rounded-full mb-3">
//                     <FolderOpen className="w-8 h-8 text-gray-400" />
//                   </div>
//                   <p className="text-sm text-gray-500">No files uploaded yet</p>
//                   <p className="text-xs text-gray-400 mt-1">Upload PDFs to begin</p>
//                 </div>
//               ) : (
//                 <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
//                   {files.map(file => {
//                     const status = processingStatus[file.id] || { status: file.status, progress: 0 };
//                     const result = results[file.id];

//                     return (
//                       <div
//                         key={file.id}
//                         className={`border rounded-lg p-3 transition-all ${getStatusColor(status.status)}`}
//                       >
//                         <div className="flex items-start gap-2 mb-2">
//                           {getStatusIcon(status.status)}
//                           <div className="flex-1 min-w-0">
//                             <p className="text-xs font-semibold truncate">{file.name}</p>
//                             <p className="text-xs opacity-75 capitalize">{status.status}</p>
//                           </div>
//                         </div>

//                         {status.status === 'processing' && (
//                           <div className="mt-2">
//                             <div className="w-full bg-white bg-opacity-50 rounded-full h-1.5 overflow-hidden">
//                               <div
//                                 className="bg-blue-600 h-full rounded-full transition-all duration-300"
//                                 style={{ width: `${status.progress}%` }}
//                               />
//                             </div>
//                           </div>
//                         )}

//                         {result && result.downloadUrl && (
//                           <div className="mt-3 pt-3 border-t border-current border-opacity-20">
//                             <div className="grid grid-cols-2 gap-2 mb-2 text-xs">
//                               <div className="bg-white bg-opacity-50 rounded p-1.5 text-center">
//                                 <p className="opacity-75 text-[10px]">Records</p>
//                                 <p className="font-bold">{result.recordCount}</p>
//                               </div>
//                               <div className="bg-white bg-opacity-50 rounded p-1.5 text-center">
//                                 <p className="opacity-75 text-[10px]">Pages</p>
//                                 <p className="font-bold">{result.processedPages}</p>
//                               </div>
//                             </div>
//                             <div className="flex gap-1.5">
//                               <button
//                                 onClick={() => viewExcelData(result.excelFileName)}
//                                 className="flex-1 px-2 py-1.5 bg-white rounded text-xs font-medium hover:shadow transition-all flex items-center justify-center gap-1"
//                               >
//                                 <Eye className="w-3 h-3" />
//                                 View
//                               </button>
//                               <button
//                                 onClick={() => downloadFile(result.downloadUrl, result.excelFileName)}
//                                 className="flex-1 px-2 py-1.5 bg-white rounded text-xs font-medium hover:shadow transition-all flex items-center justify-center gap-1"
//                               >
//                                 <Download className="w-3 h-3" />
//                                 Save
//                               </button>
//                             </div>
//                           </div>
//                         )}
//                       </div>
//                     );
//                   })}
//                 </div>
//               )}
//             </div>

//             {files.length > 0 && (
//               <div className="bg-gradient-to-br from-blue-600 to-cyan-600 rounded-2xl shadow-lg p-6 text-white">
//                 <h3 className="text-sm font-semibold mb-4 opacity-90">Summary</h3>
//                 <div className="grid grid-cols-2 gap-4">
//                   <div className="bg-white bg-opacity-20 rounded-lg p-3 backdrop-blur-sm">
//                     <p className="text-xs opacity-90 mb-1">Total Files</p>
//                     <p className="text-2xl font-bold">{files.length}</p>
//                   </div>
//                   <div className="bg-white bg-opacity-20 rounded-lg p-3 backdrop-blur-sm">
//                     <p className="text-xs opacity-90 mb-1">Completed</p>
//                     <p className="text-2xl font-bold">{Object.keys(results).length}</p>
//                   </div>
//                 </div>

//                 {Object.keys(results).length > 0 && (
//                   <div className="mt-4 pt-4 border-t border-white border-opacity-20">
//                     <div className="bg-white bg-opacity-20 rounded-lg p-3 backdrop-blur-sm">
//                       <p className="text-xs opacity-90 mb-1">Total Records</p>
//                       <p className="text-2xl font-bold">
//                         {Object.values(results).reduce((sum, r) => sum + r.recordCount, 0)}
//                       </p>
//                     </div>
//                   </div>
//                 )}
//               </div>
//             )}
//           </div>
//         </div>
//       </div>

//       {viewingFile && excelData[viewingFile] && (
//         <ExcelPreviewModal
//           excelData={excelData[viewingFile]}
//           filename={viewingFile}
//           onClose={() => setViewingFile(null)}
//           onDownload={() => {
//             const result = Object.values(results).find(r => r.excelFileName === viewingFile);
//             if (result) downloadFile(result.downloadUrl, result.excelFileName);
//           }}
//         />
//       )}
//     </>
//   );
// }

// // Prospect Excel Uploader Component

// function ProspectUploader() {
//   const [file, setFile] = useState(null); // Changed to store a single file
//   const [uploading, setUploading] = useState(false);
//   const [error, setError] = useState(null);
//   const [success, setSuccess] = useState(null);
//   const fileInputRef = useRef(null);

//   const handleFileSelect = (e) => {
//     const selectedFile = e.target.files[0]; // Take only the first file
//     if (selectedFile) {
//       if (!selectedFile.name.toLowerCase().endsWith('.xlsx') && !selectedFile.name.toLowerCase().endsWith('.xls')) {
//         setError('Only Excel files (.xlsx, .xls) are allowed');
//         return;
//       }
//       setFile({
//         id: Math.random().toString(36).substr(2, 9),
//         file: selectedFile,
//         name: selectedFile.name,
//         size: (selectedFile.size / 1024).toFixed(2) + ' KB',
//         status: 'queued',
//       });
//       setError(null);
//       setSuccess(null);
//     }
//   };

//   const removeFile = () => {
//     setFile(null);
//     if (fileInputRef.current) fileInputRef.current.value = '';
//   };

//   const uploadProspects = async () => {
//     if (!file || uploading) return;
//     setUploading(true);
//     setError(null);
//     setSuccess(null);

//     try {
//       const formData = new FormData();
//       formData.append('file', file.file); // Use 'file' key as expected by backend

//       const response = await fetch('http://localhost:8000/api/upload-prospects-excel', {
//         method: 'POST',
//         body: formData,
//       });

//       if (!response.ok) {
//         const errorData = await response.json();
//         throw new Error(errorData.detail || 'Failed to upload prospect file');
//       }

//       const result = await response.json();
//       setSuccess(
//         `Successfully uploaded ${result.filename} with ${result.companies_imported} records (Document ID: ${result.document_id})`
//       );
//       setFile(null);
//       if (fileInputRef.current) fileInputRef.current.value = '';
//     } catch (err) {
//       console.error('Upload error:', err);
//       setError(err.message);
//     } finally {
//       setUploading(false);
//     }
//   };

//   return (
//     <div className="space-y-6">
//       {error && (
//         <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg shadow-sm">
//           <div className="flex items-start gap-3">
//             <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
//             <div>
//               <p className="font-semibold text-red-800">Upload Error</p>
//               <p className="text-red-700 text-sm mt-1">{error}</p>
//             </div>
//           </div>
//         </div>
//       )}

//       {success && (
//         <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded-lg shadow-sm">
//           <div className="flex items-start gap-3">
//             <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
//             <div>
//               <p className="font-semibold text-green-800">Upload Successful</p>
//               <p className="text-green-700 text-sm mt-1">{success}</p>
//             </div>
//           </div>
//         </div>
//       )}

//       <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//         <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
//           <FileSpreadsheet className="w-5 h-5 text-purple-600" />
//           Upload Prospect Excel File
//         </h2>

//         <input
//           type="file"
//           onChange={handleFileSelect}
//           className="hidden"
//           id="prospectFileInput"
//           accept=".xlsx,.xls"
//           disabled={uploading}
//           ref={fileInputRef}
//         />
//         <label
//           htmlFor="prospectFileInput"
//           className={`block border-2 border-dashed border-purple-300 rounded-xl p-8 text-center transition-all duration-200 ${
//             uploading ? 'opacity-50 cursor-not-allowed' : 'hover:border-purple-500 hover:bg-purple-50 cursor-pointer'
//           }`}
//         >
//           <div className="inline-block p-3 bg-purple-100 rounded-full mb-2">
//             <FileSpreadsheet className="w-6 h-6 text-purple-600" />
//           </div>
//           <p className="text-base font-semibold text-gray-700 mb-1">
//             Drop an Excel file or click to browse
//           </p>
//           <p className="text-xs text-gray-500">Supports .xlsx and .xls formats</p>
//         </label>
//       </div>

//       {file && (
//         <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
//           <div className="flex items-center justify-between mb-4">
//             <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
//               <FileText className="w-5 h-5 text-purple-600" />
//               Selected File
//             </h2>
//             <button
//               onClick={removeFile}
//               disabled={uploading}
//               className="px-3 py-1.5 text-sm border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all disabled:opacity-50"
//             >
//               Clear
//             </button>
//           </div>

//           <div className="rounded-xl p-4 border bg-purple-50 border-purple-200">
//             <div className="flex items-center justify-between">
//               <div className="flex items-center gap-3 flex-1 min-w-0">
//                 <div className="p-2 bg-white rounded-lg shadow-sm">
//                   <FileSpreadsheet className="w-4 h-4 text-purple-600" />
//                 </div>
//                 <div className="flex-1 min-w-0">
//                   <p className="font-semibold text-gray-900 text-sm truncate">{file.name}</p>
//                   <p className="text-xs text-gray-600 mt-0.5">{file.size}</p>
//                 </div>
//               </div>
//               <button
//                 onClick={removeFile}
//                 disabled={uploading}
//                 className="p-1.5 hover:bg-red-100 rounded-lg transition-colors disabled:opacity-50"
//                 title="Remove file"
//               >
//                 <X className="w-4 h-4 text-red-600" />
//               </button>
//             </div>
//           </div>

//           <div className="mt-4 pt-4 border-t border-gray-200">
//             <button
//               onClick={uploadProspects}
//               disabled={uploading || !file}
//               className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2"
//             >
//               {uploading ? (
//                 <>
//                   <Loader2 className="w-5 h-5 animate-spin" />
//                   Uploading file...
//                 </>
//               ) : (
//                 <>
//                   <Upload className="w-5 h-5" />
//                   Upload to Database
//                 </>
//               )}
//             </button>
//           </div>
//         </div>
//       )}

//       <div className="bg-purple-50 border border-purple-200 rounded-xl p-6">
//         <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
//           <AlertCircle className="w-5 h-5 text-purple-600" />
//           Excel Format Requirements
//         </h3>
//         <ul className="text-sm text-gray-700 space-y-2">
//           <li className="flex items-start gap-2">
//             <span className="text-purple-600 mt-0.5">•</span>
//             <span>First row should contain column headers</span>
//           </li>
//           <li className="flex items-start gap-2">
//             <span className="text-purple-600 mt-0.5">•</span>
//             <span>
//               Required columns: Company, Country (other fields like Reg ID, First Name, Last Name, etc., are optional)
//             </span>
//           </li>
//           <li className="flex items-start gap-2">
//             <span className="text-purple-600 mt-0.5">•</span>
//             <span>Data will be automatically validated and stored in the database</span>
//           </li>
//         </ul>
//       </div>
//     </div>
//   );
// }

// // Excel Preview Modal Component
// function ExcelPreviewModal({ excelData, filename, onClose, onDownload }) {
//   const data = excelData.data;
//   if (!data || data.length === 0) {
//     return (
//       <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
//         <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6">
//           <div className="text-center py-8 text-gray-500">No data to display</div>
//           <button
//             onClick={onClose}
//             className="w-full mt-4 px-6 py-3 bg-gray-600 text-white rounded-xl font-semibold hover:bg-gray-700 transition-all"
//           >
//             Close
//           </button>
//         </div>
//       </div>
//     );
//   }

//   const columns = Object.keys(data[0]);

//   return (
//     <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
//       <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] flex flex-col">
//         <div className="p-6 border-b border-gray-200 flex items-center justify-between">
//           <div className="flex items-center gap-3">
//             <div className="p-2 bg-blue-100 rounded-lg">
//               <Table className="w-6 h-6 text-blue-600" />
//             </div>
//             <div>
//               <h3 className="text-xl font-bold text-gray-900">{filename}</h3>
//               <p className="text-sm text-gray-600">{data.length} records</p>
//             </div>
//           </div>
//           <button
//             onClick={onClose}
//             className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
//           >
//             <X className="w-6 h-6 text-gray-600" />
//           </button>
//         </div>

//         <div className="flex-1 overflow-auto p-6">
//           <div className="overflow-x-auto">
//             <table className="w-full border-collapse">
//               <thead>
//                 <tr className="bg-gradient-to-r from-blue-50 to-cyan-50">
//                   {columns.map((col, idx) => (
//                     <th
//                       key={idx}
//                       className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b-2 border-blue-200 sticky top-0 bg-blue-50"
//                     >
//                       {col}
//                     </th>
//                   ))}
//                 </tr>
//               </thead>
//               <tbody>
//                 {data.map((row, rowIdx) => (
//                   <tr
//                     key={rowIdx}
//                     className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
//                   >
//                     {columns.map((col, colIdx) => (
//                       <td
//                         key={colIdx}
//                         className="px-4 py-3 text-sm text-gray-900 border-b border-gray-200"
//                       >
//                         {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
//                       </td>
//                     ))}
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           </div>
//         </div>

//         <div className="p-6 border-t border-gray-200 bg-gray-50">
//           <button
//             onClick={onDownload}
//             className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-cyan-700 transition-all flex items-center justify-center gap-2"
//           >
//             <Download className="w-5 h-5" />
//             Download Excel File
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default DocumentUploader;























import { useState, useRef, useEffect } from 'react';
import {
  Upload,
  FileText,
  X,
  Download,
  Loader2,
  AlertCircle,
  CheckCircle2,
  FolderOpen,
  Eye,
  Table,
  Clock,
  FileCheck,
  FileSpreadsheet,
  AlertTriangle,
  Ban,
} from 'lucide-react';
import JSZip from 'jszip';
import * as XLSX from 'xlsx';

// Document Uploader Component (Clients + Prospects)
function DocumentUploader() {
  const [uploadType, setUploadType] = useState('clients');
  const [isProcessing, setIsProcessing] = useState(false);

  // Block navigation when processing
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (isProcessing) {
        e.preventDefault();
        e.returnValue = 'Processing is in progress. Are you sure you want to leave?';
        return e.returnValue;
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [isProcessing]);

  return (
    <div className="space-y-6 relative">
      {/* Processing Overlay */}
      {isProcessing && (
        <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
                <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Processing Documents</h3>
              <p className="text-gray-600 mb-4">
                Please wait while we process your files. Do not close or navigate away from this page.
              </p>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-yellow-800 text-left">
                    Closing this page will lose your upload progress, but processing will continue in the background.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upload Type Toggle */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4">Select Upload Type</h2>
        <div className="flex gap-4">
          <button
            onClick={() => setUploadType('clients')}
            disabled={isProcessing}
            className={`flex-1 px-6 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 ${
              uploadType === 'clients'
                ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <FileText className="w-5 h-5" />
            <div className="text-left">
              <div className="font-bold">Clients</div>
              <div className="text-xs opacity-90">Upload PDF documents</div>
            </div>
          </button>
          <button
            onClick={() => setUploadType('prospects')}
            disabled={isProcessing}
            className={`flex-1 px-6 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-3 ${
              uploadType === 'prospects'
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <FileSpreadsheet className="w-5 h-5" />
            <div className="text-left">
              <div className="font-bold">Prospects</div>
              <div className="text-xs opacity-90">Upload Excel files</div>
            </div>
          </button>
        </div>
      </div>

      {/* Render appropriate uploader */}
      {uploadType === 'clients' ? (
        <ClientUploader isProcessing={isProcessing} setIsProcessing={setIsProcessing} />
      ) : (
        <ProspectUploader isProcessing={isProcessing} setIsProcessing={setIsProcessing} />
      )}
    </div>
  );
}

// Client PDF Uploader Component
function ClientUploader({ isProcessing, setIsProcessing }) {
  const [files, setFiles] = useState([]);
  const [excludedPages, setExcludedPages] = useState({});
  const [processingStatus, setProcessingStatus] = useState({});
  const [results, setResults] = useState({});
  const [excelData, setExcelData] = useState({});
  const [viewingFile, setViewingFile] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [duplicateFiles, setDuplicateFiles] = useState([]);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const newFiles = selectedFiles.map(file => {
      const fileExt = file.name.toLowerCase();
      const isPdf = fileExt.endsWith('.pdf');
      const isDocx = fileExt.endsWith('.docx') || fileExt.endsWith('.doc');
      
      return {
        id: Math.random().toString(36).substr(2, 9),
        file,
        name: file.name,
        size: (file.size / 1024).toFixed(2) + ' KB',
        fileType: isPdf ? 'pdf' : isDocx ? 'docx' : 'unknown',
        pageCount: isPdf ? Math.floor(Math.random() * 20) + 5 : null,
        status: 'queued',
        progress: 0,
      };
    });
    setFiles(prev => [...prev, ...newFiles]);
    setError(null);
    setSuccess(null);
    setDuplicateFiles([]);
  };

  const removeFile = (id) => {
    setFiles(prev => prev.filter(f => f.id !== id));
    const newExcluded = { ...excludedPages };
    const newStatus = { ...processingStatus };
    const newResults = { ...results };
    delete newExcluded[id];
    delete newStatus[id];
    delete newResults[id];
    setExcludedPages(newExcluded);
    setProcessingStatus(newStatus);
    setResults(newResults);
    setError(null);
  };

  const handlePageExclusion = (fileId, pages) => {
    setExcludedPages(prev => ({
      ...prev,
      [fileId]: pages,
    }));
    setError(null);
  };

  const parseExcelToJson = async (blob, filename) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          const sheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[sheetName];
          const jsonData = XLSX.utils.sheet_to_json(worksheet);
          resolve({ filename, data: jsonData, workbook });
        } catch (err) {
          reject(err);
        }
      };
      reader.onerror = reject;
      reader.readAsArrayBuffer(blob);
    });
  };

  const updateFileStatus = (fileId, status, progress = 0) => {
    setProcessingStatus(prev => ({
      ...prev,
      [fileId]: { status, progress },
    }));
    setFiles(prev =>
      prev.map(f => (f.id === fileId ? { ...f, status, progress } : f))
    );
  };

  const startProcessing = async () => {
    if (files.length === 0 || isProcessing) return;
    
    setIsProcessing(true);
    setError(null);
    setSuccess(null);
    setResults({});
    setExcelData({});
    setDuplicateFiles([]);

    files.forEach(f => updateFileStatus(f.id, 'processing', 10));

    const excludedJson = {};
    files.forEach(f => {
      excludedJson[f.name] = excludedPages[f.id] || '';
    });

    try {
      const formData = new FormData();
      files.forEach(f => {
        formData.append('files', f.file);
      });
      formData.append('bucket', 'clients');
      formData.append('excluded_pages_json', JSON.stringify(excludedJson));

      files.forEach(f => updateFileStatus(f.id, 'processing', 30));

      const response = await fetch('http://localhost:8000/api/process-documents', {
        method: 'POST',
        body: formData,
      });

      files.forEach(f => updateFileStatus(f.id, 'processing', 60));

      if (!response.ok) {
        let errorMsg = 'Failed to process files';
        try {
          const errorData = await response.json();
          
          // Check for duplicate file errors in the response
          if (errorData.detail && typeof errorData.detail === 'string') {
            if (errorData.detail.includes('Duplicate file') || errorData.detail.includes('already processed')) {
              const docIdMatch = errorData.detail.match(/Document ID[:\s]+(\d+)/i);
              const docId = docIdMatch ? docIdMatch[1] : 'unknown';
              errorMsg = `This file has already been uploaded (Document ID: ${docId})`;
            } else {
              errorMsg = errorData.detail;
            }
          }
        } catch {
          errorMsg = `Server error: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorMsg);
      }

      const blob = await response.blob();

      if (blob.size === 0) {
        throw new Error('Received empty response from server');
      }

      files.forEach(f => updateFileStatus(f.id, 'processing', 80));

      const zip = await JSZip.loadAsync(blob);
      const newResults = {};
      const excelDataMap = {};
      const duplicates = [];

      for (const relativePath in zip.files) {
        const zipEntry = zip.files[relativePath];
        
        if (zipEntry.dir) continue;
        
        const filename = relativePath.split('/').pop();
        
        // Check for duplicate indicators
        if (filename.includes('DUPLICATE') || filename.includes('_duplicate')) {
          duplicates.push(filename);
          continue;
        }
        
        if (filename.endsWith('.xlsx')) {
          const excelBlob = await zipEntry.async('blob');
          
          try {
            const parsedData = await parseExcelToJson(excelBlob, filename);
            excelDataMap[filename] = parsedData;
          } catch (parseErr) {
            console.error(`Failed to parse ${filename}:`, parseErr);
          }
          
          const url = URL.createObjectURL(excelBlob);
          
          const baseNameMatch = filename.match(/report_(.+)\.xlsx/);
          const excelBaseName = baseNameMatch ? baseNameMatch[1] : filename.replace('report_', '').replace('.xlsx', '');
          
          const file = files.find(f => {
            const fileBaseName = f.name.replace(/\.(pdf|docx|doc)$/i, '');
            return fileBaseName === excelBaseName;
          });
          
          if (file) {
            const processedPages = file.pageCount
              ? file.pageCount - (excludedPages[file.id]?.split(',').filter(p => p.trim()).length || 0)
              : 'N/A';
            
            newResults[file.id] = {
              fileId: file.id,
              fileName: file.name,
              excelFileName: filename,
              downloadUrl: url,
              processedPages,
              excludedPages: excludedPages[file.id] || 'None',
              status: 'success',
              recordCount: excelDataMap[filename]?.data?.length || 0,
            };
            
            updateFileStatus(file.id, 'success', 100);
          }
        }
      }

      // Handle files with no data
      files.forEach(file => {
        if (!newResults[file.id] && processingStatus[file.id]?.status === 'processing') {
          const baseName = file.name.replace(/\.(pdf|docx|doc)$/i, '');
          const hasNoDataFile = Object.keys(zip.files).some(path =>
            path.includes(baseName) && path.includes('NO_DATA_EXTRACTED')
          );

          if (hasNoDataFile) {
            updateFileStatus(file.id, 'error', 0);
            newResults[file.id] = {
              fileId: file.id,
              fileName: file.name,
              status: 'error',
              error: 'No contact data found',
              recordCount: 0,
            };
          }
        }
      });

      if (duplicates.length > 0) {
        setDuplicateFiles(duplicates);
      }

      if (Object.keys(newResults).filter(k => newResults[k].downloadUrl).length === 0 && duplicates.length === 0) {
        throw new Error('No Excel files generated - check if documents contain contact information');
      }

      setResults(newResults);
      setExcelData(excelDataMap);
      
      const successCount = Object.keys(newResults).length;
      const totalRecords = Object.values(newResults).reduce((sum, r) => sum + r.recordCount, 0);
      
      let successMessage = `Successfully processed ${successCount} files with ${totalRecords} records`;
      if (duplicates.length > 0) {
        successMessage += ` (${duplicates.length} duplicate file${duplicates.length > 1 ? 's' : ''} skipped)`;
      }
      
      setSuccess(successMessage);
      
    } catch (err) {
      console.error('Processing error:', err);
      setError(err.message);
      files.forEach(f => {
        if (processingStatus[f.id]?.status === 'processing') {
          updateFileStatus(f.id, 'error', 0);
        }
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const downloadFile = (url, filename) => {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const downloadAllFiles = () => {
    Object.values(results).forEach(result => {
      if (result.downloadUrl) downloadFile(result.downloadUrl, result.excelFileName);
    });
  };

  const viewExcelData = (excelFileName) => {
    setViewingFile(excelFileName);
  };

  const resetApp = () => {
    Object.values(results).forEach(result => {
      if (result.downloadUrl) {
        URL.revokeObjectURL(result.downloadUrl);
      }
    });

    setFiles([]);
    setExcludedPages({});
    setProcessingStatus({});
    setResults({});
    setExcelData({});
    setViewingFile(null);
    setError(null);
    setSuccess(null);
    setDuplicateFiles([]);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-600" />;
      case 'processing':
        return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-700 border-green-200';
      case 'processing':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'error':
        return 'bg-red-100 text-red-700 border-red-200';
      default:
        return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  return (
    <>
      {duplicateFiles.length > 0 && (
        <div className="mb-4">
          <div className="p-4 bg-orange-50 border-l-4 border-orange-500 rounded-lg shadow-sm">
            <div className="flex items-start gap-3">
              <Ban className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="font-semibold text-orange-800">Duplicate Files Detected</p>
                <p className="text-orange-700 text-sm mt-1">
                  The following {duplicateFiles.length} file{duplicateFiles.length > 1 ? 's have' : ' has'} already been processed and {duplicateFiles.length > 1 ? 'were' : 'was'} skipped:
                </p>
                <ul className="mt-2 space-y-1">
                  {duplicateFiles.map((file, idx) => (
                    <li key={idx} className="text-sm text-orange-700 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 bg-orange-600 rounded-full"></span>
                      {file}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-4">
          <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg shadow-sm">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-red-800">Processing Error</p>
                <p className="text-red-700 text-sm mt-1">{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {success && (
        <div className="mb-4">
          <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded-lg shadow-sm">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-green-800">Processing Successful</p>
                <p className="text-green-700 text-sm mt-1">{success}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5 text-blue-600" />
              Upload Client PDFs
            </h2>

            <input
              type="file"
              multiple
              onChange={handleFileSelect}
              className="hidden"
              id="fileInput"
              accept=".pdf,.docx,.doc"
              disabled={isProcessing}
              ref={fileInputRef}
            />
            <label
              htmlFor="fileInput"
              className={`block border-2 border-dashed border-blue-300 rounded-xl p-8 text-center transition-all duration-200 ${
                isProcessing ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-500 hover:bg-blue-50 cursor-pointer'
              }`}
            >
              <div className="inline-block p-3 bg-blue-100 rounded-full mb-2">
                <Upload className="w-6 h-6 text-blue-600" />
              </div>
              <p className="text-base font-semibold text-gray-700 mb-1">
                Drop PDF/DOCX files or click to browse
              </p>
              <p className="text-xs text-gray-500">Multiple files supported (.pdf, .docx)</p>
            </label>
          </div>

          {files.length > 0 && (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  Uploaded Files ({files.length})
                </h2>
                <button
                  onClick={resetApp}
                  disabled={isProcessing}
                  className="px-3 py-1.5 text-sm border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all disabled:opacity-50"
                >
                  Clear All
                </button>
              </div>

              <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                {files.map(file => (
                  <div
                    key={file.id}
                    className={`rounded-xl p-4 border transition-all ${
                      file.status === 'success'
                        ? 'bg-green-50 border-green-200'
                        : file.status === 'processing'
                        ? 'bg-blue-50 border-blue-200'
                        : file.status === 'error'
                        ? 'bg-red-50 border-red-200'
                        : 'bg-gray-50 border-gray-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div className="p-2 bg-white rounded-lg shadow-sm">
                          <FileText className="w-4 h-4 text-blue-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-gray-900 text-sm truncate">{file.name}</p>
                          <p className="text-xs text-gray-600 mt-0.5">
                            {file.size}
                            {file.pageCount && ` • ${file.pageCount} pages`}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(file.id)}
                        disabled={isProcessing}
                        className="p-1.5 hover:bg-red-100 rounded-lg transition-colors disabled:opacity-50"
                        title="Remove file"
                      >
                        <X className="w-4 h-4 text-red-600" />
                      </button>
                    </div>

                    {file.pageCount && file.status !== 'success' && (
                      <div>
                        <label className="block text-xs font-medium text-gray-700 mb-1.5">
                          Exclude pages (optional)
                        </label>
                        <input
                          type="text"
                          value={excludedPages[file.id] || ''}
                          onChange={e => handlePageExclusion(file.id, e.target.value)}
                          placeholder="e.g., 1, 3, 5-7"
                          disabled={isProcessing}
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all disabled:opacity-50"
                        />
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={startProcessing}
                  disabled={isProcessing}
                  className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-cyan-700 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Processing {files.length} files...
                    </>
                  ) : (
                    <>
                      <Upload className="w-5 h-5" />
                      Start Processing
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="lg:col-span-1">
          <div className="sticky top-6 space-y-4">
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <FileCheck className="w-5 h-5 text-blue-600" />
                Processing Status
              </h2>

              {files.length === 0 ? (
                <div className="text-center py-12">
                  <div className="inline-block p-4 bg-gray-100 rounded-full mb-3">
                    <FolderOpen className="w-8 h-8 text-gray-400" />
                  </div>
                  <p className="text-sm text-gray-500">No files uploaded yet</p>
                  <p className="text-xs text-gray-400 mt-1">Upload PDFs to begin</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                  {files.map(file => {
                    const status = processingStatus[file.id] || { status: file.status, progress: 0 };
                    const result = results[file.id];

                    return (
                      <div
                        key={file.id}
                        className={`border rounded-lg p-3 transition-all ${getStatusColor(status.status)}`}
                      >
                        <div className="flex items-start gap-2 mb-2">
                          {getStatusIcon(status.status)}
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-semibold truncate">{file.name}</p>
                            <p className="text-xs opacity-75 capitalize">{status.status}</p>
                          </div>
                        </div>

                        {status.status === 'processing' && (
                          <div className="mt-2">
                            <div className="w-full bg-white bg-opacity-50 rounded-full h-1.5 overflow-hidden">
                              <div
                                className="bg-blue-600 h-full rounded-full transition-all duration-300"
                                style={{ width: `${status.progress}%` }}
                              />
                            </div>
                          </div>
                        )}

                        {result && result.downloadUrl && (
                          <div className="mt-3 pt-3 border-t border-current border-opacity-20">
                            <div className="grid grid-cols-2 gap-2 mb-2 text-xs">
                              <div className="bg-white bg-opacity-50 rounded p-1.5 text-center">
                                <p className="opacity-75 text-[10px]">Records</p>
                                <p className="font-bold">{result.recordCount}</p>
                              </div>
                              <div className="bg-white bg-opacity-50 rounded p-1.5 text-center">
                                <p className="opacity-75 text-[10px]">Pages</p>
                                <p className="font-bold">{result.processedPages}</p>
                              </div>
                            </div>
                            <div className="flex gap-1.5">
                              <button
                                onClick={() => viewExcelData(result.excelFileName)}
                                className="flex-1 px-2 py-1.5 bg-white rounded text-xs font-medium hover:shadow transition-all flex items-center justify-center gap-1"
                              >
                                <Eye className="w-3 h-3" />
                                View
                              </button>
                              <button
                                onClick={() => downloadFile(result.downloadUrl, result.excelFileName)}
                                className="flex-1 px-2 py-1.5 bg-white rounded text-xs font-medium hover:shadow transition-all flex items-center justify-center gap-1"
                              >
                                <Download className="w-3 h-3" />
                                Save
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {files.length > 0 && (
              <div className="bg-gradient-to-br from-blue-600 to-cyan-600 rounded-2xl shadow-lg p-6 text-white">
                <h3 className="text-sm font-semibold mb-4 opacity-90">Summary</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-white bg-opacity-20 rounded-lg p-3 backdrop-blur-sm">
                    <p className="text-xs opacity-90 mb-1">Total Files</p>
                    <p className="text-2xl font-bold">{files.length}</p>
                  </div>
                  <div className="bg-white bg-opacity-20 rounded-lg p-3 backdrop-blur-sm">
                    <p className="text-xs opacity-90 mb-1">Completed</p>
                    <p className="text-2xl font-bold">{Object.keys(results).length}</p>
                  </div>
                </div>

                {Object.keys(results).length > 0 && (
                  <div className="mt-4 pt-4 border-t border-white border-opacity-20">
                    <div className="bg-white bg-opacity-20 rounded-lg p-3 backdrop-blur-sm">
                      <p className="text-xs opacity-90 mb-1">Total Records</p>
                      <p className="text-2xl font-bold">
                        {Object.values(results).reduce((sum, r) => sum + r.recordCount, 0)}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {viewingFile && excelData[viewingFile] && (
        <ExcelPreviewModal
          excelData={excelData[viewingFile]}
          filename={viewingFile}
          onClose={() => setViewingFile(null)}
          onDownload={() => {
            const result = Object.values(results).find(r => r.excelFileName === viewingFile);
            if (result) downloadFile(result.downloadUrl, result.excelFileName);
          }}
        />
      )}
    </>
  );
}

// Prospect Excel Uploader Component
function ProspectUploader({ isProcessing, setIsProcessing }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      if (!selectedFile.name.toLowerCase().endsWith('.xlsx') && !selectedFile.name.toLowerCase().endsWith('.xls')) {
        setError('Only Excel files (.xlsx, .xls) are allowed');
        return;
      }
      setFile({
        id: Math.random().toString(36).substr(2, 9),
        file: selectedFile,
        name: selectedFile.name,
        size: (selectedFile.size / 1024).toFixed(2) + ' KB',
        status: 'queued',
      });
      setError(null);
      setSuccess(null);
    }
  };

  const removeFile = () => {
    setFile(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const uploadProspects = async () => {
    if (!file || isProcessing) return;
    setIsProcessing(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file.file);

      const response = await fetch('http://localhost:8000/api/upload-prospects-excel', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorMsg = 'Failed to upload prospect file';
        try {
          const errorData = await response.json();
          
          // Handle duplicate file error
          if (errorData.detail && typeof errorData.detail === 'string') {
            if (errorData.detail.includes('already uploaded') || errorData.detail.includes('Duplicate')) {
              const docIdMatch = errorData.detail.match(/Document ID[:\s]+(\d+)/i);
              const docId = docIdMatch ? docIdMatch[1] : 'unknown';
              errorMsg = `This file has already been uploaded (Document ID: ${docId})`;
            } else {
              errorMsg = errorData.detail;
            }
          }
        } catch {
          errorMsg = `Server error: ${response.status}`;
        }
        throw new Error(errorMsg);
      }

      const result = await response.json();
      setSuccess(
        `Successfully uploaded ${result.filename} with ${result.companies_imported} records (Document ID: ${result.document_id})`
      );
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      console.error('Upload error:', err);
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 bg-red-50 border-l-4 border-red-500 rounded-lg shadow-sm">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-800">Upload Error</p>
              <p className="text-red-700 text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {success && (
        <div className="p-4 bg-green-50 border-l-4 border-green-500 rounded-lg shadow-sm">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-green-800">Upload Successful</p>
              <p className="text-green-700 text-sm mt-1">{success}</p>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
          <FileSpreadsheet className="w-5 h-5 text-purple-600" />
          Upload Prospect Excel File
        </h2>

        <input
          type="file"
          onChange={handleFileSelect}
          className="hidden"
          id="prospectFileInput"
          accept=".xlsx,.xls"
          disabled={isProcessing}
          ref={fileInputRef}
        />
        <label
          htmlFor="prospectFileInput"
          className={`block border-2 border-dashed border-purple-300 rounded-xl p-8 text-center transition-all duration-200 ${
            isProcessing ? 'opacity-50 cursor-not-allowed' : 'hover:border-purple-500 hover:bg-purple-50 cursor-pointer'
          }`}
        >
          <div className="inline-block p-3 bg-purple-100 rounded-full mb-2">
            <FileSpreadsheet className="w-6 h-6 text-purple-600" />
          </div>
          <p className="text-base font-semibold text-gray-700 mb-1">
            Drop an Excel file or click to browse
          </p>
          <p className="text-xs text-gray-500">Supports .xlsx and .xls formats</p>
        </label>
      </div>

      {file && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <FileText className="w-5 h-5 text-purple-600" />
              Selected File
            </h2>
            <button
              onClick={removeFile}
              disabled={isProcessing}
              className="px-3 py-1.5 text-sm border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-all disabled:opacity-50"
            >
              Clear
            </button>
          </div>

          <div className="rounded-xl p-4 border bg-purple-50 border-purple-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <div className="p-2 bg-white rounded-lg shadow-sm">
                  <FileSpreadsheet className="w-4 h-4 text-purple-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-900 text-sm truncate">{file.name}</p>
                  <p className="text-xs text-gray-600 mt-0.5">{file.size}</p>
                </div>
              </div>
              <button
                onClick={removeFile}
                disabled={isProcessing}
                className="p-1.5 hover:bg-red-100 rounded-lg transition-colors disabled:opacity-50"
                title="Remove file"
              >
                <X className="w-4 h-4 text-red-600" />
              </button>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-gray-200">
            <button
              onClick={uploadProspects}
              disabled={isProcessing || !file}
              className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 shadow-lg hover:shadow-xl transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Uploading file...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  Upload to Database
                </>
              )}
            </button>
          </div>
        </div>
      )}

      <div className="bg-purple-50 border border-purple-200 rounded-xl p-6">
        <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-purple-600" />
          Excel Format Requirements
        </h3>
        <ul className="text-sm text-gray-700 space-y-2">
          <li className="flex items-start gap-2">
            <span className="text-purple-600 mt-0.5">•</span>
            <span>First row should contain column headers</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-purple-600 mt-0.5">•</span>
            <span>
              Required columns: Company, Country (other fields like Reg ID, First Name, Last Name, etc., are optional)
            </span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-purple-600 mt-0.5">•</span>
            <span>Data will be automatically validated and stored in the database</span>
          </li>
        </ul>
      </div>
    </div>
  );
}

// Excel Preview Modal Component
function ExcelPreviewModal({ excelData, filename, onClose, onDownload }) {
  const data = excelData.data;
  if (!data || data.length === 0) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6">
          <div className="text-center py-8 text-gray-500">No data to display</div>
          <button
            onClick={onClose}
            className="w-full mt-4 px-6 py-3 bg-gray-600 text-white rounded-xl font-semibold hover:bg-gray-700 transition-all"
          >
            Close
          </button>
        </div>
      </div>
    );
  }

  const columns = Object.keys(data[0]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-6xl w-full max-h-[90vh] flex flex-col">
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Table className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">{filename}</h3>
              <p className="text-sm text-gray-600">{data.length} records</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
        </div>

        <div className="flex-1 overflow-auto p-6">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gradient-to-r from-blue-50 to-cyan-50">
                  {columns.map((col, idx) => (
                    <th
                      key={idx}
                      className="px-4 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider border-b-2 border-blue-200 sticky top-0 bg-blue-50"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.map((row, rowIdx) => (
                  <tr
                    key={rowIdx}
                    className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}
                  >
                    {columns.map((col, colIdx) => (
                      <td
                        key={colIdx}
                        className="px-4 py-3 text-sm text-gray-900 border-b border-gray-200"
                      >
                        {row[col] !== null && row[col] !== undefined ? String(row[col]) : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <button
            onClick={onDownload}
            className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-cyan-700 transition-all flex items-center justify-center gap-2"
          >
            <Download className="w-5 h-5" />
            Download Excel File
          </button>
        </div>
      </div>
    </div>
  );
}

export default DocumentUploader;

