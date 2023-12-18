<template>
  <div class="map-display">
    <div v-if="mapData.length > 0">
      <div v-for="(row, rowIndex) in mapData" :key="rowIndex" class="map-row">
        <span v-for="(cell, cellIndex) in row" :key="cellIndex" class="map-cell">
          {{ cell }}
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
    axios.get('http://0.0.0.0:5000/mapa')
      .then(response => {
        this.mapData = response.data;
      })
      .catch(error => {
        console.error("Error al cargar el mapa: ", error);
      });
  }
}
</script>

<style scoped>
.map-row {
  /* Estilos para cada fila del mapa */
}
.map-cell {
  /* Estilos para cada celda del mapa */
  display: inline-block;
  margin-right: 10px;
}
</style>