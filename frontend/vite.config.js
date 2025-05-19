import { fileURLToPath, URL } from 'node:url'
import vueJsx from "@vitejs/plugin-vue-jsx";
import { defineConfig,searchForWorkspaceRoot } from 'vite'
import vue from '@vitejs/plugin-vue'

// "src/projects/resume/about.vue", "src/projects/resume/education.vue", "src/projects/resume/experience.vue", "src/projects/resume/skills.vue", 
// "src/projects/resume/index.vue","src/projects/resume/navbar.vue", "src/projects/resume/projects.vue","src/projects/resume/interests.vue"
const filesNeedToExclude = ["src/components/0.vue", "src/components/1.vue", "src/components/2.vue", "src/components/3.vue", "src/components/a.vue",
"src/components/b.vue","src/components/c.vue","src/components/d.vue","src/components/e.vue","src/components/f.vue","src/components/g.vue",
"src/components/h.vue","src/components/i.vue","src/components/j.vue","src/components/k.vue","src/components/l.vue","src/components/m.vue",
"src/components/n.vue","src/components/o.vue","src/components/p.vue","src/components/q.vue","src/components/r.vue","src/components/s.vue",
"src/components/t.vue","src/components/u.vue","src/components/v.vue","src/components/w.vue","src/components/x.vue","src/components/y.vue",
];

const filesPathToExclude = filesNeedToExclude.map((src) => {
  return fileURLToPath(new URL(src, import.meta.url));
});
// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: '127.0.0.1', // 设置为你想要的监听地址
    port: 7081, // 设置为你想要的端口号
    fs: {
      // 添加你的fontawesome文件路径到allow列表
      allow: [searchForWorkspaceRoot(process.cwd()),
        '../node_modules/font-awesome/fonts',
        '../node_modules/@fortawesome/fontawesome-free',
      ],
    },
  },
  build: {
    rollupOptions: {
      external: [
        ...filesPathToExclude
      ],
    },
  },
  plugins: [
    vue(),
    vueJsx()
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
