import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

# -----------------------------------------------------------------------------
# 典型用途：机器学习快速原型 (ML Prototyping)
# 核心特色：Script-to-App 模式，无需懂前端即可快速将 Python 脚本转化为交互式应用
# -----------------------------------------------------------------------------

st.set_page_config(page_title="ML 模型演练场", page_icon="🤖", layout="wide")

st.title("🤖 机器学习模型演练场")
st.markdown("""
> **Streamlit 特色展示**：
> 这是一个典型的 ML 原型应用。通过侧边栏调整超参数，实时触发模型训练并可视化结果。
> 这种"所见即所得"的开发模式是 Streamlit 最大的优势。
""")

# 1. 数据加载
with st.sidebar:
    st.header("1. 模型配置")
    st.info("使用经典的 Iris 鸢尾花数据集")
    
    n_estimators = st.slider("决策树数量 (n_estimators)", 10, 200, 100, 10)
    max_depth = st.slider("最大深度 (max_depth)", 1, 20, 5)
    criterion = st.selectbox("分裂标准", ["gini", "entropy"])

# 加载数据
@st.cache_data
def load_data():
    df = sns.load_dataset('iris')
    return df

df = load_data()

# 2. 页面布局 - 数据概览
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("原始数据")
    st.dataframe(df.head(10), use_container_width=True)
    st.caption(f"总样本数: {len(df)}")

with col2:
    st.subheader("特征分布")
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.scatterplot(data=df, x='sepal_length', y='sepal_width', hue='species', ax=ax)
    st.pyplot(fig)

# 3. 模型训练
st.divider()
st.subheader("2. 模型训练与评估")

# 准备数据
X = df.drop('species', axis=1)
y = df['species']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 训练
clf = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, criterion=criterion)
clf.fit(X_train, y_train)
y_pred = clf.predict(X_test)

# 指标
acc = accuracy_score(y_test, y_pred)

# 显示指标卡片
m1, m2, m3 = st.columns(3)
m1.metric("模型准确率 (Accuracy)", f"{acc:.2%}", delta=f"{acc-0.9:.2%}")
m2.metric("训练样本数", len(X_train))
m3.metric("测试样本数", len(X_test))

# 4. 结果可视化
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 混淆矩阵")
    cm = confusion_matrix(y_test, y_pred)
    fig_cm, ax_cm = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax_cm)
    st.pyplot(fig_cm)

with c2:
    st.markdown("#### 特征重要性")
    feat_importances = pd.Series(clf.feature_importances_, index=X.columns)
    st.bar_chart(feat_importances)

st.success("✅ 模型训练完成！尝试调整侧边栏参数来优化模型。")
