# Day 9 任务清单：补全 CRUD，固定 `Serializer + service + APIView` 分工

## 这一阶段的主线不变

今天继续沿用昨天定下来的结构：

- `APIView` 处理 HTTP 请求和响应
- `Serializer` 负责输入校验和输出结构
- `service` 负责 ORM 和事务

今天不是换一套写法，而是把昨天的主线补完整。

也就是说，Day 8 是：

- 先把 DRF 主线搭起来

Day 9 是：

- 在不推翻 Day 8 的前提下，把这条主线补成真正可用的基础 CRUD

---

## 今天的目标

把笔记接口从“能查、能看、能创建”补成真正的基础 CRUD：

- 列表
- 详情
- 创建
- 更新
- 删除

同时把几个项目里非常重要的概念固定下来：

- `validated_data`
- `serializer.is_valid(raise_exception=True)`
- 读写分离的 serializer
- `transaction.atomic`
- `partial=True`

---

## 今天这份笔记怎么读

今天和 Day 8 一样，不是只贴一段代码就结束。

今天你需要继续训练这种阅读方式：

1. 先看这段代码要解决什么问题
2. 再看每一行代码在做什么
3. 再看每个参数为什么这样写
4. 最后总结这段代码完成了什么功能

你后面自己写 CRUD 时，也应该按这个逻辑去想，而不是“先抄一段差不多的代码”。

---

## 为什么今天继续坚持同一套结构

因为真实项目里最怕的不是“代码一开始不完美”，而是：

- 昨天一套组织方式
- 今天整套推翻
- 明天再来一次

这会让学习和项目同时变得低效。

所以今天的原则很简单：

> 只在昨天的主线基础上加能力，不改主架构。

---

## 今天建议看的官方文档

- Serializers  
  https://www.django-rest-framework.org/api-guide/serializers/
- Views  
  https://www.django-rest-framework.org/api-guide/views/
- Status codes  
  https://www.django-rest-framework.org/api-guide/status-codes/

今天重点看：

1. `is_valid()`
2. `validated_data`
3. `raise_exception=True`
4. `partial=True`
5. `create()` / `update()` 这两个词在 DRF 里的含义

---

## 今天的项目目录建议

```text
notes/
├─ models.py
├─ serializers.py
├─ services.py
├─ views.py
├─ urls.py
└─ tests.py
```

今天主要改 4 个文件：

- `serializers.py`
- `services.py`
- `views.py`
- `tests.py`

---

## 任务 1：把 serializer 拆清楚

今天建议把 `Note` 相关 serializer 固定成这几类：

- `NoteListSerializer`
- `NoteDetailSerializer`
- `NoteCreateSerializer`
- `NoteUpdateSerializer`

如果列表接口要支持查询参数，也可以今天先加一个：

- `NoteListQuerySerializer`

推荐方向：

```python
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


class NoteUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, required=False)
    content = serializers.CharField(required=False)
    status = serializers.ChoiceField(choices=Note.STATUS_CHOICES, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
    )
```

下面把这段代码拆开讲。

### 1.1 为什么创建和更新要分两个 serializer

因为“创建”和“更新”在输入规则上并不完全一样。

创建时通常意味着：

- 一些核心字段应该传进来

更新时通常意味着：

- 只更新一部分字段也可以

所以虽然两个接口都和 `Note` 有关，但它们的输入契约不一定相同。

这就是为什么今天我们开始固定一个认知：

- 列表和详情是“读 serializer”
- 创建和更新是“写 serializer”

---

### 1.2 `class NoteCreateSerializer(serializers.Serializer):`

这里用的是普通 `Serializer`，不是 `ModelSerializer`。

原因是：

- 这里更关注“前端传什么”
- 而不是简单把模型字段原样暴露出去

比如：

- 前端传的是 `tag_ids`
- 但模型里实际是 `tags` 这个多对多关系

所以这里更适合用普通 `Serializer` 显式声明输入格式。

---

### 1.3 `title = serializers.CharField(max_length=200)`

这一行的意思是：

