import axios from "axios";
import type {
    AxiosInstance,
    AxiosError,
    AxiosResponse,
    InternalAxiosRequestConfig,
} from "axios";
import { ElMessage } from "element-plus";

// 本地：为了防止打包后网站被认定不安全，打包前须注释
// const DEVELOP_URL = "http://localhost:1209";
// 使用接口反向代理
// @ts-ignore
// const PRODUCTION_URL = "http://124.223.93.75:90";
const PRODUCTION_URL = "https://charliebu.cn/api";

const service: AxiosInstance = axios.create({
    baseURL: PRODUCTION_URL,
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
            ElMessage.error("请求失败：" + response.status);
            return Promise.reject(response);
        }
    },
    (error: AxiosError) => {
        console.log(error);
        ElMessage.error(error.message || "请求失败，请稍后重试");
        return Promise.reject(error);
    }
);

export default service;
export { service as request };
