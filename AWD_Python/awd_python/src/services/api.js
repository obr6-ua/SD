// services/api.js
import axios from 'axios';

const API_URL = 'http://10.0.2.15:5000'; // URL de tu API

export const getBoard = async () => {
    try {
        const response = await axios.get(`${API_URL}/ruta-del-endpoint-del-tablero`);
        return response.data;
    } catch (error) {
        console.error('Error al obtener el tablero:', error);
        throw error;
    }
};