- `title`
  输入字段名
- `serializers.CharField(...)`
  表示它必须是字符串
- `max_length=200`
  最长 200 个字符

它完成的功能是：

- 规定“创建笔记时，标题必须是一个不超过 200 字符的字符串”

---

### 1.4 `content = serializers.CharField()`

这一行的意思是：

- `content` 是一个字符串字段

它完成的功能是：

- 规定“创建笔记时，要传内容字段，并且内容是字符串”

---

### 1.5 `status = serializers.ChoiceField(...)`

```python
status = serializers.ChoiceField(
    choices=Note.STATUS_CHOICES,
    required=False,
    default=Note.STATUS_DRAFT,
)
```

这里每个参数的意思是：

- `choices=Note.STATUS_CHOICES`
  说明这个字段只能从 `Note` 模型定义好的状态选项里选
- `required=False`
  说明前端可以不传这个字段
- `default=Note.STATUS_DRAFT`
  如果前端不传，就默认设为草稿状态

这行代码完成的功能是：

- 让 `status` 既有合法值范围，又支持默认值

---

### 1.6 `tag_ids = serializers.ListField(...)`

```python
tag_ids = serializers.ListField(
    child=serializers.IntegerField(min_value=1),
    required=False,
    default=list,
)
```

这里每一部分的意思是：

- `tag_ids`
  前端传进来的字段名
- `serializers.ListField(...)`
  说明这个字段整体是一个列表
- `child=serializers.IntegerField(min_value=1)`
  说明列表里的每一项都必须是大于等于 1 的整数
- `required=False`
  不传也可以
- `default=list`
  不传时默认生成一个新的空列表 `[]`

这行代码完成的功能是：

- 允许前端传一组标签 id，用来表示“创建这条 note 时要绑定哪些标签”

---

### 1.7 `class NoteUpdateSerializer(serializers.Serializer):`

这个 serializer 和创建版的最大区别是：

- 更新通常允许“只改一部分”

所以这里很多字段都写成了：

- `required=False`

这表示：

- 这个字段在更新请求里可以不出现

---

### 1.8 `title = serializers.CharField(max_length=200, required=False)`

这行的意思是：

- `title` 如果传了，必须是长度不超过 200 的字符串
- 但它不是必传项

所以它适合“部分更新”场景。

---

### 1.9 `content = serializers.CharField(required=False)`

意思是：

- `content` 如果传了，必须是字符串
- 但可以不传

---

### 1.10 `status = serializers.ChoiceField(..., required=False)`

意思是：

- 如果前端传了状态，就必须是合法状态
- 但更新时可以只改别的字段，不改状态

---

### 1.11 更新版里的 `tag_ids`

```python
tag_ids = serializers.ListField(
    child=serializers.IntegerField(min_value=1),
    required=False,
)
```

这里和创建版的区别在于：

- 它没有写 `default=list`

为什么？

因为更新时：

- “不传 `tag_ids`” 和 “传空列表 `[]`” 语义不同

这两个场景要分开理解：

- 不传 `tag_ids`
  表示“这次更新不动标签”
- 传 `tag_ids=[]`
  表示“这次明确要把标签清空”

如果这里也默认 `[]`，那你就分不清“没传”和“要清空标签”了。

这就是为什么更新 serializer 里，`tag_ids` 通常只写：

- `required=False`

而不写默认空列表。

---

### 1.12 这一整段 serializer 代码完成了什么功能

它完成了 3 件事：

1. 把“创建输入”和“更新输入”分开定义清楚
2. 让每个字段都有明确的校验规则
3. 让后面的 `view` 和 `service` 可以放心地使用 `validated_data`

今天先固定一个非常重要的认知：

> 创建和更新虽然都操作同一个模型，但输入规则并不一定相同，所以完全可以用不同 serializer。

---

## 任务 2：把 service 层补完整

今天建议把 `services.py` 补成这几个动作：

- `list_notes`
- `get_note`
- `get_note_detail`
- `create_note`
- `update_note`
- `delete_note`

推荐思路：

