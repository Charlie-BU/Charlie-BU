import axios from "axios";
import type {
    AxiosInstance,
    AxiosError,
    AxiosResponse,
    InternalAxiosRequestConfig,
} from "axios";
import { ElMessage } from "element-plus";

// 本地
const DEVELOP_URL = "http://localhost:1209";
// 使用接口反向代理
const PRODUCTION_URL = "http://124.223.93.75:1209";

const service: AxiosInstance = axios.create({
    baseURL: DEVELOP_URL,
    timeout: 20000,
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
