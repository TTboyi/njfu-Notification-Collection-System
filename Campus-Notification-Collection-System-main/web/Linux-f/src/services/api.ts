import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
    baseURL: API_BASE_URL
});

export const getCompetitions = async () => {
    const response = await api.get('/competitions');
    return response.data;
};

export const getNotices = async () => {
    const response = await api.get('/notices');
    return response.data;
};

export const getExams = async () => {
    const response = await api.get('/exams');
    return response.data;
};

export const getInternships = async () => {
    const response = await api.get('/internships');
    return response.data;
};

export const searchItems = async (keyword: string) => {
    const response = await api.get(`/search?keyword=${encodeURIComponent(keyword)}`);
    return response.data;
};

export const getItemDetails = async (table: string, id: number) => {
    const response = await api.get(`/item/${table}/${id}`);
    return response.data;
};

export const toggleFavorite = async (table: string, id: number) => {
    const response = await api.post(`/favorite/${table}/${id}`);
    return response.data;
};

export const updateMockNotices = async (content: string) => {
  try {
    console.log('发送更新请求到:', `${API_BASE_URL}/api/update-mock-notices`);
    console.log('请求内容长度:', content.length);
    
    const response = await axios.post(`${API_BASE_URL}/api/update-mock-notices`, { content });
    console.log('更新响应:', response.data);
    
    return response.data;
  } catch (error) {
    console.error('更新 mockNotices.ts 文件失败:', error);
    if (axios.isAxiosError(error)) {
      console.error('错误详情:', error.response?.data);
    }
    throw error;
  }
}; 