```python
from django.db import transaction

from .models import Note, Tag


def list_notes():
    return Note.objects.select_related("author").prefetch_related("tags").all()


def get_note(*, note_id):
    return (
        Note.objects.select_related("author")
        .prefetch_related("tags")
        .get(pk=note_id)
    )


def get_note_detail(*, note_id):
    return (
        Note.objects.select_related("author")
        .prefetch_related("tags", "comments")
        .get(pk=note_id)
    )


@transaction.atomic
def create_note(*, author, validated_data):
    payload = dict(validated_data)
    tag_ids = payload.pop("tag_ids", [])

    note = Note.objects.create(author=author, **payload)
    if tag_ids:
        note.tags.set(Tag.objects.filter(id__in=tag_ids))

    return get_note_detail(note_id=note.pk)


@transaction.atomic
def update_note(*, note, validated_data):
    payload = dict(validated_data)
    tag_ids = payload.pop("tag_ids", None)

    for field, value in payload.items():
        setattr(note, field, value)
    note.save()

    if tag_ids is not None:
        note.tags.set(Tag.objects.filter(id__in=tag_ids))

    return get_note_detail(note_id=note.pk)


def delete_note(*, note):
    note.delete()
```

下面按函数逐个拆开。

### 2.1 `from django.db import transaction`

这一行的作用是：

- 导入 Django 的事务工具

后面会用到：

- `@transaction.atomic`

它的作用是：

- 把一组数据库操作包成一个整体
- 要么一起成功
- 要么中途出错时一起回滚

---

### 2.2 `list_notes()`

```python
def list_notes():
    return Note.objects.select_related("author").prefetch_related("tags").all()
```

这段代码拆开看：

- `Note.objects`
  进入 `Note` 的 ORM 查询入口
- `select_related("author")`
  提前把外键作者查出来
- `prefetch_related("tags")`
  提前把多对多标签查出来
- `.all()`
  取出全部笔记

它完成的功能是：

- 返回一个已经预加载作者和标签的笔记列表

---

### 2.3 `get_note(*, note_id)`

```python
def get_note(*, note_id):
    return (
        Note.objects.select_related("author")
        .prefetch_related("tags")
        .get(pk=note_id)
    )
```

这里要注意两点：

- `note_id`
  是你要查找的那条笔记的 id
- `*`
  表示这个参数必须用关键字方式传入

也就是要这样调用：

```python
get_note(note_id=3)
```

而不是：

```python
get_note(3)
```

`get(pk=note_id)` 的意思是：

- 查找主键等于 `note_id` 的这条 `Note`

它完成的功能是：

- 返回一条适合更新、删除等场景使用的 note 对象

---

### 2.4 `get_note_detail(*, note_id)`

```python
def get_note_detail(*, note_id):
    return (
        Note.objects.select_related("author")
        .prefetch_related("tags", "comments")
        .get(pk=note_id)
    )
```

它和 `get_note()` 的区别是：

- 多预加载了 `comments`

为什么：

- 详情接口通常要把评论一起返回
- 更新和删除场景通常不一定需要评论

它完成的功能是：

- 返回一条适合详情输出的完整 note 对象

---

### 2.5 `@transaction.atomic`

这个装饰器会出现在：

- `create_note`
- `update_note`

因为这两个动作都不只是“单步写入”。

例如创建时：

1. 先创建 note
2. 再设置 note 的标签关系

如果第一步成功、第二步失败，就会产生“半完成数据”。

加上事务以后：

- 只要中途出错
- 前面的数据库写入也会撤销

所以这个装饰器完成的功能是：

- 保证创建或更新动作的数据一致性

---

### 2.6 `def create_note(*, author, validated_data):`

这个函数的两个关键参数是：

- `author`
  当前登录用户对象
- `validated_data`
  serializer 校验通过后的输入数据

为什么 `author` 不从前端传：

- 作者身份必须来自当前登录用户
- 不能让前端自己伪造作者

为什么用 `validated_data` 而不是 `request.data`：

- 因为前者已经过了校验
- 后者只是原始输入

