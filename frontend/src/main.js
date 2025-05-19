import { createApp } from 'vue';
import ElementPlus from 'element-plus';
import router from "./router/index";
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import { createI18n } from 'vue-i18n'
import App from './App.vue';
import store from './store';
import * as ElementPlusIconsVue from '@element-plus/icons-vue';
import scrollto from 'vue-scrollto';
import './assets/main.css';
import 'element-plus/dist/index.css';

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const app = createApp(App)
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

const vAutogrow = {
    //自动扩充元素的高度，例如textarea, 防止出现滚动条
    mounted: function (el) {
        // 当元素插入DOM时，设置textarea的高度为scrollHeight
        el.style.height = 'auto'
        el.style.height = (el.scrollHeight) + 'px'
    },
    updated: function (el) {
        // 当组件更新时，重新设置textarea的高度
        el.style.height = (el.scrollHeight) + 'px'
    }
};
app.directive('autogrow', vAutogrow);


// 创建 i18n 实例
const i18n = createI18n({
    legacy: false,
    locale: localStorage.getItem('language') || 'en' // 从本地存储中获取语言，默认语言为 'en'
  });

// 注册 i18n 插件
app.use(i18n);
app.use(scrollto);
app.use(store).use(ElementPlus).use(pinia).use(router).mount('#app')
