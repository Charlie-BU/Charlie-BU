import { Message } from "@arco-design/web-vue";
import axios from "axios";
import type {
    AxiosInstance,
    AxiosError,
    AxiosResponse,
    InternalAxiosRequestConfig,
} from "axios";


const isDev = import.meta.env.DEV;
// @ts-ignore
const DEVELOP_URL = "http://localhost:1209";
// @ts-ignore
const PRODUCTION_URL = "https://charliebu.cn/api";

const service: AxiosInstance = axios.create({
    baseURL: isDev ? DEVELOP_URL : PRODUCTION_URL,
    timeout: 50000,
    withCredentials: true, // 自动携带cookies
});

service.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
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
