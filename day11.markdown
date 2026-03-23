# Day 11 任务清单：学会 `ViewSet`、`Router` 和更像框架化 API 的写法

## 今天的目标

前两天我们已经经历了这条演进路线：

- 原生 Django JSON 视图
- DRF 函数式视图
- `APIView`
- 通用类视图

今天再往前一步，你会接触 DRF 最有代表性的组合：

- `ViewSet`
- `Router`

这两个东西第一次看时，很容易让人觉得“有点抽象”。  
但只要理解了它们的目标，你会发现它们很实用：

> 如果你的接口本质上是围绕某个资源做一组标准动作，那路由和动作映射完全可以交给框架。

今天学完后，你应该能做到：

- 理解 `ViewSet` 是什么
- 知道 `ModelViewSet` 帮你封装了哪些动作
- 会用 `DefaultRouter` 自动生成路由
- 能把 `Note` 资源改造成一套更完整的 DRF 风格接口
- 明白 `ViewSet` 的优点和缺点，不会盲目滥用

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 45 分钟 | 看 ViewSets 和 Routers 官方文档 |
| 理解动作映射 | 35 分钟 | 把 `list/create/retrieve/update/destroy` 的关系理顺 |
| 核心编码 | 130 分钟 | 用 `ModelViewSet` 重构 Note 接口 |
| 联调复盘 | 50 分钟 | 观察路由自动生成效果，并对比前几天实现 |

---

## 今天的官方文档入口

- 教程 6：ViewSets & Routers  
  https://www.django-rest-framework.org/tutorial/6-viewsets-and-routers/
- ViewSets API Guide  
  https://www.django-rest-framework.org/api-guide/viewsets/
- Routers API Guide  
  https://www.django-rest-framework.org/api-guide/routers/

建议阅读顺序：

1. 先看教程 6
2. 再看 `ViewSets`
3. 最后看 `Routers`

---

## 先用一句话理解今天学的是什么

前几天你一直在做这件事：

- 定义视图
- 手动写 URL
- 手动决定哪个类负责列表、哪个类负责详情

今天 DRF 提供了一个更“资源导向”的方式：

- 一个 `ViewSet` 表示一组围绕同一资源的动作
- 一个 `Router` 帮你自动生成对应路由

如果用 `Note` 举例，那就是：

- `list`
- `create`
- `retrieve`
- `update`
- `partial_update`
- `destroy`

这些动作可以交给同一个 `ViewSet` 管理。

---

## 今天你必须理解的 6 个概念

## 1. `ViewSet` 不是普通类视图，而是“动作集合”

通俗一点说：

- `APIView` 更像“一个接口类”
- `ViewSet` 更像“一个资源控制器”

它不是按 `get()`、`post()` 来组织，而是按动作组织：

- `list()`
- `create()`
- `retrieve()`
- `update()`
- `partial_update()`
- `destroy()`

这和 REST 资源建模是很契合的。

---

## 2. `ModelViewSet` 是最常见的快速 CRUD 方案

如果你写：

```python
from rest_framework.viewsets import ModelViewSet


class NoteViewSet(ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteDetailSerializer
```

DRF 基本已经帮你把标准 CRUD 动作都准备好了。  
当然，真实项目不会只写这么少，通常还会补：

- 查询优化
- 不同动作切换 serializer
- 权限控制
- 当前用户逻辑

但它确实能极大减少样板代码。

---

## 3. `Router` 帮你自动生成 URL

以前你要写：

```python
path("drf/v3/notes/", ...),
path("drf/v3/notes/<int:pk>/", ...),
```

今天你可以改成：

```python
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("notes", views.NoteViewSet, basename="note")
```

然后在 `urls.py` 中接入：

```python
urlpatterns = [
    ...
] + router.urls
```

这样 DRF 会自动帮你生成一套标准路由。

---

## 4. `get_serializer_class()` 在 `ViewSet` 里更常用

因为 `ViewSet` 会处理多个动作，  
而不同动作往往需要不同 serializer：

- `list` 用精简返回
- `retrieve` 用详情返回
- `create/update/partial_update` 用写入校验

常见写法：

```python
def get_serializer_class(self):
    if self.action == "list":
        return NoteListSerializer
    if self.action == "retrieve":
        return NoteDetailSerializer
    return NoteWriteSerializer
```

这里的 `self.action` 很重要。  
它是 `ViewSet` 模式里非常常用的判断依据。

---

## 5. `get_permissions()` 可以按动作切换权限

比如你可能想要：

- 列表和详情允许匿名查看
- 创建必须登录
- 更新和删除必须是作者本人

在 `ViewSet` 里你可以开始按动作切分权限逻辑：

```python
def get_permissions(self):
    if self.action in ["list", "retrieve"]:
        return [AllowAny()]
    return [IsAuthenticated()]
```

今天先学会这个思路，  
明天我们再专门把认证和权限做扎实。

---

## 6. `ViewSet` 很省代码，但不是所有接口都适合

适合：

- 标准资源 CRUD
- 资源风格清晰
- 路由规则标准

不太适合：

- 动作完全不规则
- 一个接口牵扯很多不同资源
- 很强的业务编排型端点

这时你仍然可以回退到：

- `APIView`
- 通用类视图
- 自定义 action

---

## 今天的项目任务

今天我们把 `Note` 相关的 DRF 接口，继续升级成更典型的 `ViewSet + Router` 风格。

建议完成这些事：

1. 在 `notes/views.py` 中新增 `NoteViewSet`
2. 用 `DefaultRouter` 注册 `notes`
3. 用 `get_queryset()` 做查询优化
4. 用 `get_serializer_class()` 按动作切换 serializer
5. 用 `perform_create()` 注入当前登录用户
6. 初步按动作配置权限

