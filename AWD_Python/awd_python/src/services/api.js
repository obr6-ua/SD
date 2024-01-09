import axios from 'axios';

const API_URL = 'http://192.68.23.1:5000'; // URL de tu API

let pollingInterval;

export const startPolling = () => {
  pollingInterval = setInterval(async () => {
    try {
      const response = await axios.get(`${API_URL}/mapa`);
      console.log(response.data);
      // Aquí puedes hacer algo con los datos, como actualizar el estado
    } catch (error) {
      console.error('Error al obtener el tablero:', error);
    }
  }, 500); // Intervalo de 0.5 segundos
};

export const stopPolling = () => {
  clearInterval(pollingInterval);
};
