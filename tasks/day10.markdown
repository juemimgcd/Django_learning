# Day 10 任务清单：补上认证、权限和对象级权限

## 主线继续不变

这一天仍然沿用：

- `APIView`
- `Serializer`
- `service`

今天补的是“安全边界”，不是重写接口组织方式。

也就是说，Day 8 和 Day 9 已经把接口主线搭起来了，Day 10 要做的是：

> 让这套接口不只是“能用”，还要“谁能做什么”非常清楚。

---

## 今天的目标

把当前 API 从“能增删改查”推进到：

- 匿名用户能不能看
- 登录用户能不能创建
- 谁能修改
- 谁能删除
- 是否只有作者本人能改自己的笔记

今天要真正吃透的不是“多一个类名”，而是这三个层次：

- 认证
- 权限
- 对象级权限

---

## 今天这份笔记怎么读

和 Day 8、Day 9 一样，今天不要只看代码结论。

你要继续训练这种阅读方式：

1. 先看这段代码要解决什么问题
2. 再看每个类、每个方法的职责
3. 再看每个参数到底控制什么
4. 最后总结这段代码完成了什么功能

特别是今天，很多概念都很像，如果不拆开看，很容易混：

- `authentication_classes`
- `permission_classes`
- `has_permission`
- `has_object_permission`
- `request.user`
- `request.method`

---

## 为什么今天先学权限，而不是继续换视图抽象

因为对一个真实项目来说，优先级通常是：

1. 接口能用
2. 权限正确
3. 列表工程化
4. 测试补齐
5. 再看是否要进一步抽象

如果你现在就去把 `APIView` 改写成 `GenericAPIView` 或 `ViewSet`，收益未必比先把权限补好更高。

所以今天继续坚持：

> 主项目不换写法，只在现有主线上补安全能力。

---

## 今天建议看的官方文档

- Authentication  
  https://www.django-rest-framework.org/api-guide/authentication/
- Permissions  
  https://www.django-rest-framework.org/api-guide/permissions/
- Tutorial 4: Authentication & Permissions  
  https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/

今天重点看这 5 个词：

1. `SessionAuthentication`
2. `IsAuthenticated`
3. `IsAuthenticatedOrReadOnly`
4. `SAFE_METHODS`
5. `has_object_permission`

---

## 先把今天最容易混的三个概念分开

### 认证

回答的是：

> 你是谁？

例如：

- 这个请求是不是登录用户发来的
- `request.user` 是谁

### 权限

回答的是：

> 你能不能做这件事？

例如：

- 匿名用户能不能创建 note
- 登录用户能不能访问某个接口

### 对象级权限

回答的是：

> 你能不能操作这个具体对象？

例如：

- 你虽然已经登录了
- 但你是不是这条 note 的作者

对当前项目来说，最典型的规则就是：

- 列表和详情可以公开读
- 创建必须登录
- 更新和删除必须登录
- 更新和删除还必须是作者本人

---

## 今天的项目文件建议

```text
notes/
├─ permissions.py
├─ serializers.py
├─ services.py
├─ views.py
├─ urls.py
└─ tests.py
```

今天大概率会改：

- `studynotes/settings.py`
- `notes/permissions.py`
- `notes/views.py`
- `notes/urls.py`
- `notes/tests.py`

---

## 任务 1：在 `settings.py` 中加 DRF 认证默认配置

推荐起步配置：

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

下面把这段代码拆开讲。

### 1.1 `REST_FRAMEWORK = {...}`

这是 DRF 的全局配置入口。

意思是：

- 你可以在这里给整个项目设置 DRF 默认行为

比如：

- 默认用什么认证方式
- 默认用什么权限类
- 默认分页方式

---

### 1.2 `"DEFAULT_AUTHENTICATION_CLASSES"`

这一项的意思是：

- 整个项目默认使用哪些认证方式

认证方式控制的是：

- DRF 怎么识别当前请求是谁发来的

---

### 1.3 `"rest_framework.authentication.SessionAuthentication"`

这个值表示：

- 默认用 Django Session 来做 DRF 认证

为什么当前项目适合它：

- 你前面已经做过 Django 登录
- 项目里已经有 Session 体系
- 现在重点是吃透 DRF 权限，而不是立刻切 JWT

这行配置完成的功能是：

- 让 DRF 可以识别当前请求对应的 Django 登录用户

---

