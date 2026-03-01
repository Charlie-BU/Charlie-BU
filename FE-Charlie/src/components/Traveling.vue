<template>
    <el-main class="main-content">
        <section class="map-section">
            <div class="section-title">
                <h2>{{ t('worldMap') }}
                    <span class="corner-count">{{ countriesCount }} {{ t('countries') }}</span>
                </h2>
            </div>
            <div class="map-container" ref="worldMapContainer"></div>
        </section>

        <section class="map-section">
            <div class="section-title">
                <h2>{{ t('chinaMap') }}
                    <span class="corner-count">{{ citiesCount }} {{ t('cities') }}</span>
                </h2>
            </div>
            <div class="map-container china-map-container" ref="chinaMapContainer"></div>
        </section>

        <section class="places-section">
            <div class="section-title">
                <h2>
                    {{ t('placesVisited') }}
                    <span class="corner-count">{{ places.length }} {{ t('corners') }}</span>
                </h2>
            </div>
            <el-row :gutter="24" class="places-grid">
                <el-col :xs="24" :sm="12" :md="8" v-for="(place, index) in places" :key="index"
                    style="margin-top: 50px;">
                    <el-card class="place-card" shadow="hover" @click.stop="showPlaceDetails(place)" ref="placeCards">
                        <div class="place-header">
                            <h3>{{ place.city }}, {{ place.country }}</h3>
                            <div class="place-date">{{ formatDateRange(place.dateStart, place.dateEnd, LANG) }}</div>
                        </div>
                        <p class="place-description">{{ place.description }}</p>
                        <div class="place-photos" v-if="place.photos && place.photos.length > 0"
                            :style="{ padding: isMobileRef ? '0 25px' : '0 35px', display: 'flex', justifyContent: 'center', alignItems: 'center', flexWrap: 'wrap' }">
                            <el-image v-for="(photo, photoIndex) in place.photos" :key="photoIndex"
                                :src="photo.thumb_url || photo.url" fit="cover" class="place-photo" lazy
                                @click.stop="openPhotoPreview(place, photoIndex)"></el-image>
                        </div>
                    </el-card>
                </el-col>
            </el-row>
        </section>


        <!-- 图片预览模态弹框 -->
        <Modal v-model:visible="photoPreviewVisible" type="custom" :title="currentPlace?.city || ''" :showCancel="false"
            :showConfirm="false">
            <div class="photo-preview-container">
                <div class="photo-preview-image-container">
                    <img v-if="currentPhotos && currentPhotoIndex >= 0" :src="currentPhotos[currentPhotoIndex]?.url"
                        class="preview-image" />
                </div>
                <div class="photo-preview-controls">
                    <button class="preview-nav-button" @click="prevPhoto" :disabled="currentPhotoIndex <= 0">
                        <el-icon>
                            <ArrowLeft />
                        </el-icon>
                    </button>
                    <div class="photo-preview-counter">
                        {{ currentPhotoIndex + 1 }} / {{ currentPhotos?.length || 0 }}
                    </div>
                    <button class="preview-nav-button" @click="nextPhoto"
                        :disabled="currentPhotoIndex >= (currentPhotos?.length - 1)">
                        <el-icon>
                            <ArrowRight />
                        </el-icon>
                    </button>
                </div>
            </div>
        </Modal>
    </el-main>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount, watch, nextTick } from 'vue';
import Modal from './Modal.vue';
import * as echarts from 'echarts';
import { Message } from "@arco-design/web-vue";

import { request } from '../api/request';
import { getContinentForCountry } from '../utils/map';
import { isMobile, formatDateRange, getDate } from '../utils/utils';

const isMobileRef = ref(isMobile());
// 地图容器引用
const worldMapContainer = ref(null);
const chinaMapContainer = ref(null);

// 地图实例
let worldMap = null;
let chinaMap = null;

// 地点数据
const places = ref([]);

// 创建一个Map来存储已经观察的元素，避免重复观察
const observedPlaces = new Map();
// 存储observer实例，以便在组件卸载时清理
let placeObserver = null;

// 创建Intersection Observer实例
const createObserver = () => {
    const options = {
        root: null, // 使用视口作为根元素
        rootMargin: isMobileRef.value ? '50px' : '0px',
        threshold: 0 // 元素一进入视口立刻触发回调
    };

    return new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // 获取对应的place数据
                const index = Number(entry.target.dataset.index);
                const place = places.value[index];

                if (place && !observedPlaces.get(place.id)) {
                    // 标记该place已经被观察过，避免重复请求
                    observedPlaces.set(place.id, true);
                    // 加载该place的照片
                    fetchTravelPhotos(place);
                }

                // 停止观察该元素
                observer.unobserve(entry.target);
            }
        });
    }, options);
};

