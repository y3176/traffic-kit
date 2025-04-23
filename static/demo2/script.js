let pyodide;

async function initializePyodide() {
    // 初始化 Pyodide
    pyodide = await loadPyodide({
        indexURL: "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/"
    });
    
    // 加载常用包
    await pyodide.loadPackage(["micropip", "numpy"]);
    await pyodide.runPythonAsync(`
        import micropip
        await micropip.install('matplotlib')
    `);
        
    document.getElementById("output").innerHTML = "Pyodide 初始化完成！可以开始运行代码了。";
}

// 初始化 Pyodide
initializePyodide();

// 运行代码
document.getElementById("runCode").addEventListener("click", async () => {
    const code = document.getElementById("code-input").value;
    if (!code.trim()) {
        document.getElementById("output").innerHTML = "请输入Python代码";
        return;
    }
    
    try {
        const output = await pyodide.runPython(code);
        if (output !== undefined) {
            document.getElementById("output").innerHTML = output;
        } else {
            document.getElementById("output").innerHTML = "代码执行成功（无返回值）";
        }
    } catch (error) {
        document.getElementById("output").innerHTML = `错误: ${error}`;
    }
});

// 清空代码
document.getElementById("clearCode").addEventListener("click", () => {
    document.getElementById("code-input").value = "";
    document.getElementById("output").innerHTML = "";
});

// 示例代码
const examples = {
    "print": `# 简单打印示例
print("Hello, Pyodide!")
for i in range(5):
    print(f"计数: {i}")`,
    
    "math": `# 数学计算示例
import math

def circle_area(radius):
    return math.pi * radius ** 2

radius = 3
area = circle_area(radius)
print(f"半径为 {radius} 的圆面积是: {area:.2f}")`,
    
    "numpy": `# NumPy 数组操作示例
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
print("原始数组:", arr)
print("平均值:", np.mean(arr))
print("标准差:", np.std(arr))
print("平方:", arr ** 2)`
};

// 加载示例代码
document.querySelectorAll(".example-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        const exampleType = btn.getAttribute("data-example");
        document.getElementById("code-input").value = examples[exampleType];
    });
});
