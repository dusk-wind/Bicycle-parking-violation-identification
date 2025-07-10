# 梨花校园违停检测系统后端

## 项目简介

这是梨花校园违停检测系统的后端服务，基于SpringBoot开发，提供违停记录管理、摄像头管理、数据统计分析等功能的REST API接口。

## 技术栈

- **框架**: Spring Boot 2.x
- **持久化**: MyBatis
- **数据库**: MySQL 8.0
- **构建工具**: Maven
- **JDK版本**: JDK 8+

## 项目结构

```
lihua-new/
├── src/main/java/com/lihua/demo/
│   ├── Camera/                 # 摄像头模块
│   │   ├── controller/         # 控制器
│   │   ├── service/           # 服务层
│   │   ├── entity/            # 实体类
│   │   ├── dto/               # 数据传输对象
│   │   └── mapper/            # Mapper接口
│   ├── Violation/             # 违停记录模块
│   │   ├── controller/        # 控制器
│   │   ├── service/          # 服务层
│   │   ├── entity/           # 实体类
│   │   ├── dto/              # 数据传输对象
│   │   └── mapper/           # Mapper接口
│   ├── common/               # 通用类
│   ├── dto/                  # 全局DTO
│   └── LihuaApplication.java # 主启动类
├── src/main/resources/
│   ├── com/lihua/demo/mapper/ # MyBatis XML映射文件
│   ├── application.yml        # 配置文件
│   └── init_data.sql         # 数据库初始化脚本
└── pom.xml                   # Maven配置
```

## 数据库设计

### 表结构

1. **camera (摄像头表)**
   - id: 摄像头主键ID
   - serial: 设备序列号
   - interface_type: 接口类型
   - connected: 是否连接
   - last_updated: 最后更新时间

2. **violation_record (违停记录表)**
   - id: 违停记录主键ID
   - camera_id: 摄像头ID（外键）
   - image_path: 识别截图路径
   - upload_time: 识别记录上传时间
   - confidence: 模型识别置信度
   - location: 识别位置

## 快速开始

### 1. 环境准备

- JDK 8 或更高版本
- Maven 3.6+
- MySQL 8.0+

### 2. 数据库配置

1. 创建数据库：
```sql
CREATE DATABASE lihua_db DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 执行初始化脚本：
```bash
mysql -u root -p lihua_db < src/main/resources/init_data.sql
```

### 3. 修改配置

编辑 `src/main/resources/application.yml`，修改数据库连接信息：

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/lihua_db?useUnicode=true&characterEncoding=utf8&zeroDateTimeBehavior=convertToNull&useSSL=true&serverTimezone=GMT%2B8
    username: your_username
    password: your_password
```

### 4. 启动项目

```bash
# 进入项目目录
cd lihua-new

# 编译打包
mvn clean package

# 运行项目
mvn spring-boot:run
```

或者直接运行主类：
```bash
java -jar target/lihua-new-1.2.1.jar
```

### 5. 验证启动

访问 http://localhost:8080/api/camera/status 确认服务正常启动。

## API接口文档

### 摄像头相关接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/camera/status` | 获取摄像头状态 |
| POST | `/api/camera/toggle` | 切换摄像头连接状态 |
| GET | `/api/camera/list` | 获取摄像头列表 |
| GET | `/api/camera/stats` | 获取摄像头统计信息 |

### 违停记录相关接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/history/list` | 分页查询违停记录 |
| GET | `/api/history/stats` | 获取违停统计数据 |
| GET | `/api/history/detail/{id}` | 获取违停记录详情 |
| POST | `/api/history/export` | 导出违停记录 |

### 首页相关接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/index/statistics` | 获取首页统计数据 |
| GET | `/api/index/latest/{limit}` | 获取最新记录 |
| GET | `/api/index/updates` | 获取系统更新信息 |

### 数据分析相关接口

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/api/data/overview` | 获取概览统计数据 |
| GET | `/api/data/all` | 获取所有统计数据 |

## 前端对接

### 请求格式

所有POST请求需要设置Content-Type为application/json：

```javascript
fetch('/api/camera/toggle', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ connect: true })
});
```

### 响应格式

所有接口统一返回格式：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {}
}
```

- code: 状态码（200成功，500错误）
- msg: 响应消息
- data: 具体数据

## 开发说明

### 添加新功能

1. 在对应模块下创建Controller、Service、Mapper
2. 在resources/mapper下添加XML映射文件
3. 按需创建DTO和Entity类

### 数据库变更

1. 修改建表语句（init_data.sql）
2. 更新对应的Entity类
3. 修改Mapper XML文件

## 注意事项

1. **数据库连接**: 确保MySQL服务正常运行且连接信息正确
2. **端口冲突**: 默认端口8080，如有冲突请修改application.yml
3. **跨域配置**: 已配置允许所有域名访问，生产环境请根据需要调整
4. **日志输出**: 开发环境下开启了debug日志，生产环境建议调整为info级别

## 故障排除

### 1. 启动失败
- 检查JDK版本是否符合要求
- 检查Maven依赖是否下载完整
- 检查数据库连接信息是否正确

### 2. 接口返回500错误
- 查看控制台日志确定具体错误
- 检查数据库表结构是否正确
- 确认请求参数格式是否正确

### 3. 数据库连接失败
- 确认MySQL服务是否启动
- 检查数据库名、用户名、密码是否正确
- 检查防火墙设置

## 许可证

本项目仅供学习使用。 