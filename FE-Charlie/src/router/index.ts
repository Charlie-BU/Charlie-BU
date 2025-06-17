import { createRouter, createWebHistory } from "vue-router";
import Home from "../components/Home.vue";
import Login from "../components/Login.vue";
import Article from "../components/Article.vue";

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
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
