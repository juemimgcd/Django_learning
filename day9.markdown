# Day 9 任务清单：学会 `ModelSerializer`、校验流程和 `APIView`

## 今天的目标

昨天你已经把 DRF 接进来了，也已经体验到这些变化：

- 不用自己手写 `JsonResponse`
- 不用自己手动 `json.loads(request.body)`
- 可以通过 `Serializer` 管理输入和输出

但昨天更像是“先跑通第一遍”。  
今天我们要真正进入 DRF 的核心工作流，把几个最关键的东西彻底弄明白：

> 数据是怎么从请求进来，被校验，被转换，最后再被保存并返回的？

今天学完后，你应该能做到：

- 理解 `Serializer` 和 `ModelSerializer` 的区别
- 看懂 `serializer.is_valid()`、`serializer.validated_data`、`serializer.save()`
- 区分“请求序列化器”和“响应序列化器”
- 用 `APIView` 重写昨天的函数式 DRF 接口
- 知道为什么 DRF 的类视图比你自己写很多 `if request.method == ...` 更清晰

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 50 分钟 | 看 `Serializer`、`ModelSerializer`、Class-based Views |
| 理解校验链路 | 40 分钟 | 把 `is_valid()` 到 `save()` 的流程看明白 |
| 核心编码 | 120 分钟 | 新建/改造序列化器，改写成 `APIView` |
| 联调复盘 | 50 分钟 | 用接口测试工具验证输入输出和报错格式 |

---

## 今天的官方文档入口

- 教程 1：Serialization  
  https://www.django-rest-framework.org/tutorial/1-serialization/
- 教程 3：Class-based views  
  https://www.django-rest-framework.org/tutorial/3-class-based-views/
- Serializer API Guide  
  https://www.django-rest-framework.org/api-guide/serializers/
- Views API Guide  
  https://www.django-rest-framework.org/api-guide/views/

建议阅读顺序：

1. 先回看 `Serialization`
2. 再看 `Class-based views`
3. 编码时回查 `Serializer API Guide`

---

## 先把今天最重要的结论说清楚

如果用你熟悉的 FastAPI 思路来类比，今天学的核心大概是这件事：

- FastAPI 里：`Pydantic schema` 既负责校验，也负责结构描述
- DRF 里：`Serializer` 承担了类似角色

而 `APIView` 的意义是：

- 把“不同 HTTP 方法的处理逻辑”分开写
- 让代码结构更接近真正的 API 设计

所以今天本质上是在做两件事：

1. 把“数据结构”交给 `Serializer`
2. 把“请求方法分发”交给 `APIView`

---

## 你今天必须理解的 6 个概念

## 1. `Serializer` 不等于 `ModelSerializer`

`Serializer` 是完全手写字段的。

比如：

```python
class NoteCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    status = serializers.ChoiceField(choices=Note.STATUS_CHOICES, required=False)
```

优点：

- 非常灵活
- 适合请求体校验
- 不会把模型字段一股脑暴露出去

`ModelSerializer` 是根据模型自动生成很多字段的。

比如：

```python
class NoteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "status", "created_at", "updated_at"]
```

优点：

- 写得少
- 适合模型型接口
- 很适合做标准 CRUD

今天的建议是：

- 请求体：先保留 `Serializer`
- 响应体：开始引入 `ModelSerializer`

这样你更容易理解职责边界。

---

## 2. `serializer = XxxSerializer(data=request.data)` 是“反序列化入口”

这一句不是“把对象转成 JSON”，而是：

- 接收用户传进来的原始数据
- 准备做校验

例如：

```python
serializer = NoteCreateSerializer(data=request.data)
```

这里的意思是：

- `request.data` 是客户端发来的内容
- 现在交给 `NoteCreateSerializer` 检查是否合法

---

## 3. `serializer.is_valid()` 才会真正触发校验

只有调用了：

```python
serializer.is_valid()
```

DRF 才会去检查：

- 字段是否缺失
- 类型是否正确
- 长度是否超限
- 枚举值是否在允许范围内
- 你自定义的校验规则是否通过

常见写法：

```python
if serializer.is_valid():
    ...
else:
    return Response(serializer.errors, status=400)
```

更常见的工程化写法是：

```python
serializer.is_valid(raise_exception=True)
```

好处：

- 少写一层 `if`
- DRF 会自动抛出异常并生成标准错误响应

这也是你后面会越来越喜欢 DRF 的原因之一。

---

## 4. `validated_data` 才是“可信数据”

很多初学者容易写成这样：

```python
title = request.data.get("title")
```

这虽然能取到值，但这时它还没经过完整校验。  
更规范的做法是：

```python
serializer.is_valid(raise_exception=True)
title = serializer.validated_data["title"]
```

你可以把它理解成：

- `request.data` 是原始输入
- `validated_data` 是校验后的安全结果

---

## 5. `save()` 不是魔法，它会调用 `create()` 或 `update()`

很多人第一次接触 DRF 会觉得：

```python
serializer.save()
```

