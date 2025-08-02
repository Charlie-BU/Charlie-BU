import { createRouter, createWebHistory } from "vue-router";
import Home from "../components/Home.vue";
import Login from "../components/Login.vue";
import Article from "../components/Article.vue";
import ArticleEditor from "../components/ArticleEditor.vue";
import Traveling from "../components/Traveling.vue";
import Mindroom from "../components/mindroom/Mindroom.vue";
import Cookies from "js-cookie";
import { request } from "../api/request";
import {
    type RouteLocationNormalized,
    type NavigationGuardNext,
} from "vue-router";

// 管理员权限验证
const adminAuthGuard = async (
    // 在参数名前添加下划线表示这个参数是有意不使用的
    _to: RouteLocationNormalized,
    _from: RouteLocationNormalized,
    next: NavigationGuardNext
) => {
    try {
        const res = await request.post("/api/check_sessionid", {
            sessionid: Cookies.get("sessionid"),
        });
        if (res.data.status === 200 && res.data.admin_id) {
            next();
        } else {
            next("/");
        }
    } catch (error) {
        console.error("权限验证失败:", error);
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
        path: "/mindroom",
        name: "MindroomList",
        component: Mindroom,
    },
    {
        path: "/mindroom/:id",
        name: "MindroomDetail",
        component: Mindroom,
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
