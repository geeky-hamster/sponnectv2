<template>
  <canvas ref="chartCanvas"></canvas>
</template>

<script>
import { ref, onMounted, watch, toRefs } from 'vue';
import Chart from 'chart.js/auto';

export default {
  name: 'DoughnutChart',
  props: {
    chartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    const chartCanvas = ref(null);
    const chart = ref(null);
    const { chartData, options } = toRefs(props);

    const createChart = () => {
      if (chart.value) {
        chart.value.destroy();
      }

      if (chartCanvas.value) {
        chart.value = new Chart(chartCanvas.value, {
          type: 'doughnut',
          data: chartData.value,
          options: options.value
        });
      }
    };

    onMounted(() => {
      createChart();
    });

    watch([chartData, options], () => {
      createChart();
    }, { deep: true });

    return {
      chartCanvas
    };
  }
};
</script> 