import { createRouter, createWebHistory } from "vue-router";
import {
    type RouteLocationNormalized,
    type NavigationGuardNext,
} from "vue-router";

import Home from "../components/Home.vue";
import Login from "../components/Login.vue";
import Article from "../components/Article/index.vue";
import ArticleEditor from "../components/Article/ArticleEditor.vue";
import Traveling from "../components/Traveling.vue";
import Dating from "../components/Dating/index.vue";
import { checkSessionId } from "../utils/utils";

// 管理员权限验证
const adminAuthGuard = async (
    // 在参数名前添加下划线表示这个参数是有意不使用的
    _to: RouteLocationNormalized,
    _from: RouteLocationNormalized,
    next: NavigationGuardNext
) => {
    const admin_id = await checkSessionId();
    if (admin_id) {
        next();
    } else {
        next("/");
    }
};

const routes = [
    {
        path: "/",
        name: "Home",
        component: Home,
    },
    {
        path: "/login",
        name: "Login",
        component: Login,
    },
    {
        path: "/articles",
        name: "Articles",
        component: Article,
    },
    {
        path: "/articles/:id",
        name: "Article",
        component: Article,
    },
    {
        path: "/article/new",
        name: "NewArticle",
        component: ArticleEditor,
        beforeEnter: adminAuthGuard,
    },
    {
        path: "/article/edit/:id",
        name: "EditArticle",
        component: ArticleEditor,
        beforeEnter: adminAuthGuard,
    },
    {
        path: "/traveling",
        name: "Traveling",
        component: Traveling,
    },
    {
        path: "/dating",
        name: "Dating",
        component: Dating,
    },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior() {
        // 始终滚动到顶部
        return { top: 0 };
    },
});

export default router;
