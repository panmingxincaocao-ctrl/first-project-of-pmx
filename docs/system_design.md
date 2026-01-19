# 网校系统设计

## 账户系统设计

- **注册/登录**：支持邮箱 + 密码注册，登录后返回 Token。
- **密码安全**：后端使用哈希存储（Werkzeug）。
- **访问控制**：通过 Token 鉴权，服务端解析角色后进行权限判断。

## 角色系统设计

| 角色 | 权限范围 | 关键能力 |
| --- | --- | --- |
| 管理员 | 全局管理 | 用户管理、课程审核、系统设置 |
| 教师 | 课程管理 | 创建课程、维护章节、上传 PPT/视频 |
| 学生 | 学习中心 | 浏览课程、学习 PPT/视频、记录进度 |

## 核心功能清单

1. **课程管理模块**
   - 教师创建课程，状态默认 `pending` 等待审核。
   - 教师新增课程章节、上传 PPT/视频资源。
   - 所有用户可浏览课程列表。
2. **PPT 课件功能**
   - 记录 PPT 文件信息、页数、是否可编辑。
   - 支持前端播放、翻页、进度记录（按页）。
3. **视频网课功能**
   - 记录视频文件路径、时长。
   - 学生观看时记录已观看秒数。
4. **学生学习记录**
   - 按课程、资源保存学习进度。
   - 可查询已学习 PPT 页数和视频播放进度。

## API 摘要

- `POST /api/auth/register` 注册账号
- `POST /api/auth/login` 登录获取 Token
- `GET /api/courses` 课程列表
- `POST /api/courses` 教师创建课程
- `POST /api/courses/:id/chapters` 添加章节
- `POST /api/chapters/:id/ppt` 上传 PPT
- `POST /api/chapters/:id/video` 上传视频
- `POST /api/courses/:id/enroll` 学生报名课程
- `POST /api/progress` 学习进度更新
- `GET /api/progress` 查看学习进度
