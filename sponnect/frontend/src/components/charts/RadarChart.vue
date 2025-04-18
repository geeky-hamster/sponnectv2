<template>
  <canvas ref="chartCanvas"></canvas>
</template>

<script>
import { ref, onMounted, watch, toRefs } from 'vue';
import Chart from 'chart.js/auto';

export default {
  name: 'RadarChart',
  props: {
    chartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({
        elements: {
          line: {
            borderWidth: 3
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
        elements: {
          line: {
            borderWidth: 3
          }
        }
      };

      if (chartCanvas.value) {
        chart.value = new Chart(chartCanvas.value, {
          type: 'radar',
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