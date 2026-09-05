import { Message } from "@arco-design/web-vue";
import axios from "axios";
import type {
    AxiosInstance,
    AxiosError,
    AxiosResponse,
    InternalAxiosRequestConfig,
} from "axios";

const PUBLIC_BASE_URL = import.meta.env.VITE_API_PUBLIC_BASE_URL || "/api";

const service: AxiosInstance = axios.create({
    baseURL: PUBLIC_BASE_URL,
    timeout: 50000,
    withCredentials: true, // 自动携带cookies
});

service.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        if (config.url?.startsWith("/api/")) {
            config.url = config.url.slice("/api".length);
        }
        return config;
    },
    (error: AxiosError) => {
        console.log(error);
        return Promise.reject(error);
    }
);

service.interceptors.response.use(
    (response: AxiosResponse) => {
        if (response.status === 200) {
            return response;
        } else {
            Message.error("请求失败：" + response.status);
            return Promise.reject(response);
        }
    },
    (error: AxiosError) => {
        console.log(error);
        Message.error(error.message || "请求失败，请稍后重试");
        return Promise.reject(error);
    }
);

export default service;
export { service as request };
