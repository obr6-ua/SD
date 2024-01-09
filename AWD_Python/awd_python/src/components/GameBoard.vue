<template>
  <div class="board-container">
    <h1>ART WITH DRONES</h1> <!-- Título agregado aquí -->
    <div v-for="(row, rowIndex) in boardMatrix" :key="rowIndex" class="row">
      <span
        v-for="(cell, cellIndex) in row"
        :key="cellIndex"
        :class="getCellClass(cell)"
        class="cell"
      >
        {{ getCellContent(cell) }}
      </span>
    </div>
  </div>
</template>


<script>
import axios from 'axios';

export default {
  data() {
    return {
      board: {}, // Objeto original de la API
      boardMatrix: [], // Matriz convertida para usar en la plantilla
      pollingInterval: null,
    };
  },
  mounted() {
    this.startPolling();
  },
  beforeUnmount() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
    }
  },
  methods: {
    async fetchBoard() {
      try {
        const response = await axios.get('http://127.0.0.1:5000/mapa');
        this.board = response.data;
        this.boardMatrix = this.convertToMatrix(this.board);
      } catch (error) {
        console.error('Error al obtener el tablero:', error);
      }
    },
    startPolling() {
      this.fetchBoard(); // Fetch immediately, then start polling
      this.pollingInterval = setInterval(this.fetchBoard, 500); // Poll every 0.5 seconds
    },
    getCellClass(cell) {
  if (!cell || !cell.color) return '';
  const color = cell.color === 'red' ? 'light-red' : 'light-green';
  return color;
}
,
    getCellContent(cell) {
      return cell && cell.id ? cell.id : '';
    },
    convertToMatrix(boardObject) {
      const size = Math.sqrt(Object.keys(boardObject).length); // Asumiendo que el tablero es cuadrado
      return Array.from({ length: size }, (_, rowIndex) => {
        return Array.from({ length: size }, (_, colIndex) => {
          return boardObject[`${rowIndex},${colIndex}`];
        });
      });
    },
  }
};
</script>

<style>
.board-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #333; /* Fondo oscuro para el tablero */
}


h1 {
  color: #fff; /* o el color que prefieras */
  text-align: center;
  margin-bottom: 20px; /* Espacio entre el título y el mapa */
}


.row {
  display: flex;
  justify-content: center;
}

.cell {
  padding: 5px;
  margin: 2px;
  display: flex; /* Cambio importante aquí */
  align-items: center; /* Centra el contenido verticalmente */
  justify-content: center; /* Centra el contenido horizontalmente */
  width: 20px;
  height: 20px; /* Agrega altura a las celdas para hacerlas cuadradas */
  text-align: center;
  border: 1px solid #eee;
}

.red {
  color: red;
}

.green {
  color: green;
}

.light-red {
  background-color: #ffcccc; /* Rojo claro */
}

.light-green {
  background-color: #ccffcc; /* Verde claro */
}

</style>