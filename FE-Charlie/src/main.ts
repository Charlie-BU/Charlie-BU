import { createApp } from "vue";
import ElementPlus from "element-plus";
import ArcoVue from '@arco-design/web-vue';
import "element-plus/dist/index.css";
import "./assets/styles/buttons.css";
import "./style.css";
import '@arco-design/web-vue/dist/arco.css';


import App from "./App.vue";
import router from "./router";

// 导入所有icon
import * as ArcoIconsVue from '@arco-design/web-vue/es/icon';
import * as ElementPlusIconsVue from "@element-plus/icons-vue";
import "highlight.js/styles/github-dark.css";

const app = createApp(App);
app.use(ElementPlus);
app.use(ArcoVue);
app.use(router);

// 全局注册所有icon，具体查看：https://element-plus.org/zh-CN/component/icon.html
for (const [key, component] of Object.entries(ArcoIconsVue)) {
    app.component(key, component);
}
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component);
}

app.mount("#app");
// 在Vite中，使用import.meta.env来获取环境变量
// console.log("环境变量:", import.meta.env);