---

### 2.7 `payload = dict(validated_data)`

这行的意思是：

- 把 `validated_data` 拷贝成普通字典

为什么要拷贝：

- 因为后面会对这个字典做 `pop()`
- 不想直接修改原始的 `validated_data`

---

### 2.8 `tag_ids = payload.pop("tag_ids", [])`

这一行拆开看：

- `payload.pop("tag_ids", [])`
  从 `payload` 中拿出 `tag_ids`
- 如果没有这个键
  就返回默认值 `[]`

为什么要把 `tag_ids` 单独拿出来：

- 因为 `Note.objects.create(...)` 不能直接处理多对多 id 列表
- 标签关系需要在 note 创建之后再单独设置

这一行完成的功能是：

- 把“标签输入”和“普通 note 字段”拆开

---

### 2.9 `note = Note.objects.create(author=author, **payload)`

这行里：

- `author=author`
  明确指定笔记作者
- `**payload`
  把 `payload` 里剩下的字段展开，比如 `title`、`content`、`status`

假设 `payload` 是：

```python
{
    "title": "Django",
    "content": "CRUD demo",
    "status": "draft",
}
```

那么这句大致等价于：

```python
Note.objects.create(
    author=author,
    title="Django",
    content="CRUD demo",
    status="draft",
)
```

这行完成的功能是：

- 先把 note 本体创建出来

---

### 2.10 `note.tags.set(Tag.objects.filter(id__in=tag_ids))`

这句的作用分两步：

- `Tag.objects.filter(id__in=tag_ids)`
  查出所有 id 在 `tag_ids` 里的标签对象
- `note.tags.set(...)`
  把这些标签设置到当前 note 上

这里的 `id__in=tag_ids` 意思是：

- 查找 id 在这个列表中的所有 `Tag`

这行完成的功能是：

- 给新创建的 note 建立标签多对多关系

---

### 2.11 `return get_note_detail(note_id=note.pk)`

这一行的意思是：

- 刚创建完成后，不直接返回一个“裸 note 对象”
- 而是重新查一遍详情版 note

为什么这样做：

- 这样返回的对象已经把作者、标签、评论关系都准备好了
- 后面可以直接用详情 serializer 输出

`note.pk` 的意思是：

- 这条 note 自己的主键

所以 `create_note()` 整段代码完成的功能是：

- 使用当前登录用户和已校验的输入数据创建 note
- 设置标签关系
- 返回一条适合详情输出的完整 note

---

### 2.12 `def update_note(*, note, validated_data):`

这个函数的两个关键参数是：

- `note`
  已经查出来的那条要更新的 note 对象
- `validated_data`
  本次更新请求里经过校验后的字段数据

这里为什么传 `note`，而不是传 `note_id` 再查一次：

- 因为 view 层通常已经拿到对象了
- service 层直接更新这个对象即可

---

### 2.13 `tag_ids = payload.pop("tag_ids", None)`

这一行和创建时看起来很像，但默认值不同：

- 创建时默认 `[]`
- 更新时默认 `None`

这非常关键。

更新时：

- `None`
  表示“本次请求没有提标签，不改标签”
- `[]`
  表示“本次请求明确要求把标签清空”

所以这里必须用 `None` 来保留这个差异。

---

### 2.14 `for field, value in payload.items():`

这里的意思是：

- 遍历本次更新请求里传进来的所有普通字段

例如 `payload` 可能是：

```python
{
    "title": "New title",
    "status": "published",
}
```

那循环就会依次拿到：

- `field="title", value="New title"`
- `field="status", value="published"`

---

### 2.15 `setattr(note, field, value)`

`setattr()` 是 Python 内置函数。

它的作用是：

- 根据字段名动态给对象赋值

例如：

```python
setattr(note, "title", "New title")
```

大致等价于：

```python
note.title = "New title"
```

所以这一句完成的功能是：

- 把本次请求里传进来的字段，逐个写回到 `note` 对象上

---

### 2.16 `note.save()`

这一句的作用是：

