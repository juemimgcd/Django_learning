# Day 8 任务清单：从今天开始固定主线，直接用 `Serializer + APIView + service`

## 先把这 7 天的主线定死

从 Day 8 到 Day 14，这个项目统一采用下面这套写法：

- API 层：DRF `APIView`
- 输入校验和输出结构：`serializers.py`
- 数据库读写：`services.py`
- 数据结构：`models.py`
- 认证、权限、分页、测试，后面都继续加在这条主线上

这意味着：

- 不再把“手写 `JsonResponse` + 手写 `serialize_note()`”当成主项目写法
- 不再先用 `@api_view` 写一版，第二天再整个推翻成 `APIView`
- `model.serialize`、`JsonResponse`、`@api_view` 只作为补充知识了解

你这阶段的目标不是“把 DRF 的每种写法都写一遍”，而是：

> 从今天开始，用一套更接近真实项目的结构把笔记 API 稳定地做下去。

---

## 今天的目标

今天只做一件事：

> 把项目正式切到 DRF 主线，并直接落成 `APIView + Serializer + service`。

今天结束后，你应该已经有这些东西：

- `rest_framework` 已接入
- `notes/serializers.py`
- `notes/services.py`
- `APIView` 版本的笔记列表、详情、创建接口
- `Response` 和 `request.data`

今天这份笔记的阅读方式也和之前不一样：

- 不是“先抄代码，能跑就行”
- 而是每一段代码都要知道“为什么这样写”
- 每个参数都要知道“它控制的到底是什么”

你后面看代码时，至少要能自己回答这 3 个问题：

1. 这行代码的数据从哪里来？
2. 这行代码为什么不用别的写法？
3. 这段代码执行完以后，最终完成了什么功能？

---

## 为什么今天不再把 `model.serialize` 当主线

因为你已经明确是要写项目，不是只做概念体验。

手写 `model.serialize` 或手写 `JsonResponse` 的价值只在于：

- 帮你理解接口返回本质上就是 Python 数据转 JSON
- 帮你理解“序列化”到底在解决什么问题

但真实项目里继续长期这么写，问题会很快出现：

- 输入校验散在 `views.py`
- 输出结构散在 `views.py`
- ORM 代码散在 `views.py`
- 代码一长就乱

所以 Day 8 以后，主项目默认就切到 DRF。

---

## 今天建议看的官方文档

- Quickstart  
  https://www.django-rest-framework.org/tutorial/quickstart/
- Serialization  
  https://www.django-rest-framework.org/tutorial/1-serialization/
- Class-based Views  
  https://www.django-rest-framework.org/tutorial/3-class-based-views/
- Serializers  
  https://www.django-rest-framework.org/api-guide/serializers/
- Views  
  https://www.django-rest-framework.org/api-guide/views/

今天重点看这 3 件事：

1. `Serializer`
2. `Request` / `Response`
3. `APIView`

---

## 今天的项目结构目标

今天结束后，你的 `notes` 目录建议长这样：

```text
notes/
├─ models.py
├─ serializers.py
├─ services.py
├─ views.py
└─ urls.py
```

这里有一个很重要的原则：

- `views.py` 不直接堆满 ORM
- `serializers.py` 不直接写业务流程
- `services.py` 不处理 HTTP 请求对象

---

## 任务 1：接入 DRF

### 1.1 安装

```powershell
pip install djangorestframework
```

### 1.2 修改 `INSTALLED_APPS`

在 `studynotes/settings.py` 中加入：

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "notes",
]
```

这一段代码的重点不是把每个 Django 内置 app 都背下来，而是看懂新增的两个配置：

- `"rest_framework"`
  作用：把 DRF 注册进当前 Django 项目。只有加进 `INSTALLED_APPS`，DRF 相关功能才会正常工作。
- `"notes"`
  作用：把你自己的业务 app 注册进项目，让 Django 知道要加载这里的模型、视图、管理后台等。

你可以先这样理解：

- `INSTALLED_APPS` 就是“这个项目要启用哪些应用模块”的总清单
- `rest_framework` 是你今天接进来的 API 框架
- `notes` 是你自己的业务代码

这段配置完成的功能是：

- 告诉 Django：从今天开始，这个项目正式启用 DRF，并继续启用 `notes` 这个业务 app。

---

## 任务 2：先把 `serializers.py` 建起来

今天不要追求把所有 serializer 一次写满，先把这 4 个建起来：

- `NoteListSerializer`
- `NoteDetailSerializer`
- `NoteCreateSerializer`
- `UserSummarySerializer`

推荐思路：

```python
from rest_framework import serializers

