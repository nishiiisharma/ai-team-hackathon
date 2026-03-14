import axios from 'axios';

const API = axios.create({
    baseURL: '/api'
});

export const uploadMenu = async (file, userId) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('user_id', userId);
    const res = await API.post('/upload-menu', formData);
    return res.data;
};

export const analyzeMenu = async (userId) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    const res = await API.post('/analyze', formData);
    return res.data;
};

export const getIngredientsStock = async (userId) => {
    const res = await API.get('/ingredients-stock', { params: { user_id: userId } });
    return res.data;
};

export const predictQuantity = async (userId) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    const res = await API.post('/predict', formData);
    return res.data;
};

export const getCart = async (userId) => {
    const res = await API.get('/cart', { params: { user_id: userId } });
    return res.data;
};
