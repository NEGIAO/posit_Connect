import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import classification_report
import os
import time

# 设置页面配置
st.set_page_config(page_title="随机森林分类 (Random Forest)", page_icon="🌲", layout="wide")

st.title("🌲 随机森林分类与网格搜索")
st.markdown("基于 Sentinel-2 数据和 NDVI 的分类模型训练与评估")

st.info("""
**💡 提示 / Note**
本演示运行在云端服务器 (2 vCPU, 4GB RAM)。
经测试，**全参数网格搜索**大约需要 **5 分钟** 即可完成，且结果与本地计算一致。
您可以放心运行完整流程，或直接查看下方“3. 运行结果”章节中的静态展示。
""")

# 1. 加载数据
st.sidebar.header("1. 数据配置")
uploaded_file = st.sidebar.file_uploader("上传 CSV 文件", type=["csv"])

# 尝试加载本地默认文件
default_path = 'Data/nanyang_samples.csv'
df = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("已加载上传的文件")
elif os.path.exists(default_path):
    df = pd.read_csv(default_path)
    st.sidebar.info(f"已加载默认文件: {default_path}")
else:
    st.warning(f"请上传 CSV 文件或确保项目目录下存在 '{default_path}'。")
    st.stop()

if df is not None:
    with st.expander("数据预览", expanded=True):
        st.dataframe(df.head())

    # 2. 特征列表
    all_columns = df.columns.tolist()
    
    # 默认特征
    default_bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B11', 'B12', 'NDVI']
    # 检查默认特征是否都在列中
    valid_default_bands = [b for b in default_bands if b in all_columns]
    
    st.sidebar.header("2. 特征与标签选择")
    bands = st.sidebar.multiselect("选择特征 (Bands)", all_columns, default=valid_default_bands)
    
    # 默认标签
    default_label = 'class' if 'class' in all_columns else (all_columns[-1] if all_columns else None)
    
    if default_label:
        label_index = all_columns.index(default_label)
    else:
        label_index = 0
        
    label = st.sidebar.selectbox("选择标签 (Label)", all_columns, index=label_index)

    if not bands:
        st.error("请至少选择一个特征。")
        st.stop()

    # 数据预处理：删除采样中产生的空值
    df_clean = df.dropna(subset=bands + [label])
    X = df_clean[bands]
    y = df_clean[label]
    
    st.sidebar.markdown(f"**有效样本数:** {len(df_clean)}")

    # 3. 划分数据集
    test_size = st.sidebar.slider("测试集比例", 0.1, 0.5, 0.3, 0.05)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    # 4. 针对 10 个特征调整搜索网格
    st.sidebar.header("3. 网格搜索参数")
    
    # 为了在 multiselect 中显示 None，我们需要处理一下
    # n_estimators
    n_estimators_opts = st.sidebar.multiselect("n_estimators", [100, 200, 300, 500], default=[100, 200, 300, 500])
    if not n_estimators_opts: n_estimators_opts = [100]
    
    # max_depth
    # 使用字符串 'None' 来代表 None，然后在参数构建时转换回去
    max_depth_options = ['None', 15, 25, 40]
    max_depth_sel = st.sidebar.multiselect("max_depth", max_depth_options, default=['None', 15, 25, 40])
    max_depth_opts = [None if x == 'None' else x for x in max_depth_sel]
    if not max_depth_opts: max_depth_opts = [None]

    # min_samples_split
    min_samples_split_opts = st.sidebar.multiselect("min_samples_split", [2, 5, 10], default=[2, 5, 10])
    if not min_samples_split_opts: min_samples_split_opts = [2]

    # max_features
    max_features_options = ['sqrt', 'log2', 'None']
    max_features_sel = st.sidebar.multiselect("max_features", max_features_options, default=['sqrt', 'log2', 'None'])
    max_features_opts = [None if x == 'None' else x for x in max_features_sel]
    if not max_features_opts: max_features_opts = ['sqrt']

    param_grid = {
        'n_estimators': n_estimators_opts,
        'max_depth': max_depth_opts,
        'min_samples_split': min_samples_split_opts,
        'max_features': max_features_opts
    }
    
    # 计算总拟合次数
    total_combinations = len(n_estimators_opts) * len(max_depth_opts) * len(min_samples_split_opts) * len(max_features_opts)
    total_fits = total_combinations * 5
    
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 当前配置:\n- 参数组合数: {total_combinations}\n- 总拟合次数 (CV=5): {total_fits}")
    
    if total_fits > 50:
        st.sidebar.warning("⚠️ 训练次数较多 (>50)，在低配置服务器上可能需要数分钟，建议减少参数范围。")

    if st.button("开始训练 (Grid Search)", type="primary"):
        start_time = time.time()
        with st.spinner(f'正在执行网格搜索 (共 {total_fits} 次拟合)，请稍候...'):
            # 5. 执行网格搜索
            rf = RandomForestClassifier(random_state=42, n_jobs=-1)
            grid_search = GridSearchCV(rf, param_grid, cv=5, scoring='accuracy', verbose=1)
            grid_search.fit(X_train, y_train)
        
        end_time = time.time()
        elapsed_time = end_time - start_time

        # 6. 结果展示
        st.success(f"✅ 训练完成！总耗时: {elapsed_time:.2f} 秒")
            
            st.subheader("最佳参数与精度")
            col1, col2 = st.columns(2)
            with col1:
                st.write("最佳参数:")
                st.json(grid_search.best_params_)
            with col2:
                st.metric("交叉验证最高精度 (OA)", f"{grid_search.best_score_:.4f}")

            # 7. 测试集评估
            best_rf = grid_search.best_estimator_
            y_pred = best_rf.predict(X_test)
            
            st.subheader("测试集分类报告")
            report_dict = classification_report(y_test, y_pred, output_dict=True)
            st.dataframe(pd.DataFrame(report_dict).transpose().style.format("{:.4f}"))

            # 8. 特征重要性排序图
            st.subheader("特征重要性")
            importances = best_rf.feature_importances_
            indices = np.argsort(importances)[::-1]

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.set_title("Feature Importances (Sentinel-2 + NDVI)")
            sns.barplot(x=[bands[i] for i in indices], y=importances[indices], palette="magma", ax=ax)
            ax.set_ylabel("Importance Score")
            ax.set_xlabel("Bands")
            
            # 自动调整布局
            plt.tight_layout()
            
            st.pyplot(fig)
