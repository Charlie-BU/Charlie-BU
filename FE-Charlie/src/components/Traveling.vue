<template>
    <el-main class="main-content">
        <section class="map-section">
            <div class="section-title">
                <h2>{{ t('worldMap') }}</h2>
            </div>
            <div class="map-container" ref="worldMapContainer"></div>
        </section>

        <section class="map-section">
            <div class="section-title">
                <h2>{{ t('chinaMap') }}</h2>
            </div>
            <div class="map-container china-map-container" ref="chinaMapContainer"></div>
        </section>

        <section class="places-section">
            <div class="section-title">
                <h2>{{ t('placesVisited') }}</h2>
            </div>
            <el-row :gutter="24" class="places-grid">
                <el-col :xs="24" :sm="12" :md="8" v-for="(place, index) in places" :key="index"
                    style="margin-top: 50px;">
                    <el-card class="place-card" shadow="hover" @click.stop="showPlaceDetails(place)">
                        <div class="place-header">
                            <h3>{{ place.city }}</h3>
                            <div class="place-date">{{ formatDateRange(place.dateStart, place.dateEnd) }}</div>
                        </div>
                        <p class="place-description">{{ place.description }}</p>
                        <div class="place-photos" v-if="place.photos && place.photos.length > 0">
                            <el-image v-for="(photo, photoIndex) in place.photos" :key="photoIndex" :src="photo.url"
                                fit="cover" class="place-photo"
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
                <div class="photo-preview-image-container"
                    @click="openPhotoPage(currentPhotos[currentPhotoIndex]?.url)">
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
import { ref, onMounted, computed, onBeforeUnmount } from 'vue';
import Modal from './Modal.vue';
import * as echarts from 'echarts';
import { ElMessage } from 'element-plus';

import { request } from '../api/request';
import { getContinentForCountry } from '../utils/map';

onMounted(async () => {
    await fetchTravelData();
});

// 语言设置
const LANG = localStorage.getItem("LANG") || "Chinese";

const t = (key) => {
    const translations = {
        worldMap: {
            Chinese: "🌍 全球",
            English: "🌍 World"
        },
        chinaMap: {
            Chinese: "🇨🇳 中国",
            English: "🇨🇳 China"
        },
        placesVisited: {
            Chinese: "✨ 点亮的角落",
            English: "✨ Corners Been Lighted"
        },
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
        // 获取每个地点的照片
        await Promise.all(places.value.map(async (place) => {
            try {
                const photoResponse = await request.post(`/api/travel/getTravelPhotos`, {
                    travelId: place.id,
                });
                place.photos = photoResponse.data.photos || [];
            } catch (err) {
                console.error(`Failed to fetch photos for place ${place.id}:`, err);
            }
        }));

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
        ElMessage.error('获取旅行数据失败');
    }
};

// 地图容器引用
const worldMapContainer = ref(null);
const chinaMapContainer = ref(null);

// 地图实例
let worldMap = null;
let chinaMap = null;

// 地点数据
const places = ref([]);



// 格式化日期范围
const formatDateRange = (start, end) => {
    if (!start) return '';

    const startDate = new Date(start);
    const startStr = startDate.toLocaleDateString(LANG === 'English' ? 'en-US' : 'zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });

    if (!end || start === end) return startStr;

    const endDate = new Date(end);
    const endStr = endDate.toLocaleDateString(LANG === 'English' ? 'en-US' : 'zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });

    return `${startStr} - ${endStr}`;
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

const openPhotoPage = (url) => {
    window.open(url, '_blank');
};

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

// 组件卸载前移除事件监听
onBeforeUnmount(() => {
    document.removeEventListener('keydown', handleKeyDown);
});

// 初始化世界地图
const initWorldMap = async (visitedCountries) => {
    if (!worldMapContainer.value) return;

    // 加载世界地图数据
    await echarts.registerMap('world', await fetchWorldMapData());

    worldMap = echarts.init(worldMapContainer.value);

    // 计算点亮的大洲数量
    const visitedContinents = [...new Set(visitedCountries.map(country => getContinentForCountry(country)))];
    const continentsCount = visitedContinents.filter(continent => continent !== 'Unknown').length;
    const countriesCount = visitedCountries.length;

    // 统计信息文本
    const statsText =
        `🌍 Countries Visited: ${countriesCount}\n🗺️ Continents Visited: ${continentsCount}`;

    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'item',
            formatter: '{b}'
        },
        // 添加统计信息图表组件
        graphic: [{
            type: 'text',
            right: 20,
            bottom: 20,
            style: {
                text: statsText,
                textAlign: 'right',
                fill: '#ffd700',
                fontSize: 17,
                fontWeight: 'bold',
                fontStyle: 'italic',
                fontFamily: "Times New Roman",
                lineHeight: 25,
                textShadow: '0 0 3px rgba(0,0,0,0.5)'
            }
        }],
        series: [{
            name: 'World Map',
            type: 'map',
            map: 'world',
            roam: true,
            itemStyle: {
                areaColor: '#ffffff',
                borderColor: '#404040'
            },
            emphasis: {
                label: {
                    show: true
                },
                itemStyle: {
                    areaColor: '#ffd700'
                }
            },
            data: [
                ...visitedCountries.map((country) => ({
                    name: country,
                    value: 1,
                    itemStyle: {
                        areaColor: '#ffd700'
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
const initChinaMap = async (visitedCities) => {
    if (!chinaMapContainer.value) return;

    // 加载中国地图数据
    await echarts.registerMap('china', await fetchChinaMapData());

    chinaMap = echarts.init(chinaMapContainer.value);

    // 计算点亮的城市数量
    const citiesCount = visitedCities.length;

    // 统计信息文本
    const statsText = `🏙️ Cities Visited: ${citiesCount}`;

    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'item',
            formatter: '{b}'
        },
        // 添加统计信息图表组件
        graphic: [{
            type: 'text',
            right: 20,
            bottom: 20,
            style: {
                text: statsText,
                textAlign: 'right',
                fill: '#ffd700',
                fontSize: 17,
                fontWeight: 'bold',
                fontStyle: 'italic',
                fontFamily: "Times New Roman",
                textShadow: '0 0 3px rgba(0,0,0,0.5)'
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
                areaColor: '#ffffff',
                borderColor: '#404040'
            },
            emphasis: {
                label: {
                    show: true
                },
                itemStyle: {
                    areaColor: '#ffd700'
                }
            },
            data: [
                ...visitedCities.map((city) => ({
                    name: city,
                    value: 1,
                    itemStyle: {
                        areaColor: '#ffd700'
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
        ElMessage.error('加载世界地图数据失败');
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
        ElMessage.error('加载中国地图数据失败');
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
    padding: 0 20px;
}

.place-photo {
    width: 80px;
    height: 80px;
    border-radius: 8px;
    object-fit: cover;
    cursor: pointer;
    transition: transform 0.2s ease;
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