为什么一句话就能保存？

背后逻辑其实是：

- 如果当前是新建数据，就调用 `create()`
- 如果当前是更新数据，就调用 `update()`

比如：

```python
serializer = NoteCreateSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
note = serializer.save(author=request.user)
```

这时 `author=request.user` 这种“额外注入字段”非常常见。  
因为作者不应该来自前端，而应该来自当前登录用户。

---

## 6. `APIView` 是 DRF 的类视图基础层

如果你现在还在写：

```python
@api_view(["GET", "POST"])
def drf_note_list(request):
    ...
```

那它已经比原生 Django 更舒服了。  
但当接口越来越多时，你会开始更想要：

```python
class NoteListCreateAPIView(APIView):
    def get(self, request):
        ...

    def post(self, request):
        ...
```

原因很简单：

- `GET`、`POST` 分开写更清晰
- 后续挂权限、认证、分页更自然
- 代码组织更像真正的 API 类

---

## 今天的项目任务

今天我们要把当前项目里的 DRF 接口升级一层：

1. 在 `notes/serializers.py` 中引入 `ModelSerializer`
2. 分离列表、详情、创建、更新这几种不同用途的序列化器
3. 在 `notes/views.py` 中新增 `APIView` 版本接口
4. 在 `notes/urls.py` 中挂上新的 DRF 类视图路由
5. 用接口测试验证校验错误、创建成功、更新成功和权限行为

建议今天继续保留昨天写的函数式 DRF 视图，不要删。  
我们今天是“升级”，不是“推倒重来”。

---

## 建议先改造 `serializers.py`

今天你可以把序列化器拆成下面几类：

## 1. 标签简版序列化器

```python
from rest_framework import serializers
from .models import Note, Tag, Comment


class TagSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]
```

## 2. 评论简版序列化器

```python
class CommentSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "author_name", "content", "created_at"]
```

## 3. 笔记列表响应序列化器

```python
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
```

## 4. 笔记详情响应序列化器

```python
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
```

## 5. 创建/更新请求序列化器

```python
class NoteWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    status = serializers.ChoiceField(choices=Note.STATUS_CHOICES, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
    )

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("标题不能为空。")
        return value

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("内容不能为空。")
        return value
```

---

## 再往前一步：给写入序列化器补 `create()` 和 `update()`

如果你想更完整地用 `serializer.save()`，可以直接写：

```python
class NoteWriteSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    content = serializers.CharField()
    status = serializers.ChoiceField(choices=Note.STATUS_CHOICES, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        allow_empty=True,
    )

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("标题不能为空。")
        return value

    def validate_content(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("内容不能为空。")
        return value

    def create(self, validated_data):
        tag_ids = validated_data.pop("tag_ids", [])
        author = self.context["author"]

        note = Note.objects.create(author=author, **validated_data)
        if tag_ids:
            note.tags.set(Tag.objects.filter(id__in=tag_ids))
        return note

    def update(self, instance, validated_data):
        tag_ids = validated_data.pop("tag_ids", None)

        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.status = validated_data.get("status", instance.status)
        instance.save()

        if tag_ids is not None:
            instance.tags.set(Tag.objects.filter(id__in=tag_ids))

        return instance
```

这里的关键点是：

- `context` 可以把视图层信息传给序列化器
- `author` 不从前端来，而是从 `request.user` 注入

---

## 今天开始改写成 `APIView`

在 `notes/views.py` 中新增一组类视图。

## 1. 列表 + 创建

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Note
from .serializers import (
    NoteListSerializer,
    NoteDetailSerializer,
    NoteWriteSerializer,
)


class DrfNoteListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        queryset = Note.objects.select_related("author").prefetch_related("tags").all()
        serializer = NoteListSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NoteWriteSerializer(
            data=request.data,
            context={"author": request.user},
        )
        serializer.is_valid(raise_exception=True)
        note = serializer.save()
        output = NoteDetailSerializer(note)
        return Response(output.data, status=status.HTTP_201_CREATED)
```

这段代码里很值得你注意的点有 3 个：

1. `permission_classes` 已经开始接管权限
2. `is_valid(raise_exception=True)` 会自动生成标准报错
3. 创建成功后可以用另一个响应序列化器返回更完整的数据

## 2. 详情 + 更新 + 删除

```python
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated


class DrfNoteDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(
            Note.objects.select_related("author").prefetch_related("tags", "comments"),
            pk=pk,
        )

    def get(self, request, pk):
        note = self.get_object(pk)
        serializer = NoteDetailSerializer(note)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=401)

        note = self.get_object(pk)
        if note.author_id != request.user.id:
            return Response({"detail": "You do not have permission to perform this action."}, status=403)

        serializer = NoteWriteSerializer(note, data=request.data, context={"author": request.user})
        serializer.is_valid(raise_exception=True)
        note = serializer.save()
        output = NoteDetailSerializer(note)
        return Response(output.data)

    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=401)

        note = self.get_object(pk)
        if note.author_id != request.user.id:
            return Response({"detail": "You do not have permission to perform this action."}, status=403)

        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