### 1.4 `"DEFAULT_PERMISSION_CLASSES"`

这一项的意思是：

- 整个项目默认使用哪些权限类

权限类决定的是：

- 即使识别出你是谁了
- 你到底能不能访问这个接口

---

### 1.5 `"rest_framework.permissions.AllowAny"`

这个值表示：

- 默认谁都可以访问

为什么今天先用它：

- 因为你接下来会在具体视图里精细配置权限
- 学习阶段先让“全局默认宽松、局部按需收紧”更容易理解

这段配置完成的功能是：

- 先给整个项目设定一个统一的 DRF 默认认证和默认权限基础盘

---

## 任务 2：新建 `notes/permissions.py`

今天建议直接写一个项目里最常见的对象级权限类：

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    message = "你没有权限修改或删除这条笔记。"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author_id == request.user.id
```

下面把这段权限类一行一行拆开。

### 2.1 `from rest_framework.permissions import BasePermission, SAFE_METHODS`

这一行导入了两个东西：

- `BasePermission`
  DRF 自定义权限类的基类
- `SAFE_METHODS`
  DRF 预定义的“安全方法”常量，通常包含：
  - `GET`
  - `HEAD`
  - `OPTIONS`

你可以先把 `SAFE_METHODS` 理解成：

- 这些方法通常是只读的

---

### 2.2 `class IsAuthorOrReadOnly(BasePermission):`

这行的意思是：

- 你定义了一个新的权限类
- 它继承自 DRF 的 `BasePermission`

类名 `IsAuthorOrReadOnly` 本身就在表达规则：

- 如果是作者，可以写
- 如果只是读，可以放开

---

### 2.3 `message = "你没有权限修改或删除这条笔记。"`

这里的 `message` 是权限类自带的一个属性。

作用是：

- 当权限校验失败时
- DRF 可以把这条消息作为错误提示返回

这行完成的功能是：

- 给权限失败时的提示语统一命名

---

### 2.4 `def has_object_permission(self, request, view, obj):`

这是今天最重要的方法之一。

先看这 4 个参数：

- `self`
  当前权限类实例本身
- `request`
  当前请求对象
- `view`
  当前正在执行的视图对象
- `obj`
  当前要进行权限判断的具体对象

为什么这里叫 `has_object_permission`，而不是 `has_permission`：

- 因为这里判断的是“你能不能操作这个具体对象”
- 不是“你能不能进入这个接口”

所以它完成的是：

- 对象级权限检查

---

### 2.5 `if request.method in SAFE_METHODS:`

这一行的意思是：

- 如果当前请求方法属于只读方法
- 那就直接放行

这里的 `request.method` 是：

- 当前 HTTP 请求方法，比如 `GET`、`POST`、`PATCH`、`DELETE`

这里的 `SAFE_METHODS` 是：

- DRF 提供的只读方法集合

这行完成的功能是：

- 让详情查看这类读操作默认通过

---

### 2.6 `return True`

意思是：

- 权限检查通过

在这个分支里它表示：

- 读操作不拦

---

### 2.7 `return obj.author_id == request.user.id`

这一行的意思是：

- 如果不是只读方法
- 那就继续判断：当前对象的作者 id，是否等于当前登录用户 id

这里为什么用 `obj.author_id`，而不是 `obj.author.id`：

- `author_id` 是 Django 外键自动带出来的原始 id 值
- 直接比较 id 更直接，也少一次对象属性访问

这里的 `request.user.id` 表示：

- 当前登录用户自己的 id

这一句完成的功能是：

- 只有当“当前登录用户就是这条 note 的作者”时，写操作才允许通过

---

### 2.8 这整个权限类完成了什么功能

它完成的规则就是：

- 读操作允许所有人
- 写操作只允许作者本人

这也是内容型系统里最常见的对象级权限规则之一。

---

## 任务 3：把权限接进 `APIView`

你现在没有必要切去 `ViewSet` 才能用权限类，`APIView` 一样能优雅接。

推荐思路：

```python
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAuthorOrReadOnly
from .serializers import NoteCreateSerializer, NoteDetailSerializer, NoteUpdateSerializer, UserSummarySerializer
from .services import create_note, delete_note, get_note_detail, update_note


class NoteCreateAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = create_note(author=request.user, validated_data=serializer.validated_data)
        return Response(NoteDetailSerializer(note).data, status=status.HTTP_201_CREATED)


class NoteDetailAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self, pk):
        note = get_note_detail(note_id=pk)
        self.check_object_permissions(self.request, note)
        return note

    def get(self, request, pk):
        note = self.get_object(pk)
        return Response(NoteDetailSerializer(note).data)

    def patch(self, request, pk):
        note = self.get_object(pk)
        serializer = NoteUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        note = update_note(note=note, validated_data=serializer.validated_data)
        return Response(NoteDetailSerializer(note).data)

    def delete(self, request, pk):
        note = self.get_object(pk)
        delete_note(note=note)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSummarySerializer(request.user).data)
```

下面按块拆开讲。

### 3.1 `authentication_classes = [SessionAuthentication]`

这一行的意思是：

- 当前这个视图具体使用哪些认证方式

即使你已经在全局 `REST_FRAMEWORK` 里配了默认认证，很多项目里仍然会在重要视图上显式写出来，原因是：

- 读代码的人一眼就能知道这里用什么认证

这里为什么写成列表：

- 因为一个视图可以同时挂多个认证类

这行完成的功能是：

- 明确告诉 DRF：当前视图使用 Session 认证

---

### 3.2 `permission_classes = [IsAuthenticated]`

这一行的意思是：

- 当前视图必须登录后才能访问

这里的 `IsAuthenticated` 是 DRF 内置权限类。

它只做一件事：

- 检查当前请求是不是登录用户

这行完成的功能是：

- 把“创建 note 必须登录”这条规则挂到视图上

---

### 3.3 `permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]`

这一行是今天最重要的组合之一。

它表示当前视图同时挂了两个权限类：

- `IsAuthenticatedOrReadOnly`
- `IsAuthorOrReadOnly`

这两个类的分工分别是：

- `IsAuthenticatedOrReadOnly`
  控制“匿名用户是否能写”
- `IsAuthorOrReadOnly`
  控制“登录用户是不是对象作者”

你可以把它们理解成两层门：

1. 第一层门：是不是允许你做写操作
2. 第二层门：你是不是这个对象的主人

这行完成的功能是：

- 让接口同时具备“匿名只读”和“作者可写”两层规则

---

### 3.4 `def post(self, request):`

这里和 Day 8、Day 9 一样：

- `post()` 负责处理 HTTP POST 请求

也就是“创建资源”的动作。

---

### 3.5 `serializer = NoteCreateSerializer(data=request.data)`

这一行的意思是：

- 用创建 serializer 校验前端请求体

这里的 `data=` 参数表示：

- 传进去的是输入数据，不是模型实例

---

### 3.6 `serializer.is_valid(raise_exception=True)`

这一行表示：

- 执行输入校验
- 校验失败时直接抛异常，由 DRF 统一返回错误响应

---

### 3.7 `note = create_note(author=request.user, validated_data=serializer.validated_data)`

这里的两个参数要继续记牢：

- `author=request.user`
  当前登录用户就是作者
- `validated_data=serializer.validated_data`
  把校验通过的安全数据交给 service 层

这一行完成的功能是：

- 让 service 层真正执行 note 创建

---

### 3.8 `return Response(NoteDetailSerializer(note).data, status=status.HTTP_201_CREATED)`

这一行的意思是：

- 创建成功后，用详情 serializer 返回完整结果
- 状态码用 201，表示资源创建成功

`NoteCreateAPIView` 这一整段代码完成的功能是：

- 只允许登录用户创建 note
- 走统一 serializer 校验
- 用当前登录用户作为作者
- 返回新创建的详情数据

---

### 3.9 `def get_object(self, pk):`

这一段是今天对象级权限能接上的关键。

```python
def get_object(self, pk):
    note = get_note_detail(note_id=pk)
    self.check_object_permissions(self.request, note)
    return note
