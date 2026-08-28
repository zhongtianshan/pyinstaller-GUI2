# Cyber PyInstaller Pro

基于 PySide6 的 PyInstaller 图形化打包工具。把 PyInstaller 的命令行参数全部可视化，勾勾选选、填个脚本路径，就能把 Python 脚本打包成 exe。

## 功能特性

- **图形化配置 PyInstaller 全部常用选项**：单文件（--onefile）、无控制台（--noconsole）、UPX 压缩、调试模式
- **一键生成 Windows 版本信息**：公司、产品、版本号、描述、版权（自动写 version file，无需手改 .spec）
- **资源管理**：附加数据、附加二进制、隐藏导入、钩子目录
- **可选字节码加密**：自定义密钥（留空则不加密）
- **实时打包日志**：后台线程执行，界面不卡死，实时显示输出
- **配置保存 / 加载**：上次的设置自动恢复，支持保存多份配置
- **一键生成命令**：可以先"生成命令"看一眼将要执行的完整命令行

## 界面预览

（待补充截图）

## 安装

需要 Python 3.9 及以上。

```bash
pip install -r requirements.txt
```

> 提示：勾选"加密字节码"需要 `pycryptodome`，requirements.txt 已包含。

## 运行

```bash
python "Pyinstall GUI.py"
```

## 使用

1. 在 **基本** 页选择要打包的主脚本，输出目录默认是运行目录下的 `output\`
2. 在 **打包** 页按需勾选选项、填版本信息（公司名等）
3. 在 **资源 / 安全 / 高级** 页按需添加数据、二进制、隐藏导入、加密等
4. 点 **开始打包**，下方日志区实时显示进度
5. 完成后 exe 在 `output\` 目录下

想先看命令行效果，可先点 **生成命令**。

## 目录结构

```
Pyinstall GUI.py    主程序
requirements.txt    依赖清单
temp_build\         打包临时目录（自动清理）
output\             打包产物输出目录
```

## License

[MIT](LICENSE)

Copyright (c) 2025 zhongtianshan
