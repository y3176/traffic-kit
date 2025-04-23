import plotly.express as px
import pandas as pd

# 1. 准备数据（示例：汽车数据集）
data = {
    "品牌": ["丰田", "本田", "奔驰", "宝马", "特斯拉"],
    "价格(万)": [25, 28, 45, 50, 35],
    "销量(辆)": [1200, 1500, 800, 600, 2000],
    "类型": ["燃油车", "燃油车", "燃油车", "燃油车", "电动车"]
}
df = pd.DataFrame(data)

# 2. 创建交互式散点图（带颜色和大小维度）
fig = px.scatter(
    df,
    x="价格(万)",
    y="销量(辆)",
    color="类型",
    size="销量(辆)",
    hover_name="品牌",
    title="汽车品牌价格-销量关系（气泡大小代表销量）",
    labels={"价格(万)": "价格（万元人民币）", "销量(辆)": "年销量（辆）"},
    template="plotly_white"
)

# 3. 自定义布局
fig.update_layout(
    font_family="SimHei",  # 中文字体支持
    hoverlabel=dict(bgcolor="white", font_size=12),
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)

# 4. 显示图表（在Jupyter/IDE中）
# fig.show()

# 5. 导出为静态HTML文件
fig.write_html("static/demo1/car_sales_visualization.html", 
               include_plotlyjs='cdn',  # 使用CDN减小文件体积
               full_html=True)  # 生成完整HTML文档

import logging
import base.logs
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.responses import FileResponse 
from fastapi.staticfiles import StaticFiles 


app = FastAPI()
@app.get("/", response_class=FileResponse)
async def read_index():
    return FileResponse("static/demo1/car_sales_visualization.html")

app.mount("/", StaticFiles(directory="static/demo1/"), name="static")

if __name__ == "__main__":  
    host="0.0.0.0"
    port=8009
    import webbrowser
    webbrowser.open(f"http://127.0.0.1:{port}/car_sales_visualization.html")
    import uvicorn 
    uvicorn.run(app, host=host, port=port)