```

先看参数：

- `self`
  当前视图实例
- `pk`
  URL 里传进来的 note 主键

---

### 3.10 `note = get_note_detail(note_id=pk)`

这行的意思是：

- 先把目标 note 对象查出来

因为对象级权限判断的前提是：

- 你得先拿到“到底是哪一个对象”

---

### 3.11 `self.check_object_permissions(self.request, note)`

这一行是今天最核心的一行。

它的作用是：

- 让 DRF 去执行当前视图上所有对象级权限类的检查

这里传了两个参数：

- `self.request`
  当前请求对象
- `note`
  当前要检查权限的对象

为什么这行必须手动写：

- 在 `APIView` 里，对象级权限不像某些通用视图那样会自动帮你跑
- 你自己查出对象后，要主动调用它

这行完成的功能是：

- 让 `IsAuthorOrReadOnly` 真正对当前 `note` 生效

如果这里权限不通过：

- DRF 会直接抛出权限异常
- 后面的代码不会继续执行

---

### 3.12 `return note`

这一行表示：

- 对象查出来了
- 权限也通过了
- 把这条 note 返回给后面的 `get`、`patch`、`delete` 方法使用

所以 `get_object()` 这一整段代码完成的功能是：

- 查出目标对象
- 立即执行对象级权限检查
- 只把“允许访问的对象”返回出去

---

### 3.13 `def get(self, request, pk):`

这里对应的是：

- 详情读取

```python
note = self.get_object(pk)
return Response(NoteDetailSerializer(note).data)
```

这里为什么读操作也要走 `get_object(pk)`：

- 因为这样权限检查路径是统一的
- 只不过对于读操作，`IsAuthorOrReadOnly` 会放行

这段代码完成的功能是：

- 获取一条 note 详情，并自动经过对象级权限检查

---

### 3.14 `def patch(self, request, pk):`

这里对应：

- 部分更新

```python
note = self.get_object(pk)
serializer = NoteUpdateSerializer(data=request.data, partial=True)
serializer.is_valid(raise_exception=True)
note = update_note(note=note, validated_data=serializer.validated_data)
return Response(NoteDetailSerializer(note).data)
```

这段里最关键的参数有两个：

- `partial=True`
  说明这是部分更新
- `note=note`
  把已经通过权限检查的对象交给 service 层

为什么这里先 `self.get_object(pk)` 再更新：

- 因为只有先过了对象级权限，才能执行更新

这段代码完成的功能是：

- 只有有权限的人，才能对指定 note 做部分更新

---

### 3.15 `def delete(self, request, pk):`

这一段逻辑也类似：

```python
note = self.get_object(pk)
delete_note(note=note)
return Response(status=status.HTTP_204_NO_CONTENT)
```

这里最重要的点是：

- 删除前同样先走 `self.get_object(pk)`
- 这样对象级权限会先执行

`status=status.HTTP_204_NO_CONTENT` 的意思是：

- 删除成功
- 不返回正文内容

这段代码完成的功能是：

- 只有有权限的人，才能删除这条 note

---

### 3.16 `class MeAPIView(APIView):`

这个接口虽然小，但很实用。

```python
class MeAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSummarySerializer(request.user).data)
```

这里的重点是：

- `request.user`
  就是 DRF 通过认证后识别出来的当前登录用户
- `UserSummarySerializer(request.user)`
  把用户对象转成可以返回给前端的结构

这段代码完成的功能是：

- 给前端一个“我是谁”的接口
- 也方便你观察 DRF 认证是不是已经正确跑通

---

### 3.17 这一整组 APIView 权限代码完成了什么功能

它完成了 4 件事：

1. 给创建接口加上“必须登录”
2. 给详情/更新/删除接口加上“匿名只读”
3. 给对象操作加上“只有作者能改删”
4. 给前端提供了一个可以查看当前登录用户信息的接口

---

## 任务 4：把“作者检查”从 view 里的 `if` 挪出去

今天之后，尽量不要再在每个更新/删除接口里散着写：

```python
if note.author_id != request.user.id:
    ...
