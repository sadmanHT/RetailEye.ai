import { useState, useEffect, useCallback } from 'react';
import { getJobStatus } from '../services/api.js';

export const useJobPolling = (jobId, enabled = true) => {
  const [status, setStatus] = useState(null);
  const [progress, setProgress] = useState(0);
  const [resultPath, setResultPath] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const pollStatus = useCallback(async () => {
    if (!jobId) return;

    try {
      setIsLoading(true);
      const data = await getJobStatus(jobId);
      
      setStatus(data.status);
      setProgress(data.progress || 0);
      
      if (data.result_path) {
        setResultPath(data.result_path);
      }
      
      if (data.error) {
        setError(data.error);
      }
    } catch (err) {
      setError(err.message);
      setStatus('failed');
    } finally {
      setIsLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    let intervalId;

    const shouldPoll = enabled && jobId && status !== 'completed' && status !== 'failed';

    if (shouldPoll) {
      // Poll immediately upon satisfying conditions
      pollStatus();
      
      intervalId = setInterval(() => {
        pollStatus();
      }, 2000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [enabled, jobId, status, pollStatus]);

  return { status, progress, resultPath, error, isLoading };
};