from .models import Comment, Note, Tag


class TagSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class CommentSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author_name", "content", "created_at"]


class NoteListSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    tags = TagSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "author",
            "status",
            "tags",
            "created_at",
            "updated_at",
        ]


class NoteDetailSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    tags = TagSimpleSerializer(many=True, read_only=True)
    comments = CommentSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = Note
        fields = [
            "id",
            "title",
            "content",
            "author",
            "status",
            "tags",
            "comments",
            "created_at",
            "updated_at",
        ]


class NoteCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    status = serializers.ChoiceField(
        choices=Note.STATUS_CHOICES,
        required=False,
        default=Note.STATUS_DRAFT,
    )
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
    )
```

下面把这段代码按块拆开讲。

### 2.1 `from rest_framework import serializers`

这行的意思是：

- 导入 DRF 里的序列化工具模块
- 后面你写的 `ModelSerializer`、`CharField`、`ChoiceField`、`ListField` 都来自这里

你可以先把它理解成：

- 这是 DRF 里专门负责“输入校验”和“输出结构”的工具入口

### 2.2 `from .models import Comment, Note, Tag`

这行的意思是：

- 从当前 app 的 `models.py` 里导入 3 个模型
- 后面的 serializer 要围绕这 3 个模型来写

这里的点在于：

- serializer 不是凭空写的
- 它要么描述模型对象怎么输出
- 要么描述前端输入应该长什么样

### 2.3 `class TagSimpleSerializer(serializers.ModelSerializer):`

这行里最重要的是 `ModelSerializer`。

它的意思是：

- 这个 serializer 主要是围绕 Django 模型来定义的
- DRF 可以根据模型字段帮你省掉很多重复工作

为什么 `Tag` 很简单：

- 因为 `Tag` 只有 `id`、`name` 这种很直接的字段
- 不涉及复杂关联展示

### 2.4 `class Meta:`

`Meta` 在这里的作用是：

- 告诉 DRF 这个 serializer 绑定哪个模型
- 告诉 DRF 要暴露哪些字段

### 2.5 `model = Tag`

意思是：

- 这个 serializer 对应的模型是 `Tag`

### 2.6 `fields = ["id", "name"]`

意思是：

- 最终输出时，只包含 `id` 和 `name`
- 其它字段即使模型里有，也不会自动暴露

这段 `TagSimpleSerializer` 完成的功能是：

- 把一个 `Tag` 模型对象转成只包含 `id` 和 `name` 的 JSON 结构

### 2.7 `CommentSimpleSerializer`

这一段和 `TagSimpleSerializer` 的思路完全一样。

```python
class CommentSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author_name", "content", "created_at"]
```

这里每个字段的意思是：

- `id`：评论自己的主键
- `author_name`：评论者名字
- `content`：评论内容
- `created_at`：评论创建时间

这段代码完成的功能是：

- 把一个 `Comment` 对象序列化成最基础的评论输出结构

### 2.8 `class NoteListSerializer(serializers.ModelSerializer):`

为什么到了 `NoteListSerializer` 就开始变复杂了？

因为 `Note` 模型不像 `Tag` 那么“平”。

`Note` 里有：

- `author`，它是外键，指向用户
- `tags`，它是多对多，指向多个标签

所以这里不能只靠最基础的模型字段自动映射，还要显式告诉 DRF：

- 作者怎么显示
- 标签怎么显示

### 2.9 `author = serializers.CharField(source="author.username", read_only=True)`

这一行可以拆成 3 部分：

- `author`
  这是最终返回给前端的字段名
- `serializers.CharField(...)`
  表示最终想把它表现成一个字符串字段
- `source="author.username"`
  表示这个字段的值，不是直接取 `note.author`，而是取 `note.author.username`

为什么要这样写：

- `note.author` 本身是一个用户对象，不是纯字符串
- 但列表接口里，我们通常只想让前端看到作者用户名

`read_only=True` 的意思是：

- 这个字段只负责输出
- 不负责接收前端输入来反向写入数据库

所以这一行完成的功能是：

- 把 `Note.author` 这个用户对象，转换成一个简单的作者名字符串输出给前端

### 2.10 `tags = TagSimpleSerializer(many=True, read_only=True)`

这一行也拆开看：

- `tags`
  最终返回给前端的字段名
- `TagSimpleSerializer(...)`
  表示每个标签对象都用你上面定义好的 `TagSimpleSerializer` 来序列化
- `many=True`
  表示这里不是单个对象，而是一组对象
- `read_only=True`
  表示这里只负责展示，不负责用它来接收前端写入数据

为什么这里不能简单写成一个普通字符串字段：

- 因为 `tags` 本身是多对多关系
- 它对应的是多个 `Tag` 对象

所以这一行完成的功能是：

- 把一篇笔记关联的多个标签，转换成标签对象列表输出给前端

### 2.11 `NoteListSerializer` 里的 `Meta`

```python
class Meta:
    model = Note
    fields = [
        "id",
        "title",
        "author",
        "status",
        "tags",
        "created_at",
        "updated_at",
    ]
