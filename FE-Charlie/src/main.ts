import { createApp } from "vue";
import ElementPlus from "element-plus";
import ArcoVue from '@arco-design/web-vue';
import "element-plus/dist/index.css";
import "./assets/styles/buttons.css";
import "./style.css";
import '@arco-design/web-vue/dist/arco.css';

import App from "./App.vue";
import router from "./router";
// 导入所有图标
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import "highlight.js/styles/github-dark.css";

const app = createApp(App);
app.use(ElementPlus);
app.use(ArcoVue);
app.use(router);

// 全局注册所有图标，具体查看：https://element-plus.org/zh-CN/component/icon.html
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

app.mount("#app");