// 观察元素的函数
const observePlaceCards = () => {
    // 如果已经有observer实例，先断开连接
    if (placeObserver) {
        placeObserver.disconnect();
    }

    // 创建新的observer
    placeObserver = createObserver();
    const placeCardElements = document.querySelectorAll('.place-card');

    placeCardElements.forEach((card, index) => {
        // 为每个card添加索引属性，用于在回调中找到对应的place数据
        card.dataset.index = index;
        placeObserver.observe(card);
    });
};

onMounted(async () => {
    await fetchTravelData();
    // 在下一个tick中设置观察者，确保DOM已经更新
    setTimeout(() => {
        observePlaceCards();
    }, 100);
});

// 监听places数组变化，当有新的地点数据加载时重新设置观察者
watch(() => places.value.length, async (newLength, oldLength) => {
    if (newLength > oldLength) {
        // 等待DOM更新
        await nextTick();
        // 重新设置观察者
        observePlaceCards();
    }
});

// 语言设置
const LANG = localStorage.getItem("LANG") || "Chinese";

const t = (key) => {
    const translations = {
        worldMap: {
            Chinese: "🌍 全球",
            English: "🌍 Global"
        },
        chinaMap: {
            Chinese: "🇨🇳 中国",
            English: "🇨🇳 China"
        },
        placesVisited: {
            Chinese: "👣 足迹",
            English: "👣 Footprint On"
        },
        countries: {
            Chinese: "个国家",
            English: "Countries"
        },
        cities: {
            Chinese: "个城市",
            English: "Cities"
        },
        corners: {
            Chinese: "个角落",
            English: "Corners"
        },
        statisticsTime: {
            Chinese: "截止到",
            English: "Updated on"
        }
    };
    return translations[key]?.[LANG] || key;
};



// 获取旅行数据
const fetchTravelData = async () => {
    try {
        const response = await request.post("/api/travel/getPlacesBeenTo", {
            lang: LANG,
        });
        places.value = response.data.places || [];

        // 已访问的国家和城市（使用Set去重）
        const visitedCountries = [...new Set(places.value.map(place => place.country_ENG))];
        const visitedCities = [...new Set(places.value
            .filter(place => place.country === '中国' || place.country === 'China')
            .map(place => place.city_CH))];

        // 初始化地图
        initWorldMap(visitedCountries);
        initChinaMap(visitedCities);
    } catch (error) {
        console.error('Failed to fetch travel data:', error);
        Message.error('获取旅行数据失败');
    }
};

// 获取每个地点的照片
const fetchTravelPhotos = async (place) => {
    if (place.photos && place.photos.length > 0) {
        return;
    }
    try {
        const res = await request.post("/api/travel/getTravelPhotos", {
            travelId: place.id,
        });
        place.photos = res.data.photos || [];
        place.photos = place.photos.map(photo => {
            const thumb_url = `${photo.url}?x-oss-process=image/resize,w_300`;
            return {
                ...photo,
                thumb_url
            };
        });
    } catch (error) {
        console.error('Failed to fetch travel photos:', error);
        Message.error('获取旅行图片失败');
    }
};

// 显示地点详情
const showPlaceDetails = (place) => {
    console.log('Place details:', place);
};

// 图片预览相关
const photoPreviewVisible = ref(false);
const currentPlace = ref(null);
const currentPhotos = ref([]);
const currentPhotoIndex = ref(0);

// 打开图片预览
const openPhotoPreview = (place, photoIndex) => {
    currentPlace.value = place;
    currentPhotos.value = place.photos;
    currentPhotoIndex.value = photoIndex;
    photoPreviewVisible.value = true;
    // 添加键盘事件监听
    document.addEventListener('keydown', handleKeyDown);
};

// const openPhotoPage = (url) => {
//     window.open(url, '_blank');
// };

// 关闭图片预览
const closePhotoPreview = () => {
    photoPreviewVisible.value = false;
    // 移除键盘事件监听
    document.removeEventListener('keydown', handleKeyDown);
};

// 处理键盘事件
const handleKeyDown = (event) => {
    if (!photoPreviewVisible.value) return;

    if (event.key === 'ArrowLeft') {
        prevPhoto();
    } else if (event.key === 'ArrowRight') {
        nextPhoto();
    } else if (event.key === 'Escape') {
        closePhotoPreview();
    }
};

// 上一张图片
const prevPhoto = () => {
    if (currentPhotoIndex.value > 0) {
        currentPhotoIndex.value--;
    }
};

// 下一张图片
const nextPhoto = () => {
    if (currentPhotoIndex.value < currentPhotos.value.length - 1) {
        currentPhotoIndex.value++;
    }
};