```

这段的意思是：

- 当前 serializer 绑定的是 `Note` 模型
- 列表接口最终返回这几个字段

为什么列表接口不返回 `content`：

- 因为列表页通常更适合返回摘要型信息
- 详情接口再返回完整内容

这段 `NoteListSerializer` 完成的功能是：

- 让一条 `Note` 以“适合列表展示”的结构返回给前端

### 2.12 `NoteDetailSerializer`

这一段和 `NoteListSerializer` 很像，但比列表多了两类信息：

- `content`
- `comments`

```python
comments = CommentSimpleSerializer(many=True, read_only=True)
```

意思和前面的 `tags = TagSimpleSerializer(many=True, read_only=True)` 一样：

- `comments` 是一组评论对象
- 每个评论都交给 `CommentSimpleSerializer` 输出
- `many=True` 表示是多个
- `read_only=True` 表示这里只做读输出

所以 `NoteDetailSerializer` 完成的功能是：

- 让一条 `Note` 以“适合详情页展示”的完整结构返回给前端

### 2.13 `class NoteCreateSerializer(serializers.Serializer):`

这里为什么不用 `ModelSerializer`，而用普通 `Serializer`？

因为创建请求的输入结构，未必和模型字段一模一样。

比如：

- 前端传的是 `tag_ids`
- 但模型里实际是 `tags` 这个多对多关系

所以这里我们更关心的是：

- 前端输入长什么样
- 每个字段要怎么校验

### 2.14 `title = serializers.CharField(max_length=200)`

可以拆成：

- `title`
  字段名
- `serializers.CharField(...)`
  说明这是字符串字段
- `max_length=200`
  最长不能超过 200 个字符

这行完成的功能是：

- 要求前端必须传一个长度不超过 200 的标题字符串

### 2.15 `content = serializers.CharField()`

意思是：

- `content` 是字符串字段
- 前端创建笔记时要传内容

### 2.16 `status = serializers.ChoiceField(...)`

```python
status = serializers.ChoiceField(
    choices=Note.STATUS_CHOICES,
    required=False,
    default=Note.STATUS_DRAFT,
)
```

这里每个参数的意思是：

- `choices=Note.STATUS_CHOICES`
  说明这个字段只能从模型规定的状态选项里取值
- `required=False`
  说明这个字段不是必填
- `default=Note.STATUS_DRAFT`
  如果前端不传，就默认用草稿状态

这行完成的功能是：

- 让状态字段既有合法值约束，又允许不传时走默认值

### 2.17 `tag_ids = serializers.ListField(...)`

```python
tag_ids = serializers.ListField(
    child=serializers.IntegerField(min_value=1),
    required=False,
    default=list,
)
```

这里每个部分的意思是：

- `tag_ids`
  前端传进来的字段名
- `serializers.ListField(...)`
  表示这个字段整体是一个列表
- `child=serializers.IntegerField(min_value=1)`
  表示列表里的每一项都必须是大于等于 1 的整数
- `required=False`
  表示这个字段不是必传
- `default=list`
  表示如果前端没传，就默认给一个新的空列表 `[]`

为什么这里不直接写 `tag_ids: list[int] = []`：

- 因为 DRF 需要的是“字段对象”，不是单纯的 Python 类型提示
- `ListField` 才能让 DRF 真正做输入校验和错误提示

`NoteCreateSerializer` 这一整段代码完成的功能是：

- 规定“创建笔记时前端应该传什么”
- 校验这些输入是否合法
- 把合法输入整理成 `validated_data`

最后请你先固定一个理解：

- `ModelSerializer` 更像“围绕模型做输出”
- `Serializer` 更像“围绕请求格式做输入校验”

今天先记住一个原则：

- 读接口和写接口可以用不同 serializer

这不是重复，而是 API 设计里的正常分工。

---

## 任务 3：从第一天就把 ORM 抽到 `services.py`

既然你本来就想按真实项目写，那今天就直接这么做。

推荐最小版本：

```python
from .models import Note, Tag


