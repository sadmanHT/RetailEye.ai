import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, ChevronRight, PlayCircle, Loader2 } from 'lucide-react';
import { VideoUploader } from '../components/video/VideoUploader.jsx';
import { uploadVideo } from '../services/api.js';

const features = [
  "Person Detection and Tracking",
  "Zone Analytics",
  "Dwell Time Analysis",
  "Queue Detection",
  "Crowd Heatmaps",
  "Automated Alerts"
];

const processingStages = [
  "Initializing engine...",
  "Running YOLOv8 inference...",
  "Applying DeepSORT tracking...",
  "Generating crowd heatmaps...",
  "Compiling zone analytics...",
  "Finalizing report..."
];

export const Upload = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentStage, setCurrentStage] = useState(processingStages[0]);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [jobId, setJobId] = useState(null);
  
  const navigate = useNavigate();

  // Progress simulation while waiting for API
  useEffect(() => {
    let interval;
    if (isUploading && uploadProgress < 95 && !isComplete) {
      interval = setInterval(() => {
        setUploadProgress(prev => {
          const next = prev + (Math.random() * 2.5);
          return next > 95 ? 95 : next;
        });
        
        setTimeRemaining(prev => Math.max(1, prev - 1));
      }, 800);
    }
    return () => clearInterval(interval);
  }, [isUploading, uploadProgress, isComplete]);

  // Stage text rotation
  useEffect(() => {
    let stageInterval;
    if (isUploading && !isComplete) {
      let stageIndex = 0;
      stageInterval = setInterval(() => {
        stageIndex = (stageIndex + 1) % processingStages.length;
        setCurrentStage(processingStages[stageIndex]);
      }, 4000);
    }
    return () => clearInterval(stageInterval);
  }, [isUploading, isComplete]);

  const handleUpload = async (file, modelPath) => {
    try {
      setIsUploading(true);
      setUploadProgress(5);
      setTimeRemaining(45); // estimated 45s
      setIsComplete(false);

      const returnedJobId = await uploadVideo(file, modelPath);
      
      // Force completion state
      setUploadProgress(100);
      setCurrentStage("Processing Complete");
      setJobId(returnedJobId);
      setIsComplete(true);
      setIsUploading(false);
    } catch (error) {
      console.error(error);
      alert('Upload failed: ' + error.message);
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleDemoMode = () => {
    // Load a pre-computed demo sequence
    setIsUploading(true);
    setUploadProgress(0);
    setTimeRemaining(5);
    setIsComplete(false);
    
    let simProgress = 0;
    const simInterval = setInterval(() => {
      simProgress += 10;
      setUploadProgress(simProgress);
      setTimeRemaining(prev => Math.max(0, prev - 0.5));
      if (simProgress >= 100) {
        clearInterval(simInterval);
        setIsComplete(true);
        setIsUploading(false);
        setJobId("demo-1234");
        setCurrentStage("Demo Loaded Successfully");
      }
    }, 300);
  };

  return (
    <div className="flex flex-col items-center justify-start h-full pt-8 pb-20 overflow-y-auto custom-scrollbar px-6 w-full max-w-6xl mx-auto text-white">
      
      {/* Hero Section */}
      <div className="text-center mb-12 w-full">
        <motion.h1 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-5xl font-extrabold mb-4 bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text"
        >
          Retail Intelligence Powered by AI
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-gray-400 text-lg max-w-2xl mx-auto"
        >
          Uncover actionable insights from your store's security footage. Upload a clip to instantly generate real-time analytics, queue times, and traffic heatmaps.
        </motion.p>
      </div>

      <AnimatePresence mode="wait">
        {!isUploading && !isComplete ? (
          <motion.div 
            key="upload-section"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95, filter: 'blur(5px)' }}
            transition={{ duration: 0.4 }}
            className="w-full grid grid-cols-1 lg:grid-cols-2 gap-8 items-start"
          >
            {/* Left: Uploader */}
            <div className="bg-[#12121a] border border-white/10 p-6 rounded-2xl shadow-xl flex flex-col h-full items-center justify-center">
              <VideoUploader onSubmit={handleUpload} isLoading={false} />
              
              <div className="w-full mt-6 pt-6 border-t border-white/10 text-center">
                <p className="text-gray-400 text-sm mb-3">Want to see it in action without uploading?</p>
                <button
                  onClick={handleDemoMode}
                  className="flex items-center gap-2 mx-auto justify-center px-5 py-2.5 bg-gray-800 hover:bg-gray-700 border border-gray-600 rounded-lg text-sm font-medium transition-all hover:scale-105 shadow-md shadow-purple-900/10"
                >
                  <PlayCircle size={18} className="text-purple-400" />
                  Load Sample Video Demo
                </button>
              </div>
            </div>

            {/* Right: Features */}
            <div className="bg-gradient-to-br from-[#12121a] to-[#0f0f15] border border-purple-500/20 p-8 rounded-2xl shadow-[0_0_40px_rgba(168,85,247,0.05)] h-full">
              <h2 className="text-2xl font-bold mb-8">System Capabilities</h2>
              <ul className="space-y-6">
                {features.map((feature, i) => (
                  <motion.li 
                    key={feature}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 + 0.3 }}
                    className="flex items-center gap-4 text-gray-200 text-lg"
                  >
                    <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 text-purple-400 p-1.5 rounded-full flex-shrink-0 shadow-[0_0_10px_rgba(168,85,247,0.2)]">
                      <CheckCircle2 size={24} />
                    </div>
                    {feature}
                  </motion.li>
                ))}
              </ul>
              
              <div className="mt-12 bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 flex gap-4 items-start shadow-inner">
                <div className="p-2 bg-blue-500/20 rounded-lg flex-shrink-0">
                  <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                </div>
                <div>
                  <h4 className="font-semibold text-blue-100">State-of-the-Art Processing</h4>
                  <p className="text-sm text-blue-300/70 mt-1">Leveraging YOLOv8 bounding boxes intertwined directly with DeepSORT ID tracking via websockets.</p>
                </div>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div 
            key="progress-section"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-2xl mx-auto bg-[#12121a] border border-white/10 p-12 rounded-3xl shadow-[0_0_50px_rgba(0,0,0,0.5)] flex flex-col items-center text-center"
          >
            {isComplete ? (
              <motion.div 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", bounce: 0.5 }}
                className="flex flex-col items-center"
              >
                <div className="w-32 h-32 bg-green-500/10 rounded-full flex items-center justify-center mb-6 shadow-[0_0_50px_rgba(34,197,94,0.15)] border border-green-500/30">
                  <CheckCircle2 strokeWidth={1.5} className="w-16 h-16 text-green-400" />
                </div>
                <h2 className="text-3xl font-bold text-white mb-2">Analysis Complete!</h2>
                <p className="text-gray-400 mb-10">AI processing finished. Metrics and visualizations are ready.</p>
                
                <button
                  onClick={() => navigate(`/dashboard/${jobId}`)}
                  className="group flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-xl font-bold text-lg shadow-[0_0_20px_rgba(168,85,247,0.3)] transition-all hover:scale-105 active:scale-95"
                >
                  View Dashboard
                  <ChevronRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </button>
              </motion.div>
            ) : (
              <div className="flex flex-col items-center w-full">
                {/* Circular Progress */}
                <div className="relative w-48 h-48 mb-8">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle 
                      cx="96" cy="96" r="88" 
                      stroke="currentColor" 
                      strokeWidth="8" 
                      fill="transparent"
                      className="text-gray-800/80"
                    />
                    <motion.circle 
                      cx="96" cy="96" r="88" 
                      stroke="url(#progressGradient)" 
                      strokeWidth="8" 
                      fill="transparent"
                      strokeDasharray={2 * Math.PI * 88}
                      strokeDashoffset={2 * Math.PI * 88 * (1 - uploadProgress / 100)}
                      strokeLinecap="round"
                      className="transition-all duration-300 ease-out drop-shadow-[0_0_10px_rgba(168,85,247,0.5)]"
                    />
                    <defs>
                      <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                        <stop offset="0%" stopColor="#3b82f6" />
                        <stop offset="100%" stopColor="#a855f7" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div className="absolute inset-0 flex flex-col justify-center items-center backdrop-blur-[1px] rounded-full">
                    <span className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-br from-blue-400 to-purple-400">
                      {Math.round(uploadProgress)}%
                    </span>
                  </div>
                </div>

                <div className="space-y-4 w-full max-w-md bg-[#161622] p-6 rounded-2xl border border-white/5">
                  <h3 className="text-xl font-medium text-white">{currentStage}</h3>
                  <div className="flex justify-between text-sm font-medium items-center">
                    <div className="flex items-center gap-2 text-blue-400">
                      <Loader2 size={14} className="animate-spin" />
                      <span className="animate-pulse">Processing...</span>
                    </div>
                    <span className="text-gray-500 bg-[#0f0f15] px-3 py-1 rounded-full border border-white/5">
                      ~{Math.round(timeRemaining)}s remaining
                    </span>
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};