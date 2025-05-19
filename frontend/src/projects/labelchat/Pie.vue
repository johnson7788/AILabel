<template>
  <div class="w-full h-96 border border-gray-100 bg-green-100">
    <div ref="plotPieContainer" class="w-full h-96 my-10"></div>
  </div>
</template>

<script setup>
//使用echarts绘图，根据不同的数据和要求绘制不同的图像, 画1个柱状图
import { ref, onMounted, computed, watch, toRefs, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts';
import { ElNotification } from 'element-plus';
const plotPieContainer = ref(null);

let props = defineProps({
  dataProps: {
    type: Object,
    required: true,
    default: {
      "data": [
          { value: 1048, name: 'Search Engine' },
          { value: 735, name: 'Direct' },
          { value: 580, name: 'Email' },
          { value: 484, name: 'Union Ads' },
          { value: 300, name: 'Video Ads' }
        ],
      "title": "测试饼图"
    }
  }
});

const plotPie = (title,nameValueData) => {
  var myChart = echarts.init(plotPieContainer.value)
  const option = {
    title: {
      text: title,
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      top: '5%',
      left: 'center'
    },
    series: [
      {
        name: 'Access From',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 40,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: nameValueData
      }
    ]

  };
  option && myChart.setOption(option)
  window.onresize = () => {
    myChart.resize()
  }
};

onMounted(() => {
  plotPie(props.dataProps.title, props.dataProps.data)
});


</script>

<style lang="scss" scoped></style>