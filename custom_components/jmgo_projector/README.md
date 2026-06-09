# JMGO 坚果投影仪 Home Assistant 集成

这是一个用于控制 JMGO 坚果投影仪的 Home Assistant 自定义组件。

## 功能特性

- ✅ 开关机控制
- ✅ 音量调节（0-100）
- ✅ 方向导航（上/下/左/右）
- ✅ 确认键（OK）
- ✅ 返回键
- ✅ 设置键
- ✅ 菜单键
- ✅ 选项键

## 安装方法

### 方法一：HACS 安装（推荐）

1. 打开 HACS -> 集成
2. 点击右上角 "..." -> "自定义存储库"
3. 添加此存储库的 URL，类别选择 "集成"
4. 搜索 "JMGO Projector" 并安装

### 方法二：手动安装

1. 将 `custom_components/jmgo_projector` 文件夹复制到你的 Home Assistant 配置目录下的 `custom_components/` 中
2. 重启 Home Assistant

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

## 配置方法

### 方法一：UI 配置（推荐）

1. 进入 Home Assistant -> 配置 -> 设备与服务
2. 点击右下角 "添加集成"
3. 搜索 "JMGO Projector"
4. 输入投影仪的 IP 地址（可在投影仪设置 -> 网络信息中查看）
5. 端口默认为 9005，一般不需要修改
6. 点击提交

### 方法二：YAML 配置

在 `configuration.yaml` 中添加：

```yaml
media_player:
  - platform: jmgo_projector
    host: 192.168.1.100  # 替换为你的投影仪 IP
    port: 9005           # 默认端口
    name: 客厅投影仪     # 自定义名称
```

## 使用方法

### 基础控制

集成后会自动创建一个 `media_player` 实体，支持：

- **开机/关机**：使用 Home Assistant 的标准开关控制
- **音量调节**：
  - 使用 UI 的音量滑块
  - 调用 `media_player.volume_set` 服务
  - 调用 `media_player.volume_up` / `media_player.volume_down` 服务

### 遥控器按键控制

通过自定义服务 `jmgo_projector.send_key` 可以模拟遥控器按键：

#### 可用按键

- `power` - 电源
- `ok` - 确认
- `return` - 返回
- `up` - 上
- `down` - 下
- `left` - 左
- `right` - 右
- `setting` - 设置
- `mongo` - 菜单
- `option` - 选项

#### 服务调用示例

**自动化中使用：**

```yaml
automation:
  - alias: "投影仪确认键"
    trigger:
      platform: state
      entity_id: binary_sensor.remote_button
      to: "on"
    action:
      service: jmgo_projector.send_key
      target:
        entity_id: media_player.ke_ting_tou_ying_yi
      data:
        key: ok
```

**脚本中使用：**

```yaml
script:
  projector_menu:
    alias: "打开投影仪菜单"
    sequence:
      - service: jmgo_projector.send_key
        target:
          entity_id: media_player.ke_ting_tou_ying_yi
        data:
          key: mongo
```

**通过开发者工具测试：**

1. 进入 开发者工具 -> 服务
2. 选择服务：`jmgo_projector.send_key`
3. 选择实体
4. 输入按键名称（如 `ok`、`up` 等）

### 常用自动化示例

#### 1. 语音控制开关机

```yaml
automation:
  - alias: "语音开启投影仪"
    trigger:
      platform: event
      event_type: assist_intent
      event_data:
        intent:
          name: HassTurnOn
        slots:
          name: 客厅投影仪
    action:
      service: media_player.turn_on
      target:
        entity_id: media_player.ke_ting_tou_ying_yi

  - alias: "语音关闭投影仪"
    trigger:
      platform: event
      event_type: assist_intent
      event_data:
        intent:
          name: HassTurnOff
        slots:
          name: 客厅投影仪
    action:
      service: media_player.turn_off
      target:
        entity_id: media_player.ke_ting_tou_ying_yi
```

#### 2. 定时关机

```yaml
automation:
  - alias: "晚上11点自动关机"
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
```

#### 3. 音量调节按钮

```yaml
script:
  projector_volume_up:
    alias: "投影仪音量+"
    sequence:
      - service: media_player.volume_up
        target:
          entity_id: media_player.ke_ting_tou_ying_yi
  
  projector_volume_down:
    alias: "投影仪音量-"
    sequence:
      - service: media_player.volume_down
        target:
          entity_id: media_player.ke_ting_tou_ying_yi
```

#### 4. 模拟遥控器方向键

```yaml
script:
  projector_navigate:
    alias: "投影仪导航"
    fields:
      direction:
        name: 方向
        selector:
          select:
            options: [up, down, left, right, ok, return]
    sequence:
      - service: jmgo_projector.send_key
        target:
          entity_id: media_player.ke_ting_tou_ying_yi
        data:
          key: "{{ direction }}"
```

## 故障排除

### 无法连接投影仪

1. 确认投影仪已开机且连接到网络
2. 检查投影仪的 IP 地址是否正确（在投影仪设置 -> 网络信息中查看）
3. 确认 Home Assistant 和投影仪在同一局域网内
4. 尝试 ping 投影仪的 IP 地址
5. 检查是否有防火墙阻止 9005 端口

### 命令无响应

1. 某些投影仪型号可能不完全支持所有命令
2. 尝试重启投影仪和 Home Assistant
3. 检查投影仪固件版本

## 技术说明

- 通信协议：TCP Socket
- 默认端口：9005
- 数据包格式：二进制协议（基于 protobuf）
- 数据来源：通过抓包 JMGO 坚果控 App 与 JMGO-N1S Ultra 投影仪的通信获得

## 支持的设备

目前已测试设备：
- JMGO N1S Ultra-0087

其他 JMGO 设备可能需要调整命令，欢迎提交 PR 或 Issue。

## 许可证

MIT License

## 致谢

感谢原始项目的逆向工程工作。