今天先允许你在 `put()`、`delete()` 里手动做作者校验。  
明天和后天我们会把这件事做得更“DRF 原生”。

---

## 路由建议

在 `notes/urls.py` 中新增：

```python
path("drf/v2/notes/", views.DrfNoteListCreateAPIView.as_view(), name="drf-note-list-create"),
path("drf/v2/notes/<int:pk>/", views.DrfNoteDetailAPIView.as_view(), name="drf-note-detail"),
```

为什么建议加一个 `/drf/v2/`？

因为你现在项目里已经有：

- 原生 Django `/api/...`
- Day 8 的 DRF 函数式 `/drf/...`

今天再加一组 `APIView`，最好让版本层次清晰一点。  
这样你回头看，会非常容易比较不同实现方式。

---

## 今天推荐你主动观察的 5 个现象

## 1. 不合法输入的错误格式更统一了

比如标题不传：

```json
{
  "title": ["This field is required."]
}
```

或者你自定义中文错误：

```json
{
  "title": ["标题不能为空。"]
}
```

这比你手写 `{"error": "xxx"}` 更容易扩展。

## 2. 视图里的“参数提取代码”明显减少了

你不再需要自己写：

- `parse_json_body`
- `payload.get("title")`
- `payload.get("content")`

这些工作越来越多交给了序列化器。

## 3. `APIView` 比函数视图更适合继续扩展

后面你要接：

- 权限类
- 认证类
- 分页
- 过滤
- 自定义异常处理

类视图会比函数视图更舒服。

## 4. 响应结构开始变得“可组合”

你可以：

- 列表用 `NoteListSerializer`
- 详情用 `NoteDetailSerializer`
- 写入用 `NoteWriteSerializer`

这就是 API 工程化很重要的一步。

## 5. 你会开始理解“一个模型可以对应多个序列化器”

这一点和你以前在 FastAPI 里写：

- `RegisterRequest`
- `UserResponse`
- `UserDetailResponse`

是很像的。

---

## 今天怎么测试

继续启动服务：

```powershell
python manage.py runserver
```

### 1. 测试列表接口

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v2/notes/" -Method Get
```

### 2. 测试未登录创建

```powershell
$body = @{
    title = "DRF Day 9"
    content = "测试 APIView 创建接口"
    status = "draft"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v2/notes/" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

看返回是不是标准认证错误。

### 3. 登录后再创建

如果你前面已经做了 Session 登录接口，可以先登录拿会话。  
或者今天先用 Django Admin 创建一些数据，重点观察 DRF 返回结构。

### 4. 测试非法字段

比如不传标题、传空标题、传错误状态值，观察 `serializer.errors` 的返回格式。

---

## 今天的易错点

## 1. 忘记区分 `data=` 和 `instance`

创建：

```python
serializer = NoteWriteSerializer(data=request.data)
```

更新：

```python
serializer = NoteWriteSerializer(note, data=request.data)
```

别把这两种写反。

## 2. 忘了 `many=True`

序列化列表数据时要写：

```python
serializer = NoteListSerializer(queryset, many=True)
```

否则会报错。

## 3. 把 `validated_data` 和 `serializer.data` 混掉

先记住：

- `validated_data`：校验后的输入
- `serializer.data`：最终输出给客户端的数据

## 4. `create()` 里直接信任 `author` 来自前端

不要这样做。  
作者必须来自：

- `request.user`
- 或者 `serializer.save(author=request.user)`

而不是来自前端 body。

## 5. 更新时没处理标签关系

如果你有 `tag_ids`，更新时要想清楚：

- 是全部替换
- 还是追加

今天建议先做“全部替换”，最清晰。

---

## 今天结束后的验收标准

- 你能说清楚 `Serializer` 和 `ModelSerializer` 的区别
- 你能解释 `is_valid()`、`validated_data`、`save()` 的关系
- 你能用 `APIView` 写出 `GET`、`POST`、`PUT`、`DELETE`
- 你能把“写请求体校验”和“写响应结构”分开理解
- 你能看懂为什么 DRF 开始越来越像一个真正的 API 框架

---

## 今天的复盘问题

学习结束后，建议你写下这 3 个问题的答案：

1. 为什么 DRF 里同一个 `Note` 会有多个序列化器？
2. 为什么 `serializer.is_valid(raise_exception=True)` 比自己写很多 `if` 更舒服？
3. 和原生 Django API 相比，今天的 `APIView` 最大的提升是什么？

---

## 明天会学什么

明天我们继续往 DRF 的“省代码能力”推进：  
你会学到：

- `GenericAPIView`
- `mixins`
- `ListCreateAPIView`
- `RetrieveUpdateDestroyAPIView`

也就是说，明天会开始进入：

> “连 `APIView` 里的很多重复代码都不用自己写了。”

这一天学完后，你会更清楚 DRF 为什么很适合做标准 CRUD API。