- 把前面修改过的字段真正保存到数据库

前面的 `setattr()` 只是改了 Python 内存里的对象属性，只有 `save()` 才会真正落库。

---

### 2.17 `if tag_ids is not None:`

这里为什么判断 `is not None`，而不是 `if tag_ids:`？

因为更新时要区分两种情况：

- `tag_ids is None`
  表示没传标签字段，不动标签
- `tag_ids == []`
  表示明确要把标签清空

如果你写成：

```python
if tag_ids:
```

那空列表 `[]` 会被当成 False，就没法清空标签了。

所以这里必须写：

```python
if tag_ids is not None:
```

这句完成的功能是：

- 只要前端传了 `tag_ids`，哪怕是空列表，也执行标签更新

---

### 2.18 `return get_note_detail(note_id=note.pk)`

和创建时一样，这样返回的对象更适合后面的详情 serializer 输出。

`update_note()` 这一整段代码完成的功能是：

- 按本次请求提供的字段更新 note
- 按需更新标签关系
- 返回一条适合详情输出的完整 note

---

### 2.19 `def delete_note(*, note):`

```python
def delete_note(*, note):
    note.delete()
```

这段很简单，但也要知道它的边界：

- `note`
  是已经查出来的 note 对象
- `note.delete()`
  执行真正的删除动作

它完成的功能是：

- 删除当前这条 note

---

### 2.20 这一整段 service 代码完成了什么功能

它完成了 4 件事：

1. 把查询逻辑和 HTTP 解耦
2. 把创建、更新、删除的数据库操作集中起来
3. 用事务保证创建和更新的数据一致性
4. 让 view 层只做请求流程，不直接堆 ORM 细节

---

## 任务 3：把 `APIView` 补成完整 CRUD

今天继续使用 `APIView`，不要切到 `@api_view`，也不要急着切到 `GenericAPIView`。

推荐形态：

```python
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    NoteCreateSerializer,
    NoteDetailSerializer,
    NoteListSerializer,
    NoteUpdateSerializer,
)
from .services import create_note, delete_note, get_note, get_note_detail, list_notes, update_note


class NoteListAPIView(APIView):
    def get(self, request):
        notes = list_notes()
        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data)


class NoteDetailAPIView(APIView):
    def get(self, request, pk):
        note = get_note_detail(note_id=pk)
        serializer = NoteDetailSerializer(note)
        return Response(serializer.data)


class NoteCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        note = create_note(author=request.user, validated_data=serializer.validated_data)
        return Response(NoteDetailSerializer(note).data, status=status.HTTP_201_CREATED)


class NoteUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        note = get_note(note_id=pk)
        serializer = NoteUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        note = update_note(note=note, validated_data=serializer.validated_data)
        return Response(NoteDetailSerializer(note).data)


class NoteDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        note = get_note(note_id=pk)
        delete_note(note=note)
        return Response({"message": "deleted"}, status=status.HTTP_200_OK)
```

下面按视图逐段拆开。

### 3.1 先看导入

```python
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
```

这几行分别负责：

- `status`
  提供状态码常量，比如 `HTTP_201_CREATED`
- `IsAuthenticated`
  权限类，表示必须登录
- `Response`
  DRF 的响应对象
- `APIView`
  DRF 的类视图基类

---

### 3.2 `class NoteListAPIView(APIView):`

这个类负责：

- 笔记列表接口

### 3.3 `def get(self, request):`

这里的方法名是 `get`，对应：

- HTTP GET 请求

`request` 是：

- DRF 包装后的请求对象

### 3.4 `notes = list_notes()`

这行的意思是：

- 调用 service 层拿笔记列表
- view 不直接自己写 ORM

### 3.5 `serializer = NoteListSerializer(notes, many=True)`

这里：

- `NoteListSerializer(...)`
  说明要按“列表输出结构”序列化这些笔记
- `many=True`
  表示传进去的是多条 note，而不是单条

### 3.6 `return Response(serializer.data)`

意思是：

- 取序列化后的数据
- 用 DRF 的 `Response` 返回