---

## 推荐代码结构

## 1. 先写 `NoteViewSet`

```python
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Note
from .serializers import NoteListSerializer, NoteDetailSerializer, NoteWriteSerializer


class NoteViewSet(ModelViewSet):
    def get_queryset(self):
        queryset = (
            Note.objects.select_related("author")
            .prefetch_related("tags", "comments")
            .all()
            .order_by("-created_at")
        )

        if self.action == "list":
            return queryset.prefetch_related("tags")

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return NoteListSerializer
        if self.action == "retrieve":
            return NoteDetailSerializer
        return NoteWriteSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
```

这里最重要的是理解：

- `self.action` 是 `ViewSet` 里的核心分支点
- 同一个 `ViewSet` 里，可以按动作切换 serializer、权限和 queryset 细节

---

## 2. 再写 Router

在 `notes/urls.py` 中，你可以这么改：

```python
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("drf/v4/notes", views.NoteViewSet, basename="drf-v4-note")

urlpatterns = [
    ...
] + router.urls
```

如果你更想让结构清晰一点，也可以把 DRF 路由单独拆到另一个文件中。  
但对现在这个学习项目来说，先放在同一个 `urls.py` 里就够了。

---

## 3. 今天建议补一个自定义动作：我的笔记

如果只学标准 CRUD，会稍微有点“只会套模板”的感觉。  
所以今天建议你体验一个自定义动作：

```python
from rest_framework.decorators import action
from rest_framework.response import Response


class NoteViewSet(ModelViewSet):
    ...

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def mine(self, request):
        queryset = (
            self.get_queryset()
            .filter(author=request.user)
            .order_by("-created_at")
        )
        serializer = NoteListSerializer(queryset, many=True)
        return Response(serializer.data)
```

它会生成类似这样的路由：

- `/drf/v4/notes/mine/`

这个接口非常适合让你理解：

- `ViewSet` 不只会标准 CRUD
- 非标准动作也可以以比较整洁的方式放进去

---

## 今天推荐你主动观察的 6 个现象

## 1. 路由文件大幅变短了

你会明显感受到：

- 以前要手写很多 `path(...)`
- 现在一个 `router.register(...)` 就能带起一组路由

## 2. 一个类开始代表“一个资源”

这会让你的 API 组织方式更接近很多成熟 DRF 项目。

## 3. 动作切分比 HTTP 方法切分更适合资源式接口

例如：

- `list`
- `retrieve`
- `create`

这些名字比单纯的 `get/post` 更接近业务含义。

## 4. 代码虽然更短了，但理解门槛反而稍高一点

这是正常现象。  
因为 DRF 做了更多“约定式封装”。

你现在要适应的是：

- 框架替你做了哪些默认动作
- 你该覆盖哪些钩子

## 5. 自定义 action 能让 `ViewSet` 更灵活

这会帮你避免一个误区：

- 不是只有标准 CRUD 才能用 `ViewSet`

## 6. 你会开始觉得它有点像“控制器”

虽然 Django/DRF 不强调 MVC 里那种传统 controller 命名，  
但 `ViewSet` 在体验上确实有一点“资源控制器”的感觉。

---

## 今天怎么测试

启动服务：

```powershell
python manage.py runserver
```

### 1. 测试自动生成的列表接口

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/" -Method Get
```

### 2. 测试详情接口

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/1/" -Method Get
```

### 3. 测试创建接口

```powershell
$body = @{
    title = "Day 11 ViewSet"
    content = "今天练习 ViewSet 和 Router"
    status = "draft"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

### 4. 测试自定义动作

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/mine/" -Method Get
```

观察：

- 未登录时是什么返回
- 登录后是不是只返回自己的笔记

---

## 今天的易错点

## 1. 把 `self.action` 和 `request.method` 混掉

在 `ViewSet` 里，优先关注：

- `self.action`

因为它更贴近资源动作语义。

## 2. `Router` 注册路径写得过深

虽然技术上可以直接注册：

- `"drf/v4/notes"`

但如果你后面想把 DRF 路由拆分管理，  
也可以只注册 `"notes"`，再在总路由里挂前缀。

学习阶段两种都行，关键是你自己能看懂。

## 3. 忘记在写入时注入作者

如果你不在 `perform_create()` 里补：

```python
serializer.save(author=self.request.user)
```

创建逻辑就会不完整。

## 4. 自定义 action 里又回到手写很多重复逻辑

如果你写 `mine()`，也尽量复用：

- `get_queryset()`
- `get_serializer()`

不要一下子又退回完全手写风格。

## 5. 误以为 `ModelViewSet` 已经把权限问题全部解决

没有。  
它只是让 CRUD 动作更省代码。  
真正的对象级权限，明天和后天还要继续补。

---

## 今天结束后的验收标准

- 你能说清楚 `ViewSet` 和通用类视图的区别
- 你能独立写出 `ModelViewSet`
- 你能用 `DefaultRouter` 自动生成路由
- 你能根据 `self.action` 切换 serializer 和权限
- 你能写一个自定义 `@action`
- 你能解释 `ViewSet + Router` 为什么适合标准资源式 API

---

## 今天的复盘问题

建议你写下这 3 个问题的答案：

1. `ViewSet` 的核心抽象到底是什么？
2. 为什么 `Router` 会让路由管理更轻，但理解成本更高一点？
3. 对你现在这个项目来说，`APIView`、通用类视图、`ViewSet` 哪一种最顺手？

---

## 明天会学什么

明天我们会把 DRF 最关键的“安全边界”补完整：

- 认证
- 权限
- 对象级权限

到那一天你会开始真正写出：

> “匿名用户能看，登录用户能发，只有作者本人能改删”的 DRF API。