// 组件卸载前移除事件监听和清理observer
onBeforeUnmount(() => {
    document.removeEventListener('keydown', handleKeyDown);

    // 清理Intersection Observer
    if (placeObserver) {
        placeObserver.disconnect();
        placeObserver = null;
    }
});

// 初始化世界地图
const continentsCount = ref(0);
const countriesCount = ref(0);
const initWorldMap = async (visitedCountries) => {
    if (!worldMapContainer.value) return;

    // 加载世界地图数据
    await echarts.registerMap('world', await fetchWorldMapData());

    worldMap = echarts.init(worldMapContainer.value);

    // 计算点亮的大洲数量
    const visitedContinents = [...new Set(visitedCountries.map(country => getContinentForCountry(country)))];
    continentsCount.value = visitedContinents.filter(continent => continent !== 'Unknown').length;
    countriesCount.value = visitedCountries.length;

    // 统计信息文本
    // const statsText =
    //     `🌍 Footprint on ${countriesCount.value} Countries\n🗺️ Footprint on ${continentsCount.value} Continents`;
    const statsText =
        `📅 ${t("statisticsTime")} ${getDate(LANG)}`;

    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'item',
            formatter: '{b}'
        },
        // 添加统计信息图表组件
        graphic: [{
            type: 'text',
            right: 24,
            bottom: 20,
            style: {
                text: statsText,
                textAlign: 'left',
                fill: '#E0E0E0', // 柔白，避免死白
                fontSize: 14, // 更秀气一点
                fontWeight: 400, // 常规字体更优雅
                fontFamily: 'Inter, Roboto, sans-serif',
                lineHeight: 22,
                textShadow: '0 1px 2px rgba(0, 0, 0, 0.25)' // 更自然的阴影，减少突兀感
            }
        }],
        series: [{
            name: 'World Map',
            type: 'map',
            map: 'world',
            roam: true,
            itemStyle: {
                areaColor: new echarts.graphic.LinearGradient(
                    0, 0, 0, 1,
                    [
                        { offset: 0, color: '#ffffff' },
                        { offset: 1, color: '#f0f0f0' }
                    ]
                ),
                borderColor: '#C0C0C0'
            },
            emphasis: {
                label: {
                    show: true
                },
                itemStyle: {
                    areaColor: new echarts.graphic.LinearGradient(
                        0, 0, 0, 1,
                        [
                            { offset: 0, color: '#B875DB' },
                            { offset: 1, color: '#9A4DC0' }
                        ]
                    )
                }
            },
            data: [
                ...visitedCountries.map((country) => ({
                    name: country,
                    value: 1,
                    itemStyle: {
                        areaColor: new echarts.graphic.LinearGradient(
                            0, 0, 0, 1,
                            [
                                { offset: 0, color: '#D7A7F9' },
                                { offset: 1, color: '#B875DB' }
                            ]
                        )
                    }
                })),
            ]
        }]
    };
    worldMap.setOption(option);
    // 响应窗口大小变化
    window.addEventListener('resize', () => worldMap?.resize());
};

// 初始化中国地图
const citiesCount = ref(0);
const initChinaMap = async (visitedCities) => {
    if (!chinaMapContainer.value) return;

    // 加载中国地图数据
    await echarts.registerMap('china', await fetchChinaMapData());

    chinaMap = echarts.init(chinaMapContainer.value);

    // 计算点亮的城市数量
    citiesCount.value = visitedCities.length;

    // 统计信息文本
    // const statsText = `🏙️ Footprint on ${citiesCount.value} Cities`;
    const statsText =
        `📅 ${t("statisticsTime")} ${getDate(LANG)}`;

    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'item',
            formatter: '{b}'
        },
        // 添加统计信息图表组件
        graphic: [{
            type: 'text',
            right: 24,
            bottom: 20,
            style: {
                text: statsText,
                textAlign: 'left',
                fill: '#E0E0E0', // 柔白，避免死白
                fontSize: 14, // 更秀气一点
                fontWeight: 400, // 常规字体更优雅
                fontFamily: 'Inter, Roboto, sans-serif',
                lineHeight: 22,
                textShadow: '0 1px 2px rgba(0, 0, 0, 0.25)' // 更自然的阴影，减少突兀感
            }
        }],
        series: [{
            name: 'China Map',
            type: 'map',
            map: 'china',
            roam: true,
            zoom: 1.5, // 增加初始缩放比例
            center: [104, 36], // 设置地图中心点，向下移动几个像素

            itemStyle: {
                areaColor: new echarts.graphic.LinearGradient(
                    0, 0, 0, 1,
                    [
                        { offset: 0, color: '#ffffff' },
                        { offset: 1, color: '#f0f0f0' }
                    ]
                ),
                borderColor: '#C0C0C0'
            },
            emphasis: {
                label: {
                    show: true
                },
                itemStyle: {
                    areaColor: new echarts.graphic.LinearGradient(
                        0, 0, 0, 1,
                        [
                            { offset: 0, color: '#B875DB' },
                            { offset: 1, color: '#9A4DC0' }
                        ]
                    )
                }
            },
            data: [
                ...visitedCities.map((city) => ({
                    name: city,
                    value: 1,
                    itemStyle: {
                        areaColor: new echarts.graphic.LinearGradient(
                            0, 0, 0, 1,
                            [
                                { offset: 0, color: '#D7A7F9' },
                                { offset: 1, color: '#B875DB' }
                            ]
                        )
                    }
                })),
            ]
        }]
    };
    chinaMap.setOption(option);
    // 响应窗口大小变化
    window.addEventListener('resize', () => chinaMap?.resize());
};