```

因为一旦接口多起来，这种写法会越来越乱。

今天要建立的习惯是：

- 身份判断尽量交给认证
- 权限判断尽量交给权限类
- view 只负责流程编排

你要固定下来的结论是：

> 权限规则应该集中管理，而不是每个 view 手搓一遍。

---

## 任务 5：补路由

今天建议把当前用户接口也正式挂上去。

例如：

```python
path("api/me/", views.MeAPIView.as_view(), name="api-me"),
```

如果你已经有这些路由：

```python
path("api/notes/create/", views.NoteCreateAPIView.as_view(), name="note-create"),
path("api/notes/<int:pk>/", views.NoteDetailAPIView.as_view(), name="note-detail"),
```

那今天重点是：

- 把 `MeAPIView` 也接进来

---

### 5.1 `views.MeAPIView.as_view()`

这里的 `.as_view()` 作用还是和前面一样：

- 把类视图转换成 Django 路由系统能识别的可调用入口

### 5.2 `name="api-me"`

作用是：

- 给这个接口起一个反向查找名

这行路由完成的功能是：

- 把当前用户接口挂到 `/api/me/`

---

## 任务 6：今天重点测失败场景

今天一定要刻意验证这几种情况：

- 匿名用户创建，应该失败
- 匿名用户更新，应该失败
- 登录用户修改别人的笔记，应该失败
- 作者本人修改自己的笔记，应该成功

权限代码最怕的不是“成功路径不通”，而是“越权路径漏掉”。

---

## 任务 7：补一组最小权限测试

今天可以先补最小权限测试，重点不是把测试写满，而是把权限差异验证出来。

推荐示例：

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Note


User = get_user_model()


class NotePermissionTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="alice", password="secret123")
        self.other_user = User.objects.create_user(username="bob", password="secret123")
        self.note = Note.objects.create(
            author=self.author,
            title="Owned note",
            content="only author can edit",
            status=Note.STATUS_DRAFT,
        )

    def test_anonymous_user_cannot_create_note(self):
        response = self.client.post(
            reverse("note-create"),
            data={
                "title": "Anonymous",
                "content": "should fail",
                "status": "draft",
            },
            content_type="application/json",
        )
        self.assertIn(response.status_code, [401, 403])

    def test_non_author_cannot_update_note(self):
        self.client.force_login(self.other_user)
        response = self.client.patch(
            reverse("note-detail", args=[self.note.id]),
            data={"title": "hack"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_author_can_update_own_note(self):
        self.client.force_login(self.author)
        response = self.client.patch(
            reverse("note-detail", args=[self.note.id]),
            data={"title": "updated"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
```

下面把关键参数解释一下。

### 7.1 `self.client.force_login(...)`

作用是：

- 在测试里直接模拟一个已登录用户

### 7.2 `reverse("note-detail", args=[self.note.id])`

作用是：

- 按路由名反查 URL
- `args=[self.note.id]` 表示把这条 note 的主键填进 `<int:pk>` 的位置

### 7.3 `content_type="application/json"`

作用是：

- 告诉测试客户端：这次请求体按 JSON 处理

### 7.4 `self.assertIn(response.status_code, [401, 403])`

为什么匿名创建这里不强行写死一个状态码：

- 因为不同认证配置和中间件细节下，匿名写操作可能返回 401 或 403
- 学习阶段更重要的是理解“它必须失败”

### 7.5 这组测试完成了什么功能

它完成了最小的权限验证闭环：

- 匿名写失败
- 非作者写失败
- 作者本人写成功

这就是 Day 10 最该测出来的东西。

---

## 补充知识：为什么今天不切去 `ViewSet`

因为权限类不是 `ViewSet` 专属能力。

很多人学 DRF 时会误以为：

- 好像只有到了 `ViewSet` 才算“正规写法”

其实不是。

真实项目里：

- `APIView + permission classes + service`

本来就是非常常见、也很稳的一条路线。

所以今天最重要的不是换类，而是把：

- 认证
- 视图级权限
- 对象级权限

这三层边界做扎实。

---

## 今天不做什么

- 不改成 `GenericAPIView`
- 不改成 `ViewSet`
- 不为了权限去改整套路由结构
- 不引入 JWT

今天先把 Session 下的认证和对象级权限吃透。

---

## 今天的交付标准

- [ ] `REST_FRAMEWORK` 中配置默认认证
- [ ] 新建 `notes/permissions.py`
- [ ] 实现 `IsAuthorOrReadOnly`
- [ ] 把权限类接进现有 `APIView`
- [ ] 匿名用户只能读
- [ ] 登录用户可以创建
- [ ] 非作者不能改删别人的笔记
- [ ] 作者本人可以改删自己的笔记
- [ ] 补充对应测试

---

## 今日复盘问题

1. 为什么“已登录”不等于“有权修改这个对象”？
2. 为什么对象级权限应该抽成单独的权限类？
3. `has_object_permission(self, request, view, obj)` 里这几个参数各自代表什么？
4. 为什么在 `APIView` 中仍然值得使用 `permission_classes`？
5. 如果以后换 JWT，今天学到的哪些边界思想仍然成立？

---

## 一句总结

今天你没有换框架写法，而是在原有主线上补上了真实项目最关键的一层：

> 认证、权限和对象级权限。
