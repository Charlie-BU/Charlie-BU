// 获取大洲信息
const continentMap = {
    // 亚洲国家
    China: "Asia",
    Japan: "Asia",
    "South Korea": "Asia",
    Thailand: "Asia",
    Singapore: "Asia",
    Malaysia: "Asia",
    Indonesia: "Asia",
    Vietnam: "Asia",
    Cambodia: "Asia",
    India: "Asia",
    // 欧洲国家
    "United Kingdom": "Europe",
    France: "Europe",
    Germany: "Europe",
    Italy: "Europe",
    Spain: "Europe",
    Netherlands: "Europe",
    Belgium: "Europe",
    Switzerland: "Europe",
    Austria: "Europe",
    Greece: "Europe",
    // 北美洲国家
    "United States": "North America",
    Canada: "North America",
    Mexico: "North America",
    // 南美洲国家
    Brazil: "South America",
    Argentina: "South America",
    Chile: "South America",
    // 大洋洲国家
    Australia: "Oceania",
    "New Zealand": "Oceania",
    // 非洲国家
    "South Africa": "Africa",
    Egypt: "Africa",
    Morocco: "Africa",
};

export const getContinentForCountry = (country: string): string => {
    return continentMap[country as keyof typeof continentMap] || "Unknown";
};
