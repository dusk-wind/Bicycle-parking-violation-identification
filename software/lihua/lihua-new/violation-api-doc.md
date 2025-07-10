# 违规记录API接口文档

## 基础URL

所有API的基础URL为：`/api/violation`

## 通用返回格式

所有接口返回的数据格式统一为：

```json
{
  "code": 200,  // 状态码：200表示成功，404表示资源不存在，500表示服务器错误
  "message": "success",  // 状态消息
  "data": {}  // 具体数据，格式因接口而异
}
```

## 1. 获取违规记录列表

获取所有违规记录的分页列表。

- **URL**: `/api/violation/list`
- **方法**: GET
- **参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|-----|
| plateNumber | string | 否 | 车牌号，支持模糊查询 |
| status | integer | 否 | 处理状态：0-未处理，1-已处理 |
| pageNum | integer | 否 | 页码，默认为1 |
| pageSize | integer | 否 | 每页条数，默认为10 |

- **请求示例**:
```
GET /api/violation/list?plateNumber=京A&status=0&pageNum=1&pageSize=10
```

- **响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "plateNumber": "京A12345",
        "violationType": 1,
        "violationTypeName": "停车越位",
        "violationTime": "2023-01-01 12:00:00",
        "location": "A区停车场",
        "status": 0,
        "description": "车辆停放超出车位线约30厘米",
        "fine": 100.00,
        "createTime": "2023-01-01 12:05:00",
        "updateTime": "2023-01-01 12:05:00"
      }
    ],
    "total": 100,
    "current": 1,
    "pageSize": 10
  }
}
```

## 2. 获取违规记录详情

获取指定ID的违规记录详情。

- **URL**: `/api/violation/{id}`
- **方法**: GET
- **参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|-----|
| id | integer | 是 | 违规记录ID |

- **请求示例**:
```
GET /api/violation/1
```

- **响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "plateNumber": "京A12345",
    "violationType": 1,
    "violationTypeName": "停车越位",
    "violationTime": "2023-01-01 12:00:00",
    "location": "A区停车场",
    "status": 0,
    "description": "车辆停放超出车位线约30厘米",
    "fine": 100.00,
    "createTime": "2023-01-01 12:05:00",
    "updateTime": "2023-01-01 12:05:00"
  }
}
```

- **错误响应**:
```json
{
  "code": 404,
  "message": "记录不存在",
  "data": null
}
```

## 3. 获取违规记录统计数据

获取所有违规记录的统计信息。

- **URL**: `/api/violation/stats`
- **方法**: GET
- **参数**: 无

- **请求示例**:
```
GET /api/violation/stats
```

- **响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "totalViolations": 100,
    "pendingViolations": 20,
    "processedViolations": 80,
    "totalFines": 15000,
    "violationsByType": [
      {
        "type": 1,
        "typeName": "停车越位",
        "count": 30
      },
      {
        "type": 2,
        "typeName": "占用消防车道",
        "count": 15
      }
    ]
  }
}
```

## 4. 处理违规记录

将指定ID的违规记录标记为已处理。

- **URL**: `/api/violation/{id}/process`
- **方法**: POST
- **参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|-----|------|-----|
| id | integer | 是 | 违规记录ID |
| note | string | 否 | 处理备注 |

- **请求体示例**:
```json
{
  "note": "已通知车主并缴纳罚款"
}
```

- **响应示例**:
```json
{
  "code": 200,
  "message": "处理成功",
  "data": null
}
```

- **错误响应**:
```json
{
  "code": 500,
  "message": "处理失败：记录不存在",
  "data": null
}
```

## 5. 违规类型定义

| 代码 | 类型名称 | 罚款金额(元) |
|-----|---------|------------|
| 1   | 停车越位 | 100        |
| 2   | 占用消防车道 | 500     |
| 3   | 占用人行道 | 400      |
| 4   | 非法停车 | 300        |
| 5   | 其他原因 | 200        |

## 6. 记录状态定义

| 代码 | 状态名称 |
|-----|---------|
| 0   | 未处理   |
| 1   | 已处理   |