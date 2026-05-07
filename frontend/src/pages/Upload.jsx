import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { VideoUploader } from '../components/video/VideoUploader.jsx';
import { uploadVideo } from '../services/api.js';

export const Upload = () => {
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async (file, modelPath) => {
    try {
      setIsLoading(true);
      const jobId = await uploadVideo(file, modelPath);
      navigate(`/dashboard/${jobId}`);
    } catch (error) {
      console.error(error);
      alert('Upload failed: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-full pt-10">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold mb-4 text-white">Analyze Retail Foot-traffic</h1>
        <p className="text-gray-400 max-w-lg mx-auto">
          Upload security footage to detect customers, measure queue times, and generate interactive heatmaps.
        </p>
      </div>
      <VideoUploader onSubmit={handleUpload} isLoading={isLoading} />
    </div>
  );
};