<template>
  <div class="flex min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <div class="w-64 bg-white shadow-lg p-4 space-y-4">
      <h2 class="text-lg font-semibold mb-4">工具栏</h2>
      <button @click="exportAsImage"
        class="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors">
        导出为图片
      </button>
      <button @click="exportAsPDF"
        class="w-full bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors">
        导出为PDF
      </button>
    </div>

    <!-- Main Content -->
    <div class="flex-1 p-8" id="content">
      <EditableContent tag="h1" v-model="title" custom-class="text-3xl font-bold mb-6 text-gray-800" />

      <EditableContent tag="p" v-model="paragraph" custom-class="text-gray-600 mb-8 leading-relaxed" />

      <table class="w-full border-collapse border border-gray-300 bg-white">
        <tbody>
          <tr v-for="(row, rowIndex) in tableData" :key="rowIndex">
            <td v-for="(cell, colIndex) in row" :key="colIndex" class="border border-gray-300 p-3">
              <EditableContent tag="div" v-model="tableData[rowIndex][colIndex]" custom-class="w-full h-full" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import EditableContent from '../utils/EditableContent.vue';

const title = ref('可编辑的网页标题');
const paragraph = ref('这是一段可编辑的段落内容。双击任何内容都可以进行编辑。您可以通过左侧的按钮将内容导出为图片或PDF格式。');

const tableData = ref([
  ['产品', '价格', '库存'],
  ['商品A', '¥100', '50'],
  ['商品B', '¥200', '30'],
  ['商品C', '¥300', '20'],
]);

const exportAsImage = async () => {
  const element = document.getElementById('content');
  if (element) {
    const canvas = await html2canvas(element);
    const link = document.createElement('a');
    link.download = 'page-content.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
  }
};

const exportAsPDF = async () => {
  const element = document.getElementById('content');
  if (element) {
    const canvas = await html2canvas(element);
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF('p', 'mm', 'a4');
    const imgProps = pdf.getImageProperties(imgData);
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
    pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
    pdf.save('page-content.pdf');
  }
};

const updateTableCell = (rowIndex: number, colIndex: number, value: string) => {
  tableData.value[rowIndex][colIndex] = value;
};
</script>
