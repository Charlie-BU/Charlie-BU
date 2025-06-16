import { createApp } from "vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import "./style.css";
import App from "./App.vue";

export let LANG = "Chinese";

const app = createApp(App);
app.use(ElementPlus);
// 设置为全局属性
app.config.globalProperties.$LANG = LANG;
app.mount("#app");
