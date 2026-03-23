# Day 12 任务清单：学会 DRF 的认证、权限和对象级权限

## 今天的目标

前面几天你已经把 DRF 的“接口结构”基本搭起来了。  
今天要补的是 API 真正很关键的一层：

- 谁能访问
- 谁能创建
- 谁能更新
- 谁能删除
- 谁能操作某个具体对象

如果说前几天主要是在学“怎么把接口写出来”，  
那今天就是在学：

> 怎么让接口写得安全、边界清楚、行为可控。

今天学完后，你应该能做到：

- 理解 DRF 里的“认证”和“权限”不是一回事
- 会用 `SessionAuthentication`
- 会用 `AllowAny`、`IsAuthenticated`、`IsAuthenticatedOrReadOnly`
- 会写自定义权限类
- 会实现“只有作者本人能修改或删除笔记”

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 55 分钟 | 阅读认证和权限文档 |
| 理解边界 | 35 分钟 | 把“已登录”和“有权限”分清楚 |
| 核心编码 | 120 分钟 | 为当前 DRF 接口接入认证和自定义权限 |
| 联调复盘 | 50 分钟 | 验证匿名、普通用户、作者三种身份的行为差异 |

---

## 今天的官方文档入口

- 教程 4：Authentication & Permissions  
  https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
- Authentication API Guide  
  https://www.django-rest-framework.org/api-guide/authentication/
- Permissions API Guide  
  https://www.django-rest-framework.org/api-guide/permissions/

建议阅读顺序：

1. 先看教程 4
2. 再看 `Authentication`
3. 再看 `Permissions`

---

## 先把今天最容易混淆的点说清楚

## 1. 认证不是权限

很多刚从别的框架切过来的人，会把这两个词混在一起。  
你今天一定要彻底分开：

### 认证做什么

回答这个问题：

> 你是谁？

比如：

- 你是不是登录用户
- 这个请求有没有合法身份

### 权限做什么

回答这个问题：

> 你能不能做这件事？

比如：

- 匿名用户能不能创建笔记
- 登录用户能不能删除别人的笔记

一句话记忆：

- 认证解决“身份”
- 权限解决“行为”

---

## 2. `request.user` 只有在认证跑通后才有意义

前面原生 Django 阶段你已经接触过：

- `request.user`
- Session

在 DRF 里，这套能力仍然成立。  
只是 DRF 又包了一层“认证机制”的抽象。

今天你先继续用最适合当前项目的方式：

- `SessionAuthentication`

原因很简单：

- 你前面已经做过 Django 登录
- 现在项目也不是 JWT 主线
- 先把 DRF 权限体系学顺更重要

---

## 3. 权限分两层：视图级权限和对象级权限

这是今天的重点。

### 视图级权限

例如：

- 匿名用户可不可以访问这个接口
- 登录用户才能不能进这个端点

### 对象级权限

例如：

- 你虽然能访问这个详情接口
- 但你是不是这个具体 `Note` 的作者

如果你只做了第一层，而没做第二层，就会出现很典型的问题：

- 所有登录用户都能改任何人的笔记

这就是为什么今天一定要学自定义权限类。

---

## 今天你必须理解的 6 个概念

## 1. `authentication_classes` 决定“怎么识别你是谁”

比如：

```python
from rest_framework.authentication import SessionAuthentication

authentication_classes = [SessionAuthentication]
```

这表示：

- 通过 Django Session 来识别当前用户

对你当前项目来说，这是最自然的衔接方式。

---

## 2. `permission_classes` 决定“你有没有资格做这件事”

例如：

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly

permission_classes = [IsAuthenticatedOrReadOnly]
```

它的含义是：

- 读操作允许匿名用户
- 写操作必须登录

这非常适合“公开可读、登录可写”的内容型接口。

---

## 3. 常见权限类先记住这 3 个就够了

### `AllowAny`

- 谁都能访问

### `IsAuthenticated`

- 必须登录

### `IsAuthenticatedOrReadOnly`

- 读开放
- 写需要登录

光把这 3 个用熟，你已经能覆盖很多接口场景。

---

## 4. 对象级权限要靠自定义权限类

对于“只有作者本人可以修改或删除自己的笔记”这种需求，  
你需要写一个自定义权限类。

例如，在 `notes/permissions.py` 中新建：

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author_id == request.user.id
```

这个类的意思非常直接：

- 如果是安全方法，比如 `GET`、`HEAD`、`OPTIONS`，允许访问
- 如果是写操作，就必须是对象作者本人

这就是 DRF 里非常经典的对象级权限模式。

---

## 5. `has_permission()` 和 `has_object_permission()` 不是一个层级

这是很多初学者会混的地方。

### `has_permission()`

先判断：

- 你能不能进这个视图

### `has_object_permission()`

再判断：

- 你能不能操作这个具体对象

通俗一点说：

- 前者是“进门检查”
- 后者是“到具体房间再检查”

---

## 6. 权限类不是为了让代码“高级”，而是为了把规则集中起来

如果你继续在视图里满地写：

- `if not request.user.is_authenticated`
- `if note.author_id != request.user.id`

接口数量一多就会很乱。  
而权限类的价值就是：

- 让安全规则集中管理
- 让视图代码更干净
- 让项目行为更统一

---

## 今天的项目任务

今天我们要把当前 DRF 接口的权限体系做规范化。

建议完成这些事：

