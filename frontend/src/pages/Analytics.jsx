import React from 'react';
import { useParams } from 'react-router-dom';

export const Analytics = () => {
  const { jobId } = useParams();

  return (
    <div className="w-full max-w-6xl mx-auto p-6 text-white space-y-8">
      <h1 className="text-3xl font-bold">Deep Analytics</h1>
      <p className="text-gray-400">Viewing extended reporting metrics for Job: {jobId ? jobId : 'No job selected'}</p>
      
      {!jobId && (
        <div className="p-8 bg-[#12121a] rounded-xl border border-white/5 mt-8 text-center text-gray-500">
          Please upload a video first to view deep analytics.
        </div>
      )}
    </div>
  );
};