这整个 `NoteListAPIView` 完成的功能是：

- 返回一组按列表结构序列化好的 note 数据

---

### 3.7 `class NoteDetailAPIView(APIView):`

这个类负责：

- 单条 note 的详情接口

### 3.8 `def get(self, request, pk):`

这里的 `pk` 来自路由里的：

```python
<int:pk>
```

也就是 URL 传进来的 note 主键。

### 3.9 `note = get_note_detail(note_id=pk)`

这行的意思是：

- 用路由参数 `pk` 去 service 层查详情对象

### 3.10 `serializer = NoteDetailSerializer(note)`

这里没有 `many=True`，因为：

- 这里只处理单条对象

这整个 `NoteDetailAPIView` 完成的功能是：

- 根据 URL 里的笔记 id 返回单条 note 详情

---

### 3.11 `class NoteCreateAPIView(APIView):`

这个类负责：

- 创建 note

### 3.12 `permission_classes = [IsAuthenticated]`

意思是：

- 这个接口必须登录后才能访问

为什么写成列表：

- 因为 DRF 一个接口可以同时挂多个权限类

### 3.13 `def post(self, request):`

`post()` 对应：

- HTTP POST 请求

也就是“创建资源”的动作。

### 3.14 `serializer = NoteCreateSerializer(data=request.data)`

这里最重要的是 `data=request.data`。

它的意思是：

- 用 `NoteCreateSerializer` 去校验前端请求体

这里的 `request.data` 是：

- DRF 已经帮你解析好的请求数据

### 3.15 `serializer.is_valid(raise_exception=True)`

这里的意思是：

- 执行校验
- 如果失败，直接抛异常，让 DRF 自动返回标准错误响应

### 3.16 `note = create_note(author=request.user, validated_data=serializer.validated_data)`

这一行拆得更细一点：

- `create_note(...)`
  调用 service 层真正创建数据
- `author=request.user`
  当前登录用户就是这篇 note 的作者
- `validated_data=serializer.validated_data`
  把校验后的安全数据交给 service 层

为什么这里没有单独再传 `tag_ids`：

- 因为 `tag_ids` 已经包含在 `serializer.validated_data` 里
- service 层会自己从里面拆出来处理

### 3.17 `return Response(NoteDetailSerializer(note).data, status=status.HTTP_201_CREATED)`

这一行里：

- `NoteDetailSerializer(note).data`
  表示创建成功后，用详情 serializer 输出完整 note 数据
- `status=status.HTTP_201_CREATED`
  表示资源创建成功，状态码是 201

`NoteCreateAPIView` 这一整段代码完成的功能是：

- 只允许登录用户创建 note
- 校验输入
- 把当前用户作为作者
- 调用 service 创建数据
- 返回新创建的 note 详情

---

### 3.18 `class NoteUpdateAPIView(APIView):`

这个类负责：

- 更新 note

### 3.19 `def patch(self, request, pk):`

这里为什么用 `patch()` 而不是 `put()`：

- `PATCH` 更适合“部分更新”
- 只改本次传入的字段，不要求把整个对象所有字段都传一遍

### 3.20 `note = get_note(note_id=pk)`

这行表示：

- 先根据 URL 的 `pk` 找到要更新的 note 对象

### 3.21 `serializer = NoteUpdateSerializer(data=request.data, partial=True)`

这里最关键的是 `partial=True`。

它的意思是：

- 这次校验按“部分更新”处理
- 没传的字段不算缺失错误

比如只传：

```json
{
  "title": "new title"
}
```

也能通过，而不用把 `content`、`status`、`tag_ids` 全部补齐。

所以：

- `data=request.data`
  表示拿请求体做输入校验
- `partial=True`
  表示这不是完整重写，而是部分更新

### 3.22 `note = update_note(note=note, validated_data=serializer.validated_data)`

这一行和创建时的逻辑类似：

- `note=note`
  把已经查出来的对象交给 service
- `validated_data=serializer.validated_data`
  把本次更新里真正合法的字段交给 service