1. 在 `settings.py` 中增加 `REST_FRAMEWORK` 基础配置
2. 把 DRF 接口统一设置为基于 Session 的认证
3. 新建 `notes/permissions.py`
4. 写 `IsAuthorOrReadOnly`
5. 把 `NoteViewSet` 接上对象级权限
6. 验证匿名用户、登录用户、作者本人三种行为差异

---

## 先补 `settings.py`

在 `studynotes/settings.py` 里，你可以开始加一段 DRF 基础配置：

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}
```

这段配置的作用是：

- 全局默认使用 Session 认证
- 默认权限先放宽，然后在具体视图里再细化

学习阶段这样更容易看懂。  
等你项目更大时，再考虑全局默认收紧。

---

## 再写自定义权限类

在 `notes/permissions.py` 中新增：

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    message = "你没有权限修改或删除这条笔记。"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author_id == request.user.id
```

你可以先把它理解成：

- “读可以放开”
- “写必须是作者”

这是内容型系统里很常见的权限规则。

---

## 把权限接到 `ViewSet` 上

在 `notes/views.py` 中，`NoteViewSet` 可以改成这样：

```python
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from .permissions import IsAuthorOrReadOnly


class NoteViewSet(ModelViewSet):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        return (
            Note.objects.select_related("author")
            .prefetch_related("tags", "comments")
            .all()
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return NoteListSerializer
        if self.action == "retrieve":
            return NoteDetailSerializer
        return NoteWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

这时 DRF 会做两层检查：

1. `IsAuthenticatedOrReadOnly` 决定匿名用户能不能写
2. `IsAuthorOrReadOnly` 决定登录用户能不能改这个具体对象

这就是“视图级 + 对象级”的配合。

---

## 今天建议再补一个“当前用户接口”

为了更好理解 DRF 里的认证结果，  
你可以新增一个简单接口：

```python
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication


@api_view(["GET"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def drf_me(request):
    return Response({
        "id": request.user.id,
        "username": request.user.username,
    })
```

这个接口很适合帮你观察：

- 登录和未登录状态下 `request.user` 的区别
- DRF 权限错误的标准返回格式

---

## 今天推荐你主动观察的 6 个现象

## 1. 未登录用户的错误格式更标准了

你会看到类似：

```json
{
  "detail": "Authentication credentials were not provided."
}
```

这比自己满地手写错误响应更统一。

## 2. 已登录不等于有对象操作权限

这是今天最重要的体会之一。  
“能登录”和“能改别人数据”是完全不同的两层检查。

## 3. 权限类会让视图代码明显变干净

你不再需要每个接口都手动写：

- 认证判断
- 作者判断

视图会变得更专注于业务和数据流。

## 4. 对象级权限是 DRF 的强项之一

这部分就是 DRF 在做资源式 API 时特别顺手的地方。

## 5. `SAFE_METHODS` 这个常量很好用

它能让你非常自然地表达：

- 读开放
- 写受限

## 6. 你会开始真正理解“框架统一规则”的价值

当每个接口都用统一权限类时，  
你的项目行为会更稳定，也更容易维护。

---

## 今天怎么测试

启动服务：

```powershell
python manage.py runserver
```

### 1. 匿名访问列表和详情

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/" -Method Get
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/1/" -Method Get
```

应该能访问。

### 2. 匿名创建

```powershell
$body = @{
    title = "Anonymous create"
    content = "应该失败"
    status = "draft"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

应该返回认证错误。

### 3. 登录用户修改自己的笔记

这个请求应该成功。

### 4. 登录用户修改别人的笔记

这个请求应该返回权限错误。

这一步很关键。  
一定要自己造两名用户和至少两篇不同作者的笔记来测。

---

## 今天的易错点

## 1. 以为设置了 `IsAuthenticated` 就已经等于作者校验

不是。  
它只说明“你登录了”，不说明“这个对象归你管”。

## 2. 自定义权限类只写了 `has_permission()`，没写对象级判断

这样就会缺掉“具体对象”的限制。

## 3. `perform_create()` 里忘了注入作者

如果创建时作者没写对，  
后面的对象级权限也会跟着失真。

## 4. 只测成功场景，不测失败场景

权限代码最怕的就是：

- 正常情况能跑
- 越权场景没测

所以今天一定要重点测：

- 未登录写
- 登录但不是作者写

## 5. 对匿名用户和登录用户用了完全相同的返回策略，却没意识到差异

认证失败和权限失败是两件事。  
今天要刻意观察：

- 401 是什么情况
- 403 是什么情况

---

## 今天结束后的验收标准

- 你能清楚区分认证和权限
- 你能解释视图级权限和对象级权限的区别
- 你能写出 `IsAuthorOrReadOnly`
- 你能让匿名用户只读、登录用户可写、作者本人可改删
- 你能看懂 DRF 的标准认证/权限错误响应

---

## 今天的复盘问题

建议你写下这 3 个问题的答案：

1. 为什么“已登录”不等于“有权限修改这个对象”？
2. 为什么对象级权限要抽成单独的类，而不是散落在视图里？
3. 如果以后你要接 JWT，今天学到的哪部分思想仍然成立？

---

## 明天会学什么

明天我们会把接口继续工程化：

- 过滤
- 搜索
- 排序
- 分页

也就是把你的 API 从“能用”继续推进到：

> “对于真实列表接口来说，更像一个可交付的后端服务。”
