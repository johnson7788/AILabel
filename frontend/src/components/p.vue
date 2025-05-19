<template>
  <div class="main">
    <!-- Paragraph Summaries -->
    <div class="mb-6">
      <div v-for="(paragraph, index) in paragraphData" :key="index" class="mb-4">
        <h3 class="text-lg font-semibold text-gray-700 mb-1">{{ paragraph.title }}</h3>
        <p class="text-gray-600">
          <span v-for="(part, i) in splitSummary(paragraph.summary, paragraph.matches_answers)" :key="i">
            <template v-if="part.isMatch">
              <span class="highlighted-word underline cursor-pointer text-blue-500"
                    @mouseover="showSidebar(part.match)"
                    @mouseleave="onMouseLeave">
                {{ part.text }}
              </span>
            </template>
            <template v-else>
              {{ part.text }}
            </template>
          </span>
        </p>
      </div>
    </div>

    <!-- Sidebar -->
    <div class="sidebar fixed top-24 right-5 w-52 p-4 bg-gray-100 border border-gray-300 shadow-lg"
         v-if="hoveredData">
      <p><strong>User ID:</strong> {{ hoveredData.user_id }}</p>
      <p><strong>Answer:</strong> {{ hoveredData.answer }}</p>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';

const paragraphData = ref<ParagraphData[]>([
  {
    "dimension_title": "Screening 问题",
    "questions": [
      "您的性别是？",
      "您的年龄是多少？",
      "您的职业是?"
    ],
    "title": "Screening 问题",
    "summary": "根据访谈记录，共有8位用户参与了访谈。他们的性别、年龄和职业信息如下：\n\n- 性别：2位女性，2位男性，1位保密，3位未明确回答\n- 年龄：24岁、34岁、44岁\n- 职业：白领（管理类工作）、教师、出租车司机、其他未明确回答\n\n总的来说，用户的背景信息比较多样化，年龄跨度较大，职业也涵盖了不同领域。",
    "keywords": [
      "女性",
      "男性",
      "保密",
      "24岁",
      "34岁",
      "44岁",
      "白领",
      "教师",
      "出租车司机",
      "其他"
    ],
    "matches_answers": [
      {
        "word": "保密",
        "answer": "您好！我的性别是保密的，很高兴继续探讨工作和生活的平衡问题！",
        "similar_words": [
          "保密"
        ],
        "scores": [
          1.0000000000000002
        ],
        "user_id": "李升毓"
      },
      {
        "word": "保密",
        "answer": "哈哈，很高兴你对我的保密性别那么感兴趣！目前，我是一名出租车司机，我喜欢这个职业，因为它让我有机会与不同的人交流，了解他们的故事和生活经验。我认为，这种职业让我不仅仅是赚钱，还能收获人生的价值和经验。",
        "similar_words": [
          "保密"
        ],
        "scores": [
          1.0000000000000002
        ],
        "user_id": "李升毓"
      },
      {
        "word": "男性",
        "answer": "您好！我很高兴能够分享我的个人信息。我是男性的。",
        "similar_words": [
          "男性"
        ],
        "scores": [
          1.0000000000000002
        ],
        "user_id": "张大壮"
      },
      {
        "word": "白领",
        "answer": "哈哈，谢谢您的关心！我很高兴能够分享我的职业信息。我是一名白领，当前从事于管理类工作。",
        "similar_words": [
          "白领"
        ],
        "scores": [
          1.0000000000000002
        ],
        "user_id": "张大壮"
      },
      {
        "word": "教师",
        "answer": "您好！我目前是一名教师，全职工作。",
        "similar_words": [
          "教师"
        ],
        "scores": [
          1
        ],
        "user_id": "吴怡婷"
      }
    ]
  },
  {
    "dimension_title": "定义和理解",
    "questions": [
      "您如何理解工作和生活的平衡？它对您来说意味着什么？",
      "在您的生活中，什么时候您感到工作和生活是平衡的？"
    ],
    "title": "定义和理解",
    "summary": "根据访谈记录，用户们对工作和生活平衡的理解各不相同，但大多数人认为它意味着找到一种合理的时间分配和健康的生活方式。他们认为，工作和生活的平衡需要明确的时间分配、健康的生活方式和良好的习惯。同时，用户们也强调了家庭和朋友的支持对实现工作和生活平衡的重要性。他们认为，家人和朋友可以帮助他们设置边界、管理时间和精力、应对压力等方面。总之，工作和生活的平衡是一种动态的状态，需要不断地努力和调整才能达到。",
    "keywords": [
      "合理的时间分配",
      " 健康的生活方式",
      " 明确的时间分配",
      " 良好的习惯",
      " 家庭和朋友的支持"
    ]
  }
]);

const hoveredData = ref(null);

function splitSummary(summary: string, matches: Array<any>) {
  let parts = [{ text: summary, isMatch: false }];
  if (!matches) {
    return parts;
  }
  matches.forEach((match) => {
    const word = match.word;
    const regex = new RegExp(`(${word})`, 'gi');
    parts = parts.flatMap((part) => {
      if (!part.isMatch) {
        const splitText = part.text.split(regex);
        return splitText.map((text, index) => ({
          text,
          isMatch: index % 2 !== 0,
          match: index % 2 !== 0 ? match : null,
        }));
      }
      return [part];
    });
  });
  return parts;
}

function showSidebar(data) {
  hoveredData.value = data;
}

function onMouseLeave() {
  hoveredData.value = null;
}
</script>

<style lang="scss" scoped>
.main {
  margin: 100px auto;
}

.sidebar {
  transition: all 0.3s ease;
}

.highlighted-word:hover {
  font-weight: bold;
  background-color: #f0f0f0;
}
</style>