### 3.23 `return Response(NoteDetailSerializer(note).data)`

表示：

- 更新成功后，返回最新的详情数据

`NoteUpdateAPIView` 这一整段代码完成的功能是：

- 根据 URL 找到 note
- 校验本次部分更新输入
- 只更新本次传入的字段
- 返回更新后的详情结果

---

### 3.24 `class NoteDeleteAPIView(APIView):`

这个类负责：

- 删除 note

### 3.25 `def delete(self, request, pk):`

这里的方法名 `delete` 对应：

- HTTP DELETE 请求

### 3.26 `delete_note(note=note)`

意思是：

- 把真正的删除动作交给 service 层

### 3.27 `return Response({"message": "deleted"}, status=status.HTTP_200_OK)`

这行的意思是：

- 删除成功后返回一个简单消息
- 状态码 200 表示请求成功

你也可以以后改成 204，但今天先不展开这个细节。

`NoteDeleteAPIView` 这一整段代码完成的功能是：

- 根据 URL 找到 note
- 执行删除
- 返回成功响应

---

### 3.28 这一整组 APIView 代码完成了什么功能

它完成了 5 件事：

1. 把列表、详情、创建、更新、删除接口补齐
2. 继续保持 view 只负责 HTTP 编排
3. 继续把 ORM 逻辑留在 service 层
4. 继续让输入校验由 serializer 完成
5. 让整个 CRUD 结构保持和 Day 8 同一条主线

今天先不用把“作者权限”做完美，Day 10 会专门补这件事。

---

## 任务 4：给 CRUD 补路由

今天既然把 CRUD 补齐了，路由也要一起补全。

推荐：

```python
path("api/notes/", views.NoteListAPIView.as_view(), name="note-list"),
path("api/notes/<int:pk>/", views.NoteDetailAPIView.as_view(), name="note-detail"),
path("api/notes/create/", views.NoteCreateAPIView.as_view(), name="note-create"),
path("api/notes/<int:pk>/update/", views.NoteUpdateAPIView.as_view(), name="note-update"),
path("api/notes/<int:pk>/delete/", views.NoteDeleteAPIView.as_view(), name="note-delete"),
```

下面把新增的两条路由单独解释一下。

### 4.1 `path("api/notes/<int:pk>/update/", ...)`

意思是：

- 访问某条笔记的更新接口
- URL 里的 `<int:pk>` 会传给视图方法的 `pk`

### 4.2 `path("api/notes/<int:pk>/delete/", ...)`

意思是：

- 访问某条笔记的删除接口
- 同样把 URL 里的 `pk` 传给 delete 方法

这些路由完成的功能是：

- 把完整 CRUD 的 5 个 APIView 都正式挂到 URL 上

---

## 任务 5：把 `validated_data` 真正用起来

今天不要再直接从 `request.data` 里到处 `.get()` 字段了。

固定写法：

```python
serializer = NoteCreateSerializer(data=request.data)
serializer.is_valid(raise_exception=True)
validated = serializer.validated_data
```

下面把这 3 行再明确一下。

### 5.1 `request.data`

它表示：

- 前端传进来的原始请求数据

这是“原材料”，不是最终可信结果。

### 5.2 `serializer.is_valid(...)`

它表示：

- 让 DRF 真正执行字段校验

只有执行完这一步，serializer 才会知道数据是否合法。

### 5.3 `serializer.validated_data`

它表示：

- 校验通过之后得到的安全数据

这时它才适合被拿去：

- 创建对象
- 更新对象
- 传入 service 层

这整段的核心结论就是：

- `request.data` 是原始输入
- `validated_data` 才是你真正应该拿去写数据库的数据

---

## 任务 6：理解 `@transaction.atomic`

今天你应该在 `service` 层开始用事务装饰器。

适合加事务的函数：

- `create_note`
- `update_note`

原因很简单：

- 笔记创建成功了，但标签设置失败，不应该留下半成品
- 内容改成功了，但标签更新失败，不应该只改一半

今天再把这个点固定得更清楚一点：

### 创建场景

