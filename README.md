#  自行车违停检测系统

基于边缘计算平台 RDK X5 和 YOLOv8 实现的智能违停检测系统，支持多路视频接入、实时推理、数据可视化和自动告警。系统分为前端可视化、后端服务、模型部署和设备端推理四大模块，具备良好的可扩展性和实用性。

---

##  项目结构

```bash
.
├── software/
│   ├── lihua_springboot/     # 后端服务（Spring Boot）：处理业务逻辑与数据接口
│   └── lihua_vue/            # 前端页面（Vue3）：展示违停记录与设备状态
│
├── model/                    # 模型部署：YOLOv8 模型文件及推理脚本
│
├── rdk/                      # 开发板端代码：运行于 RDK X5，基于 Flask 的边缘推理服务

##  技术栈与平台

前端：Vue3 + TypeScript + Ant Design Vue  
  实现数据展示、用户交互与系统可视化界面。

后端：Spring Boot + MyBatis + MySQL  
  提供稳定的 RESTful API 支撑系统逻辑与数据存储。

推理服务：Python + Flask + YOLOv8（量化模型）  
  在边缘设备上部署轻量模型，进行高效的违停行为检测。

部署平台：地平线 RDK X5 边缘计算设备  
  搭载地平线 AI 芯片，实现低延迟本地推理，适配多路摄像头。
