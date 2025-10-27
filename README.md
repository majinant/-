# 柏林噪声生成器

## 功能特点

- 可调整噪声的比例（Scale）
- 可调整八度（Octaves）数量
- 可调整持久性（Persistence）
- 可调整稀疏度（Lacunarity）
- 可重置所有参数到默认值
- 可生成新的随机种子

## 安装依赖

运行以下命令安装所需的Python库：

```bash
pip install numpy matplotlib
```

## 使用方法

1. 确保已安装所有依赖项
2. 运行主程序：

```bash
python perlin_noise_generator.py
```

3. 使用界面上的滑块调整参数：
   - **Scale**: 控制噪声的比例大小，值越大图案越粗糙
   - **Octaves**: 控制噪声的八度数量，值越大细节越多
   - **Persistence**: 控制每个八度的振幅衰减
   - **Lacunarity**: 控制每个八度的频率增长

4. 按钮功能：
   - **Reset**: 重置所有参数到默认值
   - **New Seed**: 生成新的随机种子，创建不同的噪声图案