创建不是单步动作，而是：

1. 创建 note 本体
2. 设置多对多标签关系

### 更新场景

更新也不是单步动作，而是：

1. 更新普通字段
2. 保存 note
3. 按需更新多对多标签

所以加事务的意义是：

- 这些步骤要么整体成功
- 要么有一步失败时整体回滚

你今天要固定的结论是：

> 事务属于数据一致性问题，应该优先出现在 service 层，而不是散落在 view 层。

---

## 任务 7：补第一批测试

今天不用把测试写满，但至少补一个最小闭环：

- 创建成功
- 更新成功
- 删除成功
- 非法输入返回 400

今天可以先继续用 Django `TestCase`。

推荐最小版本：

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Note, Tag


User = get_user_model()


class NoteApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="secret123")
        self.tag = Tag.objects.create(name="python")
        self.note = Note.objects.create(
            author=self.user,
            title="Before",
            content="Old content",
            status=Note.STATUS_DRAFT,
        )

    def test_create_note(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("note-create"),
            data={
                "title": "New note",
                "content": "Created by test",
                "status": "draft",
                "tag_ids": [self.tag.id],
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

    def test_update_note(self):
        self.client.force_login(self.user)
        response = self.client.patch(
            reverse("note-update", args=[self.note.id]),
            data={"title": "After"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_note(self):
        self.client.force_login(self.user)
        response = self.client.delete(reverse("note-delete", args=[self.note.id]))
        self.assertEqual(response.status_code, 200)
```

下面把关键点解释一下。

### 7.1 `self.client.force_login(self.user)`

意思是：

- 在测试里模拟当前用户已登录

### 7.2 `reverse("note-create")`

意思是：

- 不手写 URL 字符串
- 而是按路由名反查出对应 URL

### 7.3 `content_type="application/json"`

意思是：

- 告诉测试客户端，这次提交的是 JSON 请求体

### 7.4 `self.client.patch(...)`

这里直接发 `PATCH` 请求，是为了测试部分更新接口。

### 7.5 这组测试完成了什么功能

它完成了最小的 CRUD 回归验证：

- 创建能不能成功
- 更新能不能成功
- 删除能不能成功

虽然今天测试还不算完整，但已经开始给这条主线提供安全网了。

---

## 补充知识：`@api_view` 还有没有必要学

有必要知道，但不应该作为这个项目的主线。

它的定位更适合：

- 小型实验接口
- 很短的单端点
- 快速验证某个 DRF 功能

但你当前这个项目已经明确要走：

- `APIView`
- `Serializer`
- `service`

所以今天不再要求你把主资源接口改写成 `@api_view` 版。

---

## 今天不做什么

- 不切到 `GenericAPIView`
- 不切到 `ViewSet`
- 不写多套路由并存
- 不把 service 逻辑塞回 serializer

今天只补全主线。

---

## 今天的交付标准

- [ ] `Note` 接口具备完整 CRUD
- [ ] `serializers.py` 中完成读写分离
- [ ] `services.py` 中有完整 CRUD 动作
- [ ] 创建和更新动作使用 `transaction.atomic`
- [ ] `APIView` 中使用 `serializer.is_valid(raise_exception=True)`
- [ ] 路由补齐 CRUD 入口
- [ ] 代码里主要 ORM 操作不再散在 `views.py`
- [ ] 补至少 3 个基础测试

---

## 今日复盘问题

1. 为什么 `validated_data` 比 `request.data` 更值得信任？
2. 为什么更新 serializer 里的 `tag_ids` 不应该默认 `[]`？
3. 为什么 `partial=True` 对 `PATCH` 很重要？
4. 为什么 `transaction.atomic` 更适合写在 service 层？
5. 同一个 `Note` 为什么应该有多个 serializer？
6. 为什么今天我们是“补完昨天的主线”，而不是“换一种 DRF 写法”？

---

## 一句总结

今天你做的不是“再学一个 DRF 新名词”，而是：

> 把 `APIView + Serializer + service` 这条主线补成真正可用的基础 CRUD 结构。
