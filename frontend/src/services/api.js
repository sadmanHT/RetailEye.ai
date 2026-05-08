import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Uploads a video file for analysis.
 * @param {File} videoFile - The video file to upload.
 * @param {string} [modelPath] - Optional path to the YOLO model.
 * @returns {Promise<string>} The job ID.
 */
export const uploadVideo = async (videoFile, modelPath = '') => {
  try {
    const formData = new FormData();
    formData.append('video', videoFile);
    if (modelPath) {
      formData.append('model_path', modelPath);
    }

    const response = await apiClient.post('/analyze/video', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data.job_id;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || error.message || 'Failed to upload video'
    );
  }
};

/**
 * Retrieves the status of a specific processing job.
 * @param {string} jobId - The ID of the job.
 * @returns {Promise<Object>} The job status object.
 */
export const getJobStatus = async (jobId) => {
  try {
    const response = await apiClient.get(`/job/status/${jobId}`);
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || error.message || 'Failed to get job status'
    );
  }
};

/**
 * Retrieves the analytics data for a specific processing job.
 * @param {string} jobId - The ID of the job.
 * @returns {Promise<Object>} The analytics data object.
 */
export const getAnalytics = async (jobId) => {
  try {
    const response = await apiClient.get(`/analytics/${jobId}`);
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || error.message || 'Failed to get analytics'
    );
  }
};

/**
 * Checks the health status of the API.
 * @returns {Promise<Object>} The health status object.
 */
export const getHealth = async () => {
  try {
    const response = await apiClient.get('/health');
    return response.data;
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || error.message || 'Failed to get health status'
    );
  }
};
