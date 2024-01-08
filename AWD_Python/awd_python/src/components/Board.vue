<template>
  <div>
    <div v-for="(row, rowIndex) in board" :key="rowIndex">
      <span v-for="(cell, cellIndex) in row" :key="cellIndex">{{ cell }}</span>
    </div>
  </div>
</template>

<script>
import { getBoard } from '@/services/api';

export default {
  data() {
    return {
      board: []
    };
  },
  async mounted() {
    try {
      this.board = await getBoard();
    } catch (error) {
      console.error('Error al montar el componente:', error);
    }
  }
};
</script>