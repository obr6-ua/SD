<template>
  <div class="map-display">
    <div v-if="mapData.length > 0">
      <div v-for="(row, rowIndex) in mapData" :key="rowIndex" class="map-row">
        <span v-for="(cell, cellIndex) in row" :key="cellIndex" :class="{'map-cell': true, 'drone': cell.id, 'completed': cell.completado}">
          {{ cell.id }}
        </span>
      </div>
    </div>
    <div v-else>
      Cargando mapa o mapa no disponible...
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'MapDisplay',
  data() {
    return {
      mapData: []
    };
  },
  mounted() {
    this.fetchMapData();
    this.startPolling();
  },
  methods: {
    fetchMapData() {
      axios.get('http://127.0.0.1:5000/mapa')
        .then(response => {
          this.mapData = response.data;
        })
        .catch(error => {
          console.error("Error al cargar el mapa: ", error);
        });
    },
    startPolling() {
      setInterval(this.fetchMapData, 1000); // Poll every second for real-time updates
    }
  }
}
</script>

<style scoped>
.map-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-family: Arial, sans-serif;
  margin-top: 20px;
}

.map-row {
  display: flex;
}

.map-cell {
  width: 20px;
  height: 20px;
  border: 1px solid #ccc;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 1px;
}

.drone {
  background-color: #f0f0f0;
  color: red; /* Color de los drones */
}

.completed {
  color: green; /* Color de los drones completados */
}
</style>