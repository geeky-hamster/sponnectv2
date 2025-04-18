<template>
  <canvas ref="chartCanvas"></canvas>
</template>

<script>
import { ref, onMounted, watch, toRefs } from 'vue';
import Chart from 'chart.js/auto';

export default {
  name: 'HorizontalBarChart',
  props: {
    chartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({
        indexAxis: 'y', // This makes the bars horizontal
        plugins: {
          legend: {
            position: 'right'
          }
        }
      })
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

      const defaultOptions = {
        indexAxis: 'y',
        plugins: {
          legend: {
            position: 'right'
          }
        }
      };

      if (chartCanvas.value) {
        chart.value = new Chart(chartCanvas.value, {
          type: 'bar',
          data: chartData.value,
          options: { ...defaultOptions, ...options.value }
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