def list_notes():
    return Note.objects.select_related("author").prefetch_related("tags").all()


def get_note_detail(*, note_id):
    return (
        Note.objects.select_related("author")
        .prefetch_related("tags", "comments")
        .get(pk=note_id)
    )


def create_note(*, author, validated_data):
    payload = dict(validated_data)
    tag_ids = payload.pop("tag_ids", [])

    note = Note.objects.create(author=author, **payload)
    if tag_ids:
        note.tags.set(Tag.objects.filter(id__in=tag_ids))

    return get_note_detail(note_id=note.pk)
```

下面把 `services.py` 这段代码逐段解释。

### 3.1 `from .models import Note, Tag`

这行的意思是：

- service 层要操作数据库
- 所以这里要导入对应的模型类

### 3.2 `def list_notes():`

这是一个没有参数的函数。

它的职责很单纯：

- 取出笔记列表

### 3.3 `Note.objects.select_related("author").prefetch_related("tags").all()`

这一句拆开看：

- `Note.objects`
  进入 `Note` 模型的 ORM 查询入口
- `select_related("author")`
  预先把外键 `author` 一起查出来，减少后面访问作者时的额外 SQL
- `prefetch_related("tags")`
  预先把多对多的 `tags` 一起查出来
- `.all()`
  取出所有符合条件的 `Note`

所以 `list_notes()` 完成的功能是：

- 取出一个已经做好作者和标签预加载优化的笔记列表

### 3.4 `def get_note_detail(*, note_id):`

这里最容易让人困惑的是 `*` 和 `note_id`。

- `note_id`
  表示你要查哪一条笔记
- `*`
  表示 `note_id` 必须使用关键字参数传入

也就是说，你要这样调用：

```python
get_note_detail(note_id=1)
```

而不是这样：

```python
get_note_detail(1)
```

这么写的好处是：

- 调用时更清楚
- 不容易把参数顺序弄错

### 3.5 `get(pk=note_id)`

这里的 `pk` 是 `primary key`，也就是主键。

在 `Note` 模型里，如果你没有自己定义主键字段，Django 会默认给它一个 `id`。

所以：

- `pk`
  就是当前 `Note` 自己的主键
- `note_id`
  是你传进来的那条笔记 id

这一句不是在查作者，而是在查：

- “主键等于 `note_id` 的那条 `Note`”

### 3.6 `prefetch_related("tags", "comments")`

这里为什么详情比列表多一个 `"comments"`：

- 因为详情页通常要把评论也一起带出来
- 所以提前把评论数据预加载，后面序列化时更省 SQL

所以 `get_note_detail()` 完成的功能是：

- 根据笔记 id 取出一条笔记详情，并预加载作者、标签和评论

### 3.7 `def create_note(*, author, validated_data):`

这个函数有两个关键参数：

- `author`
  当前登录用户，也就是这篇笔记真正的作者
- `validated_data`
  来自 serializer 校验后的安全输入数据

为什么 `author` 不让前端传：

- 因为作者身份应该来自当前登录用户
- 不能相信前端自己传一个作者 id

为什么 `validated_data` 很重要：

- 它不是原始请求体
- 而是已经通过 serializer 校验后的数据

### 3.8 `payload = dict(validated_data)`

这行的意思是：

- 把 `validated_data` 复制成一个普通字典

为什么要复制：

- 因为后面要对它做 `pop()`
- 不想直接修改原始的 `validated_data`

### 3.9 `tag_ids = payload.pop("tag_ids", [])`

这一行拆开看：

- `payload.pop("tag_ids", [])`
  从 `payload` 里把 `tag_ids` 拿出来
- 如果没有 `tag_ids`
  就给一个空列表 `[]`

为什么要单独拿出来：

- 因为 `Note.objects.create(...)` 不能直接处理多对多字段 id 列表
- 需要先创建 note，再单独设置标签关系

所以这行完成的功能是：

- 把“标签 id 列表”和“普通笔记字段”分开

### 3.10 `Note.objects.create(author=author, **payload)`

这一行里：

- `author=author`
  明确把当前登录用户写成这条 note 的作者
- `**payload`
  把字典里的其它字段，比如 `title`、`content`、`status`，展开传进去

如果 `payload` 是：

```python
{
    "title": "Django",
    "content": "serializer demo",
    "status": "draft",
}
```

那这一句大概等价于：

```python
Note.objects.create(
    author=author,
    title="Django",
    content="serializer demo",
    status="draft",
)
```

### 3.11 `note.tags.set(Tag.objects.filter(id__in=tag_ids))`

这句的作用是：

- 先用 `Tag.objects.filter(id__in=tag_ids)` 查出这些标签对象
- 再用 `note.tags.set(...)` 把它们设置到当前 note 的多对多关系上

这里的 `id__in=tag_ids` 意思是：

- 查询 id 在 `tag_ids` 列表里的所有 Tag

### 3.12 `return get_note_detail(note_id=note.pk)`

这一行的意思是：

- 不直接返回刚创建出来的 note 裸对象
- 而是重新走一遍详情查询，把作者、标签、评论这些关系都按详情接口需要的方式准备好

这里的 `note.pk`：

- 就是刚创建出来的这条 note 自己的主键

`create_note()` 这一整段代码完成的功能是：

- 用当前登录用户和校验后的输入数据创建一条新笔记
- 处理标签多对多关系
- 返回一条已经适合详情输出的完整 note 对象

这里的重点不是“service 这个名字是不是唯一标准”，而是：

- 让 `views.py` 不承担数据库细节
- 让 ORM 操作可以被复用和测试

---

## 任务 4：直接写 `APIView`

今天不再走 `@api_view` 过渡线，直接用 `APIView`。

推荐形态：

```python
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import NoteCreateSerializer, NoteDetailSerializer, NoteListSerializer
from .services import create_note, get_note_detail, list_notes


