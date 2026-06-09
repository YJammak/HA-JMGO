# JMGO Projector - HACS 信息

## 关于此集成

JMGO 坚果投影仪 Home Assistant 集成，支持通过 Home Assistant 控制投影仪的所有功能。

## 功能

- 开关机控制
- 音量调节（0-100）
- 遥控器按键（上/下/左/右/确认/返回/设置/菜单等）
- UI 配置和在线修改
- 完整中文支持

## 安装后

1. 重启 Home Assistant
2. 进入 配置 -> 设备与服务 -> 添加集成
3. 搜索 "JMGO Projector"
4. 输入投影仪 IP 地址（端口默认 9005）

## 使用方法

### 基础控制
```yaml
service: media_player.turn_on
target:
  entity_id: media_player.jmgo_projector
```

### 遥控器按键
```yaml
service: jmgo_projector.send_key
target:
  entity_id: media_player.jmgo_projector
data:
  key: ok
```

## 文档

详细文档请查看 [README.md](README.md)

## 支持

如有问题，请提交 [Issue](https://github.com/your-username/jmgo-projector/issues)
