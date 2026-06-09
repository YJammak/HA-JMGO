# JMGO 坚果投影仪 Home Assistant 集成

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![HA_version](https://img.shields.io/badge/Home_Assistant-2024.1.0+-blue)

通过 Home Assistant 控制 JMGO 坚果投影仪，支持开关机、音量调节、遥控器按键等所有功能。

![JMGO Logo](https://img.shields.io/badge/JMGO-坚果投影-red)

## ✨ 功能特性

- 🎬 **开关机控制** - 通过 media_player 实体控制
- 🔊 **音量调节** - 支持 0-100 精确音量控制
- 🎮 **遥控器按键** - 上/下/左/右、确认、返回、设置、菜单等
- 📱 **UI 配置** - 支持通过 Home Assistant UI 添加和修改配置
- 🌐 **在线修改** - 可随时修改 IP 地址、端口和名称
- 🇨🇳 **中文支持** - 完整的中文界面和文档

## 📦 安装

### 方法一：通过 HACS 安装（推荐）

1. 确保已安装 [HACS](https://hacs.xyz/)
2. 进入 HACS -> 集成
3. 点击右上角 "⋮" -> "自定义存储库"
4. 添加此存储库 URL，类别选择 "集成"
5. 搜索 "JMGO Projector" 并安装
6. 重启 Home Assistant

### 方法二：手动安装

1. 下载或克隆此仓库
2. 将 `custom_components/jmgo_projector` 文件夹复制到你的 Home Assistant 配置目录：
   ```
   你的配置目录/
   ├── configuration.yaml
   └── custom_components/
       └── jmgo_projector/
           ├── __init__.py
           ├── manifest.json
           ├── config_flow.py
           ├── media_player.py
           ├── const.py
           ├── services.yaml
           ├── strings.json
           └── translations/
               └── zh-Hans.json
   ```
3. 重启 Home Assistant

## 🚀 配置

### UI 配置（推荐）

1. 进入 **配置** -> **设备与服务**
2. 点击 **+ 添加集成**
3. 搜索 **"JMGO Projector"**
4. 输入投影仪的 IP 地址（在投影仪 设置 -> 网络信息 中查看）
5. 端口默认 `9005`，一般无需修改
6. 自定义设备名称（可选）

### YAML 配置

```yaml
media_player:
  - platform: jmgo_projector
    host: 192.168.1.100  # 替换为你的投影仪 IP
    port: 9005
    name: 客厅投影仪
```

## 🎮 使用方法

### 基础控制

集成后会创建 `media_player` 实体，支持：

- **开关机**：使用标准的 turn_on/turn_off 服务
- **音量**：volume_set、volume_up、volume_down 服务

### 遥控器按键

通过自定义服务 `jmgo_projector.send_key` 模拟遥控器：

```yaml
# 按确认键
service: jmgo_projector.send_key
target:
  entity_id: media_player.ke_ting_tou_ying_yi
data:
  key: ok

# 可用按键：
# power, ok, return, up, down, left, right, setting, mongo, option
```

### 自动化示例

```yaml
automation:
  # 定时关机
  - alias: "晚上11点自动关投影仪"
    trigger:
      platform: time
      at: "23:00:00"
    condition:
      condition: state
      entity_id: media_player.ke_ting_tou_ying_yi
      state: "on"
    action:
      service: media_player.turn_off
      target:
        entity_id: media_player.ke_ting_tou_ying_yi

  # 开机后设置音量
  - alias: "投影仪开机音量设置"
    trigger:
      platform: state
      entity_id: media_player.ke_ting_tou_ying_yi
      to: "on"
    action:
      service: media_player.volume_set
      target:
        entity_id: media_player.ke_ting_tou_ying_yi
      data:
        volume_level: 0.3  # 30%
```

## ⚙️ 修改配置

可以在运行时修改 IP 地址、端口和名称：

1. 进入 **配置** -> **设备与服务** -> **JMGO Projector**
2. 点击设备卡片右上角 **⋮** -> **选项**
3. 修改配置，系统会自动验证连接
4. 验证通过后自动应用

## 📋 支持的设备

已测试设备：
- JMGO N1S Ultra-0087

其他 JMGO 设备可能需要调整命令，欢迎提交 Issue 或 PR。

## 🔧 故障排除

### 无法连接投影仪

1. 确认投影仪已开机且连接到网络
2. 检查 IP 地址是否正确（投影仪 设置 -> 网络信息）
3. 确认 HA 和投影仪在同一局域网
4. 尝试 `ping 192.168.1.100`（替换为投影仪 IP）
5. 检查是否有防火墙阻止 9005 端口

### 命令无响应

1. 某些 JMGO 型号可能不完全支持所有命令
2. 重启投影仪和 Home Assistant
3. 检查投影仪固件版本

## 🛠️ 技术说明

- **通信协议**：TCP Socket
- **默认端口**：9005
- **数据格式**：二进制协议（基于 protobuf）
- **数据来源**：通过抓包 JMGO 坚果控 App 与投影仪通信获得
- **最低 HA 版本**：2024.1.0

## 📝 更新日志

### v1.0.0 (2026-06-09)
- ✅ 初始版本发布
- ✅ 支持开关机控制
- ✅ 支持音量调节（0-100）
- ✅ 支持所有遥控器按键
- ✅ UI 配置流程
- ✅ 在线修改配置
- ✅ YAML 配置支持
- ✅ 中文翻译

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

本项目基于 [XvZipo/JMGO-projector-controller](https://github.com/XvZipo/JMGO-projector-controller) 改造而成，感谢原作者的逆向工程工作。

---

**如果这个集成对你有帮助，请给个 ⭐️ Star！**