class NoteListAPIView(APIView):
    def get(self, request):
        notes = list_notes()
        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NoteDetailAPIView(APIView):
    def get(self, request, pk):
        note = get_note_detail(note_id=pk)
        serializer = NoteDetailSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NoteCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        note = create_note(
            author=request.user,
            validated_data=serializer.validated_data,
        )
        output = NoteDetailSerializer(note)
        return Response(output.data, status=status.HTTP_201_CREATED)
```

下面把 `APIView` 这段代码逐段拆开。

### 4.1 先看 4 个导入

```python
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
```

每一行的作用分别是：

- `status`
  DRF 提供的状态码常量工具，比如 `HTTP_200_OK`、`HTTP_201_CREATED`
- `IsAuthenticated`
  一个权限类，表示“只有登录用户才能访问”
- `Response`
  DRF 的响应对象，比 Django 原生 `JsonResponse` 更适合配合 serializer 使用
- `APIView`
  DRF 的类视图基类，你写 API 类时从它继承

### 4.2 `class NoteListAPIView(APIView):`

这行的意思是：

- 定义一个类视图
- 这个类负责处理“笔记列表接口”
- 因为继承了 `APIView`，所以它会进入 DRF 的请求响应体系

### 4.3 `def get(self, request):`

这里两个参数要分清：

- `self`
  当前这个视图类的实例对象
- `request`
  DRF 包装后的请求对象

为什么方法名叫 `get`：

- 因为它对应 HTTP GET 请求

### 4.4 `notes = list_notes()`

这行的意思是：

- 调用 service 层获取笔记列表
- view 不直接自己写 ORM

### 4.5 `serializer = NoteListSerializer(notes, many=True)`

这里最重要的是两个点：

- `NoteListSerializer(notes, ...)`
  表示用 `NoteListSerializer` 去序列化这些 note 对象
- `many=True`
  表示传进去的是“多个对象”，不是单个对象

如果你不写 `many=True`：

- DRF 会以为你传的是单个对象
- 会报错

### 4.6 `return Response(serializer.data, status=status.HTTP_200_OK)`

这一行可以拆成：

- `serializer.data`
  序列化后的输出数据
- `Response(...)`
  用 DRF 的响应对象返回给客户端
- `status=status.HTTP_200_OK`
  指定返回状态码 200，表示请求成功

所以 `NoteListAPIView` 完成的功能是：

- 收到 GET 请求后，返回一组按列表结构序列化好的笔记数据

### 4.7 `class NoteDetailAPIView(APIView):`

这个类负责：

- 单条笔记详情接口

### 4.8 `def get(self, request, pk):`

这里多了一个 `pk` 参数。

它的来源是路由里的：

```python
<int:pk>
```

意思是：

- 路由会把 URL 里的整数部分取出来
- 作为 `pk` 传给这个方法

### 4.9 `note = get_note_detail(note_id=pk)`

这行的意思是：

- 把路由里传进来的主键 `pk`
- 用关键字参数 `note_id=pk` 交给 service 层
- 去查询对应的详情对象

### 4.10 `serializer = NoteDetailSerializer(note)`

这里没有 `many=True`，因为：

- 这里处理的是单个 note 对象

`NoteDetailAPIView` 整段代码完成的功能是：

- 根据 URL 里的笔记 id，返回单条笔记的详情数据

### 4.11 `class NoteCreateAPIView(APIView):`

这个类负责：

- 创建笔记接口

### 4.12 `permission_classes = [IsAuthenticated]`

这里的 `permission_classes` 是 `APIView` 的类属性。

意思是：

- 这个接口使用哪些权限规则

`[IsAuthenticated]` 表示：

- 只有已经登录的用户，才能访问这个接口

为什么写成列表：

- 因为一个接口可以挂多个权限类

### 4.13 `def post(self, request):`

这里的方法名是 `post`，因为：

- 它对应 HTTP POST 请求

这个方法就是“创建动作”的入口。

### 4.14 `serializer = NoteCreateSerializer(data=request.data)`

这一行非常关键。

可以拆成：

- `NoteCreateSerializer(...)`
  使用你前面定义的创建输入 serializer
- `data=request.data`
  说明现在不是在“序列化模型对象输出”，而是在“校验前端输入数据”

这里的 `data=` 参数是什么意思：

- 告诉 serializer：我要拿这份原始输入数据做校验

这里的 `request.data` 是什么：

- DRF 帮你解析后的请求体数据
- 通常就是前端传来的 JSON

这一行完成的功能是：

- 准备开始校验“创建笔记”请求体

### 4.15 `serializer.is_valid(raise_exception=True)`

这行也是 DRF 的核心写法。

拆开看：

- `is_valid()`
  执行 serializer 校验
- `raise_exception=True`
  如果校验失败，直接抛出异常，让 DRF 自动返回标准错误响应

为什么推荐这样写，而不是手动 `if not serializer.is_valid()`：

- 代码更短
- 错误处理更统一

这一行完成的功能是：

- 确保前端传来的创建数据已经合法

### 4.16 `note = create_note(author=request.user, validated_data=serializer.validated_data)`

这是你刚刚问到的重点，这里单独拆得更细一点。

#### `create_note(...)`

表示：

- 调用 service 层真正执行创建逻辑

#### `author=request.user`

这里：

- 参数名 `author`
  是 `create_note()` 这个函数定义里要求的参数名
- 参数值 `request.user`
  是当前登录用户对象

为什么这里一定要传 `request.user`：

- 因为作者身份应该来自当前登录用户
- 不能让前端自己传“我是哪个作者”

也就是说，这个参数完成的功能是：

- 明确告诉 service 层：这篇笔记是谁创建的

#### `validated_data=serializer.validated_data`

这里也拆两部分：

- 参数名 `validated_data`
  是 `create_note()` 函数里定义的参数名
- 参数值 `serializer.validated_data`
  是 serializer 校验通过后的数据字典

为什么不是直接传 `request.data`：

- 因为 `request.data` 只是原始输入
- `serializer.validated_data` 才是已经过校验、可以安全进入业务层的数据

这个参数完成的功能是：

- 把“已经验证过的创建数据”交给 service 层

所以这一整行：

```python
note = create_note(
    author=request.user,
    validated_data=serializer.validated_data,
)
```

完成的事情是：

- 把“当前登录用户”和“校验通过的请求数据”一起交给 service 层
- 让 service 层真正创建出一条 note

### 4.17 `output = NoteDetailSerializer(note)`

这一行的意思是：

- 创建成功后，不再用创建 serializer 作为输出
- 而是换成详情 serializer，把新建出来的 note 转成完整详情结构

为什么要这样做：

- 输入 serializer 和输出 serializer 的职责本来就可以不同
- 创建接口成功后，通常希望把更完整的对象信息返回给前端

### 4.18 `return Response(output.data, status=status.HTTP_201_CREATED)`

拆开看：

- `output.data`
  是详情 serializer 产出的 JSON 数据
- `Response(...)`
  返回给前端
- `status=status.HTTP_201_CREATED`
  状态码 201，表示“资源创建成功”

`NoteCreateAPIView` 这一整段代码完成的功能是：

- 只允许登录用户访问
- 校验前端创建请求
- 用当前登录用户作为作者
- 调用 service 创建 note
- 最后把新创建的 note 详情数据返回给前端

这就是这 7 天要一直延续的主线风格。

---

## 任务 5：只保留一套主路由

今天建议直接让主接口进入 DRF 风格，不要为了“对照学习”长期留三四套路由。

推荐：

```python
path("api/notes/", views.NoteListAPIView.as_view(), name="note-list"),
path("api/notes/<int:pk>/", views.NoteDetailAPIView.as_view(), name="note-detail"),
path("api/notes/create/", views.NoteCreateAPIView.as_view(), name="note-create"),
```

这 3 行路由也顺手解释一下。

### 5.1 `path(...)`

`path()` 是 Django 的路由函数。

它的基本结构是：

```python
path(路径, 视图, 路由名)
```

### 5.2 `views.NoteListAPIView.as_view()`

这里为什么不是直接写类名，而是 `.as_view()`：

- 因为 Django 路由系统最终需要的是一个可调用视图函数
- `APIView` 是类
- `.as_view()` 会把这个类转换成 Django 能识别的视图入口

### 5.3 `path("api/notes/<int:pk>/", ...)`

这里的 `<int:pk>` 意思是：

- URL 里这里接收一个整数
- 参数名叫 `pk`
- 最后会把这个值传给视图方法里的 `pk`

例如访问：

```text
/api/notes/3/
```

那视图里的 `pk` 就会等于 `3`。

### 5.4 `name="note-list"` 这类名字有什么用

`name` 的作用是：

- 给这个路由起一个可反向查找的名字
- 后面在测试、模板或其它地方可以按名字找路由

这几行路由完成的功能是：

- 把“笔记列表”“笔记详情”“创建笔记”这 3 个 APIView 正式挂到 URL 上，让前端或测试工具可以访问。

学习可以对照，但项目代码不要长期并存很多等价版本。

---

## 补充知识：`model.serialize` 和 `JsonResponse` 还有没有意义

有，但意义已经变了。

现在它们的角色应该是：

- 帮你理解底层原理
- 帮你在极简单场景下快速验证数据
- 帮你理解 DRF 到底替你省掉了哪些事

而不是：

- 作为这个项目后续 7 天的主线写法

你可以单独记一句：

> 手写序列化是基础知识，Serializer 才是项目主线。

---

## 今天不做什么

今天先不要做这些事：

- 不做 `ViewSet`
- 不做 `Router`
- 不做 `GenericAPIView`
- 不做复杂分页和过滤
- 不保留多套等价实现互相对照

今天最重要的是把主线定住。

---

## 今天的交付标准

- [ ] 安装并接入 DRF
- [ ] 新建 `notes/serializers.py`
- [ ] 新建 `notes/services.py`
- [ ] 用 `APIView` 实现列表接口
- [ ] 用 `APIView` 实现详情接口
- [ ] 用 `APIView` 实现创建接口
- [ ] 在创建接口中用上 `request.data`
- [ ] 在创建接口中用上 `serializer.is_valid(raise_exception=True)`
- [ ] 让 `views.py` 不直接堆 ORM 创建逻辑

---

## 今日复盘问题

1. 为什么从 Day 8 开始就直接上 `APIView`，而不是先走 `@api_view`？
2. 为什么这个阶段要提前建立 `service` 层，而不是把 ORM 全塞在 `views.py`？
3. 为什么 `Serializer` 应该成为项目主线，而不是手写 `model.serialize`？
4. `request.data` 和 `request.body` 的角色差异是什么？

---

## 一句总结

今天不是“体验 DRF 一下”，而是：

> 正式把项目切到 `APIView + Serializer + service` 这条后面 6 天都不会推翻的主线上。
