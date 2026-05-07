import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CloudUpload, FileVideo, Loader2, X } from 'lucide-react';
import { cn } from '../../utils/formatters.js';

export const VideoUploader = ({ onSubmit, isLoading }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [modelPath, setModelPath] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('video/')) {
        setSelectedFile(file);
      }
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      if (file.type.startsWith('video/')) {
        setSelectedFile(file);
      }
    }
  };

  const openFileDialog = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const handleSubmit = () => {
    if (selectedFile && !isLoading) {
      onSubmit(selectedFile, modelPath);
    }
  };

  return (
    <div 
      className="flex flex-col w-full max-w-2xl mx-auto p-6 rounded-2xl"
      style={{ backgroundColor: '#12121a', border: '1px solid rgba(255, 255, 255, 0.06)' }}
    >
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white mb-2">Upload Video</h2>
        <p className="text-gray-400 text-sm">Select a video file to begin analysis using RetailEye AI.</p>
      </div>

      <motion.div
        className={cn(
          "relative flex flex-col items-center justify-center w-full min-h-[240px] rounded-xl border-2 border-dashed cursor-pointer overflow-hidden transition-colors duration-300",
          isDragging ? "border-blue-500 bg-blue-500/5" : "border-gray-700 hover:border-gray-500 bg-[#161622]"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={openFileDialog}
        animate={{
          boxShadow: isDragging ? '0 0 20px rgba(59, 130, 246, 0.2) inset' : '0 0 0 rgba(59, 130, 246, 0) inset',
        }}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          accept="video/*" 
          onChange={handleFileSelect} 
        />

        <AnimatePresence mode="wait">
          {!selectedFile ? (
            <motion.div
              key="upload-prompt"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="flex flex-col items-center p-6 text-center pointer-events-none"
            >
              <div className="p-4 mb-4 rounded-full bg-blue-500/10 text-blue-500">
                <CloudUpload strokeWidth={1.5} size={40} />
              </div>
              <p className="text-lg font-medium text-gray-200 mb-1">
                Drop your video here
              </p>
              <p className="text-sm text-gray-500">
                or click to browse from your computer
              </p>
              <div className="mt-4 px-3 py-1 flex items-center justify-center rounded-full bg-white/5 border border-white/10">
                <span className="text-xs text-gray-400 font-medium">MP4, AVI, MOV, MKV</span>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="file-info"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="flex flex-col items-center p-6 text-center w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-4 mb-4 rounded-full bg-green-500/10 text-green-500 relative">
                <FileVideo strokeWidth={1.5} size={40} />
                <button 
                  onClick={(e) => { e.stopPropagation(); setSelectedFile(null); }}
                  className="absolute -top-2 -right-2 p-1 bg-gray-800 rounded-full text-gray-400 hover:text-white border border-gray-700 transition"
                >
                  <X size={14} />
                </button>
              </div>
              <p className="text-md font-medium text-white max-w-full truncate px-4">
                {selectedFile.name}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {formatFileSize(selectedFile.size)}
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      <div className="my-6">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Custom Model Path (Optional)
        </label>
        <input
          type="text"
          value={modelPath}
          onChange={(e) => setModelPath(e.target.value)}
          placeholder="e.g., runs/detect/train/weights/best.pt"
          className="w-full px-4 py-3 bg-[#161622] border border-gray-700 rounded-lg text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder-gray-600"
          disabled={isLoading}
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={!selectedFile || isLoading}
        className={cn(
          "relative w-full py-4 px-6 rounded-xl font-semibold text-lg transition-all duration-300 overflow-hidden shadow-lg",
          !selectedFile || isLoading 
            ? "bg-gray-800 text-gray-500 cursor-not-allowed shadow-none hover:bg-gray-800" 
            : "bg-blue-600 text-white hover:bg-blue-500 hover:shadow-blue-500/20 active:scale-[0.98]"
        )}
      >
        <div className="flex items-center justify-center gap-2">
          {isLoading ? (
             <>
               <Loader2 className="animate-spin" size={22} />
               <span>Analyzing...</span>
             </>
          ) : (
            <span>Analyze Video</span>
          )}
        </div>
      </button>
    </div>
  );
};
