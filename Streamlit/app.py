import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
import fiona
import os

# 1. 页面配置
st.set_page_config(page_title="GIS 矢量数据云处理器", layout="wide")

st.title("🛰️ 矢量数据空间分析平台 (GeoJSON/KML)")
st.markdown("""
本工具展示了**服务器后端**对专业 GIS 格式的处理：
- **解析**：读取并转换 KML/GeoJSON。
- **分析**：执行坐标系转换 (CRS) 并计算缓冲区。
- **分发**：提供处理后的地理数据下载。
""")

# 开启 fiona 对 KML 的驱动支持
fiona.drvsupport.supported_drivers['KML'] = 'rw'

# 2. 侧边栏：参数
st.sidebar.header("分析参数")
dist_meters = st.sidebar.number_input("缓冲区距离 (米)", min_value=1, max_value=5000, value=500)
output_format = st.sidebar.selectbox("输出格式", ["GeoJSON", "KML"])

# 3. 文件上传
uploaded_file = st.file_uploader("上传 GeoJSON 或 KML 文件", type=['json', 'geojson', 'kml'])

if uploaded_file is not None:
    # 保存临时文件以便 geopandas 读取 (KML 必须通过文件路径读取)
    with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    try:
        # 4. 后端处理逻辑
        st.info("正在解析矢量图层...")
        
        # 读取数据 (自动识别驱动)
        gdf = gpd.read_file(uploaded_file.name)
        
        # 核心：为了以“米”为单位计算缓冲区，必须先投影到 Web Mercator (EPSG:3857)
        gdf_projected = gdf.to_crs(epsg=3857)
        gdf_buffer = gdf_projected.buffer(dist_meters)
        
        # 转回地理坐标系 (WGS84) 用于地图显示
        gdf_result = gpd.GeoDataFrame(gdf.copy(), geometry=gdf_buffer).to_crs(epsg=4326)
        gdf_original = gdf.to_crs(epsg=4326)

        # 5. 地图可视化
        st.subheader("空间分析预览")
        m = leafmap.Map(google_map="HYBRID")
        m.add_gdf(gdf_original, layer_name="原始数据", style={'color': 'blue', 'weight': 2})
        m.add_gdf(gdf_result, layer_name="分析结果", fill_colors=["yellow"], fill_opacity=0.4)
        m.zoom_to_gdf(gdf_original)
        m.to_streamlit(height=600)

        # 6. 导出与下载
        st.subheader("📥 结果下载")
        temp_output = f"result.{output_format.lower()}"
        
        if output_format == "GeoJSON":
            gdf_result.to_file(temp_output, driver='GeoJSON')
        else:
            gdf_result.to_file(temp_output, driver='KML')

        with open(temp_output, "rb") as f:
            st.download_button(
                label=f"导出为 {output_format}",
                data=f,
                file_name=temp_output,
                mime="application/octet-stream"
            )
            
        # 清理临时文件
        os.remove(uploaded_file.name)
        os.remove(temp_output)

    except Exception as e:
        st.error(f"处理失败: {e}")
        st.info("提示：如果是 KML 文件，请确保其包含有效的几何要素。")
else:
    st.warning("请上传一个包含空间要素的文件开始分析。")