// 获取世界地图数据
const fetchWorldMapData = async () => {
    try {
        // 不能用request.get()，会出现跨域问题
        const response = await fetch('https://charlie-assets.oss-rg-china-mainland.aliyuncs.com/json/world-map.json');
        return await response.json();
    } catch (error) {
        console.error('Failed to load world map data:', error);
        Message.error('加载世界地图数据失败');
        return {};
    }
};

// 获取中国地图数据
const fetchChinaMapData = async () => {
    try {
        // 不能用request.get()，会出现跨域问题
        const response = await fetch('https://charlie-assets.oss-rg-china-mainland.aliyuncs.com/json/china-map.json');
        return await response.json();
    } catch (error) {
        console.error('Failed to load China map data:', error);
        Message.error('加载中国地图数据失败');
        return {};
    }
};
</script>

<style scoped>
.main-content {
    padding: 2rem;
    max-width: 1500px;
    margin: 0 auto;
}

.section-title {
    margin-bottom: 2rem;
    text-align: center;
}

.section-title h2 {
    font-size: 2rem;
    color: #fff;
    margin: 0;
    padding: 0;
    position: relative;
    display: inline-block;
}

.section-title h2 .corner-count {
    font-size: 0.6em;
    font-weight: 400;
    font-style: italic;
    margin-left: 5px;
    vertical-align: middle;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #c084fc, #e9d5ff);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 0px 8px rgba(192, 132, 252, 0.5);
}

.section-title h2::after {
    content: '';
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 60px;
    height: 3px;
    background: linear-gradient(90deg, #8E2DE2, #4A00E0);
    border-radius: 3px;
}

.map-section {
    margin-bottom: 4rem;
}

.map-container {
    width: 100%;
    height: 600px;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
}

.china-map-container {
    height: 600px;
}

.places-grid {
    margin-top: -30px;
}

.place-card {
    height: 100%;
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 12px;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
    color: #fff;
    max-height: 283.59px;
    overflow: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
}

.place-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.2);
}

.place-header {
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.place-header h3 {
    margin: 0;
    font-size: 1.5rem;
    color: #fff;
}

.place-date {
    font-size: 0.9rem;
    color: #a78bfa;
}

.place-description {
    margin-bottom: 1rem;
    color: rgba(255, 255, 255, 0.8);
}

.place-photos {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 1rem;
}

.place-photo {
    width: 80px;
    height: 80px;
    border-radius: 8px;
    object-fit: cover;
    cursor: pointer;
    transition: transform 0.2s ease;
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

.place-photo:hover {
    transform: scale(1.05);
}



@media (max-width: 768px) {
    .map-container {
        height: 400px;
    }

    .place-header {
        flex-direction: column;
    }

    .place-date {
        margin-top: 0.5rem;
    }
}

/* 图片预览样式 */
.photo-preview-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

.photo-preview-image-container {
    width: 100%;
    height: 400px;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 20px;
    overflow: hidden;
    border-radius: 12px;
    cursor: pointer;
}

.preview-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    border-radius: 8px;
}

.photo-preview-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 20px;
    margin-top: 10px;
}

.preview-nav-button {
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: white;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    transition: all 0.3s ease;
}

.preview-nav-button:hover:not(:disabled) {
    background: rgba(255, 255, 255, 0.2);
    transform: scale(1.1);
}

.preview-nav-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.photo-preview-counter {
    font-size: 16px;
    color: rgba(255, 255, 255, 0.8);
    min-width: 60px;
    text-align: center;
}

@media (max-width: 768px) {
    .photo-preview-image-container {
        height: 300px;
    }
}
</style>