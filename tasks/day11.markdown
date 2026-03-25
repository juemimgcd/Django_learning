# Day 11 任务清单：把列表接口做成真实项目可用的样子

## 主线继续不变

今天还是：

- `APIView`
- `Serializer`
- `service`

今天不换视图抽象，专门升级“列表接口工程化能力”。

也就是说：

- Day 8 搭起 DRF 主线
- Day 9 补全基础 CRUD
- Day 10 补上认证和权限
- Day 11 开始把“列表接口”做得更像真实项目

今天你不会学一套新架构，而是在现有主线上继续加能力。

---

## 今天的目标

把现在的笔记列表接口从“能返回数据”升级成：

- 可过滤
- 可搜索
- 可排序
- 可分页

你今天做的不是新花样，而是把列表接口做成真实项目会需要的样子。

在真实项目里，一个列表接口通常很快就会被问到这些需求：

- 只看已发布内容
- 只看某个作者的内容
- 只看某个标签下的内容
- 按标题搜关键字
- 按时间倒序或正序
- 控制每页数量

所以今天学的本质不是“多几个参数”，而是：

> 如何让列表接口具备基本的工程化能力。

---

## 今天这份笔记怎么读

和 Day 8、Day 9、Day 10 一样，今天不要只看代码结论。

你要继续训练这种阅读方式：

1. 先看这段代码要解决什么问题
2. 再看每个字段、每个参数在控制什么
3. 再看这段代码放在哪一层最合适
4. 最后总结这段代码完成了什么功能

今天特别容易混的点有：

- `request.query_params`
- 查询参数 serializer
- `ordering`
- `distinct()`
- `PageNumberPagination`
- `paginate_queryset(...)`
- `get_paginated_response(...)`

如果不逐段拆开，很容易觉得“这几个 API 好像都是魔法”。

---

## 为什么今天先做列表工程化

因为列表接口通常是最先变复杂的。

真实 API 里最常见的需求往往是：

- 只看已发布内容
- 按标题搜索
- 按时间倒序
- 控制分页大小

这些需求一旦开始出现，代码组织会直接影响项目体验。

所以今天继续坚持：

> 不改主架构，只在 `APIView + Serializer + service` 上加列表能力。

---

## 今天建议看的官方文档

- Filtering  
  https://www.django-rest-framework.org/api-guide/filtering/
- Pagination  
  https://www.django-rest-framework.org/api-guide/pagination/

如果你想先看 APIView 下怎么分页，再重点查：

- `PageNumberPagination`
- `request.query_params`

今天你要重点建立 4 个认知：

1. 查询参数也值得被校验
2. 过滤和排序逻辑仍然应该尽量留在 service 层
3. 就算使用 `APIView`，也一样可以优雅地接入 DRF 分页
4. 列表接口往往是最先进入“工程化阶段”的接口

---

## 今天建议新增的文件

```text
notes/
├─ serializers.py
├─ services.py
├─ pagination.py
├─ views.py
├─ urls.py
└─ tests.py
```

今天不一定必须新建 `pagination.py`，但如果你已经准备长期用分页，建议建。

为什么建议把分页类单独拆文件：

- 分页本身是一个独立能力
- 后面可能不只一个列表接口会复用
- 单独放会更清楚

---

## 任务 1：先给查询参数也配 serializer

今天建议把“列表查询参数”也当成正式输入来管理，而不是在 view 里到处 `request.query_params.get(...)`。

例如：

```python
from rest_framework import serializers

from .models import Note


class NoteListQuerySerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=Note.STATUS_CHOICES,
        required=False,
    )
    author_id = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    tag_id = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    keyword = serializers.CharField(
        required=False,
        allow_blank=False,
    )
    ordering = serializers.ChoiceField(
        choices=[
            "created_at",
            "-created_at",
            "updated_at",
            "-updated_at",
            "title",
            "-title",
        ],
        required=False,
        default="-created_at",
    )
```

下面把这段代码逐段拆开讲。

### 1.1 为什么查询参数也要 serializer

因为查询参数本质上也是用户输入。

例如：

- `?status=published`
- `?author_id=2`
- `?tag_id=3`
- `?ordering=-created_at`

这些值都来自客户端，不应该默认信任。

如果你不校验查询参数，常见问题会是：

- 非法状态值也被直接带进 ORM
- 排序字段随便传，甚至出现你不想暴露的字段
- 参数散落在 view 里，一多就乱

所以今天你要固定一个认知：

> 查询参数和请求体一样，都是输入，都值得被 serializer 管起来。

---

### 1.2 `class NoteListQuerySerializer(serializers.Serializer):`

这里用的是普通 `Serializer`，不是 `ModelSerializer`。

原因是：

- 查询参数不是数据库模型对象
- 它只是接口输入规则

所以这里的重点不是“某个模型长什么样”，而是：

- 前端可以传哪些筛选条件
- 每个条件该怎么校验

---

### 1.3 `status = serializers.ChoiceField(...)`

```python
status = serializers.ChoiceField(
    choices=Note.STATUS_CHOICES,
    required=False,
)
```

这行拆开看：

- `status`
  查询参数名，也就是前端可以传 `?status=...`
- `serializers.ChoiceField(...)`
  表示这个字段只能从给定选项中取值
- `choices=Note.STATUS_CHOICES`
  复用模型里已经定义好的合法状态选项
- `required=False`
  表示这个参数不是必须传的

这行代码完成的功能是：

- 让前端只能按合法状态筛选 note，并且允许不传状态筛选

---

### 1.4 `author_id = serializers.IntegerField(required=False, min_value=1)`

这行的意思是：

- `author_id`
  查询参数名，对应 `?author_id=...`
- `serializers.IntegerField(...)`
  表示这个值必须是整数
- `required=False`
  不传也可以
- `min_value=1`
  最小值必须是 1

为什么要 `min_value=1`：

- 数据库 id 一般从 1 开始
- `0` 或负数通常没有意义

这行代码完成的功能是：

- 让作者筛选参数既有类型约束，又有基本合法范围

---

### 1.5 `tag_id = serializers.IntegerField(required=False, min_value=1)`

它和 `author_id` 的逻辑一样，只是用于标签筛选。

它完成的功能是：

- 让前端只能传合法的标签 id 作为筛选条件

---

### 1.6 `keyword = serializers.CharField(required=False, allow_blank=False)`

这一行的意思是：

- `keyword`
  查询参数名，对应 `?keyword=...`
- `serializers.CharField(...)`
  表示它必须是字符串
- `required=False`
  不传也可以
- `allow_blank=False`
  如果传了，就不能是空字符串

为什么这里要 `allow_blank=False`：

- 因为 `?keyword=` 这种空关键字通常没有意义
- 还会让代码语义变得模糊

这行代码完成的功能是：

- 只允许“有实际内容的关键词搜索”

---

### 1.7 `ordering = serializers.ChoiceField(...)`

```python
ordering = serializers.ChoiceField(
    choices=[
        "created_at",
        "-created_at",
        "updated_at",
        "-updated_at",
        "title",
        "-title",
    ],
    required=False,
    default="-created_at",
)
```

这里每个参数的意思是：

- `ordering`
  查询参数名，对应 `?ordering=...`
- `serializers.ChoiceField(...)`
  表示排序值必须从给定列表中选择
- `choices=[...]`
  明确只允许按这些字段排序
- `required=False`
  前端不传也可以
- `default="-created_at"`
  不传时默认按创建时间倒序

为什么排序字段要“收口”：

- 不希望前端随便按任意字段排序
- 有些字段没有业务意义
- 有些字段不应该暴露给外部当排序入口

这里的 `-created_at` 这种写法是什么意思：

- 前面的 `-` 表示倒序
- 没有 `-` 表示正序

所以：

- `created_at` = 按创建时间正序
- `-created_at` = 按创建时间倒序

这行代码完成的功能是：

- 把排序能力变成一个“受控的、已校验的接口输入”

---

### 1.8 这整个查询参数 serializer 完成了什么功能

它完成了 4 件事：

1. 明确列出列表接口允许哪些查询参数
2. 给这些参数加上类型和范围约束
3. 给排序设置可控的白名单
4. 让后续 view 和 service 拿到的输入更干净、更可信

---

## 任务 2：把过滤和排序继续放在 `service` 层

今天建议在 `services.py` 中把列表动作升级成带过滤版本。

例如：

```python
from .models import Note


def list_notes(
    *,
    status=None,
    author_id=None,
    tag_id=None,
    keyword=None,
    ordering="-created_at",
):
    queryset = Note.objects.select_related("author").prefetch_related("tags")

    if status:
        queryset = queryset.filter(status=status)

    if author_id:
        queryset = queryset.filter(author_id=author_id)

    if tag_id:
        queryset = queryset.filter(tags__id=tag_id)

    if keyword:
        queryset = queryset.filter(title__icontains=keyword)

    return queryset.distinct().order_by(ordering)
```

下面把这段 service 代码逐段拆开。

### 2.1 `def list_notes(*, status=None, author_id=None, tag_id=None, keyword=None, ordering="-created_at"):`

这里有 5 个关键参数：

- `status`
  按 note 状态筛选
- `author_id`
  按作者筛选
- `tag_id`
  按标签筛选
- `keyword`
  按标题关键字筛选
- `ordering`
  排序规则

这里为什么前面有一个 `*`：

- 表示这些参数必须以关键字方式传入

也就是说，推荐这样调用：

```python
list_notes(status="published", ordering="-created_at")
```

而不是：

```python
list_notes("published", None, None, None, "-created_at")
```

这样写的好处是：

- 调用时更清楚
- 参数多的时候不容易传错顺序

---

### 2.2 `queryset = Note.objects.select_related("author").prefetch_related("tags")`

这行代码的作用是：

- 初始化一个基础查询集
- 并提前做好关联预加载

拆开看：

- `Note.objects`
  进入 `Note` 的 ORM 查询入口
- `select_related("author")`
  提前把外键作者查出来
- `prefetch_related("tags")`
  提前把多对多标签查出来

为什么这里不加 `.all()` 也可以：

- Django QuerySet 本身是惰性对象
- 继续链式调用过滤和排序都没问题

这行代码完成的功能是：

- 先得到一个适合继续叠加筛选条件的基础查询集

---

### 2.3 `if status: queryset = queryset.filter(status=status)`

这一段的意思是：

- 如果前端传了 `status`
- 就加上状态过滤条件

这里的 `queryset.filter(status=status)` 表示：

- 查找 `status` 字段等于指定值的 note

这段代码完成的功能是：

- 支持按笔记状态过滤列表

---

### 2.4 `if author_id: queryset = queryset.filter(author_id=author_id)`

这一段的意思是：

- 如果前端传了 `author_id`
- 就只取这个作者的 note

这里为什么直接用 `author_id`，而不是 `author__id`：

- 因为 Django 外键字段天然就有 `author_id`
- 直接按 id 过滤更简单

这段代码完成的功能是：

- 支持按作者过滤列表

---

### 2.5 `if tag_id: queryset = queryset.filter(tags__id=tag_id)`

这一段表示：

- 如果前端传了标签 id
- 就查和这个标签有关联的 note

这里的 `tags__id=tag_id` 是 Django ORM 的跨关系过滤写法。

意思是：

- 沿着 `tags` 这个多对多关系
- 查 `Tag` 的 `id`

这段代码完成的功能是：

- 支持按标签过滤 note 列表

---

### 2.6 `if keyword: queryset = queryset.filter(title__icontains=keyword)`

这一段的意思是：

- 如果前端传了关键词
- 就按标题做包含匹配

这里的 `title__icontains=keyword`：

- `title`
  表示查 note 的标题字段
- `icontains`
  表示忽略大小写的包含搜索

例如：

- `keyword="django"`

会匹配：

- `"Django 入门"`
- `"django rest framework"`

这段代码完成的功能是：

- 支持按标题关键字模糊搜索

---

### 2.7 `return queryset.distinct().order_by(ordering)`

这一行拆开看：

- `distinct()`
  去重
- `order_by(ordering)`
  按指定字段排序

为什么这里需要 `distinct()`：

- 因为按多对多关系 `tags__id=...` 过滤时，底层 SQL 可能产生重复结果
- `distinct()` 可以把重复 note 去掉

为什么排序放在最后：

- 因为所有过滤条件都加完以后，再统一排序更自然

这行代码完成的功能是：

- 返回一个“已完成过滤、去重、排序”的列表查询集

---

### 2.8 为什么过滤和排序继续放在 `service` 层

今天的重点不是“绝对不能在 view 里写过滤”，而是：

- 既然你已经决定 service 管 ORM
- 那查询条件也应该留在 service 的边界里

这样做的好处是：

1. `view` 只负责接收和转发参数
2. 查询逻辑集中管理
3. 测试 service 时更方便
4. 以后别的接口复用这套查询时也更容易

这整段 service 代码完成的功能是：

- 把 note 列表的过滤、搜索、排序规则集中封装起来

---

## 任务 3：在 APIView 里接入 DRF 分页

即使你不使用通用类视图，`APIView` 里也一样能很好地用 DRF 分页。

推荐先新建一个分页类：

```python
from rest_framework.pagination import PageNumberPagination


class NotePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20
```

然后在 `APIView` 中这样用：

```python
from rest_framework.response import Response
from rest_framework.views import APIView

from .pagination import NotePagination
from .serializers import NoteListQuerySerializer, NoteListSerializer
from .services import list_notes


class NoteListAPIView(APIView):
    pagination_class = NotePagination

    def get(self, request):
        query_serializer = NoteListQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        queryset = list_notes(**query_serializer.validated_data)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = NoteListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
```

下面把分页类和 APIView 里的关键代码逐段拆开。

### 3.1 `from rest_framework.pagination import PageNumberPagination`

这行的意思是：

- 导入 DRF 自带的“按页码分页”基类

`PageNumberPagination` 是最适合入门的分页方式之一。

它的思路很直观：

- 前端传 `?page=1`
- 后端返回第一页

---

### 3.2 `class NotePagination(PageNumberPagination):`

这行表示：

- 你定义了一个自己的分页类
- 它继承 DRF 的页码分页基类

为什么建议单独写分页类：

- 配置集中
- 以后容易复用
- view 里更干净

---

### 3.3 `page_size = 5`

意思是：

- 默认每页返回 5 条数据

如果前端没有主动指定分页大小，就按这个值来。

---

### 3.4 `page_size_query_param = "page_size"`

意思是：

- 允许前端通过查询参数 `page_size` 指定每页数量

例如：

- `?page=1&page_size=10`

---

### 3.5 `max_page_size = 20`

意思是：

- 就算前端自己传 `page_size`
- 也最多只能到 20

为什么要限制最大值：

- 防止前端一次请求太多数据
- 避免列表接口压力过大

`NotePagination` 这一整个类完成的功能是：

- 给 note 列表定义一套稳定、可控的分页规则

---

### 3.6 `pagination_class = NotePagination`

这一行是 `APIView` 的类属性。

它的意思是：

- 当前列表视图默认使用 `NotePagination` 这个分页类

这行完成的功能是：

- 把分页策略挂到 `NoteListAPIView` 上

---

### 3.7 `query_serializer = NoteListQuerySerializer(data=request.query_params)`

这里最关键的是 `request.query_params`。

它的意思是：

- DRF 提供的查询参数读取入口

你可以把它理解成：

- 查询字符串版的 `request.data`

例如请求：

```text
/api/notes/?status=published&page=2
```

那么：

- `request.query_params`
  就会包含这些查询参数

这一行完成的功能是：

- 准备用查询参数 serializer 去校验前端传来的筛选和排序条件

---

### 3.8 `query_serializer.is_valid(raise_exception=True)`

意思是：

- 执行查询参数校验
- 如果参数非法，直接抛异常让 DRF 返回标准错误响应

例如这些都能被拦下来：

- 非法状态值
- 非法排序字段
- 非法 `author_id`

这行完成的功能是：

- 保证后面的 service 拿到的是合法查询参数

---

### 3.9 `queryset = list_notes(**query_serializer.validated_data)`

这一行拆开看：

- `query_serializer.validated_data`
  是校验通过后的查询参数字典
- `**query_serializer.validated_data`
  把这个字典展开成关键字参数传给 `list_notes(...)`

例如如果 `validated_data` 是：

```python
{
    "status": "published",
    "ordering": "-created_at",
}
```

那么这句大致等价于：

```python
list_notes(status="published", ordering="-created_at")
```

这行完成的功能是：

- 把“已校验的查询参数”交给 service 层生成最终查询集

---

### 3.10 `paginator = self.pagination_class()`

这一行的意思是：

- 创建一个分页类实例

这里的 `self.pagination_class`
就是你前面挂上的 `NotePagination`。

这行完成的功能是：

- 准备启动分页流程

---

### 3.11 `page = paginator.paginate_queryset(queryset, request, view=self)`

这是今天最关键的分页调用之一。

先看这 3 个参数：

- `queryset`
  要分页的数据源
- `request`
  当前请求对象，分页器要从里面读 `page`、`page_size`
- `view=self`
  当前视图实例，有些分页逻辑会用到

这个方法的作用是：

- 按当前请求里的页码和页大小
- 从完整 queryset 里切出当前页的数据

所以这行完成的功能是：

- 生成“当前这一页”的结果集合

---

### 3.12 `serializer = NoteListSerializer(page, many=True)`

这里和你前面学到的一样：

- `page`
  是一页 note 对象
- `many=True`
  表示这里是多个对象

这行完成的功能是：

- 把当前页的 note 对象列表序列化成可返回的 JSON 结构

---

### 3.13 `return paginator.get_paginated_response(serializer.data)`

这是今天第二个最关键的分页调用。

它的作用是：

- 自动生成 DRF 标准分页响应结构

返回结果通常长这样：

```json
{
  "count": 12,
  "next": "http://127.0.0.1:8000/api/notes/?page=2",
  "previous": null,
  "results": [...]
}
```

这行完成的功能是：

- 用 DRF 官方推荐的分页结构把当前页数据返回给前端

---

### 3.14 这整个分页版 `NoteListAPIView` 完成了什么功能

它完成了 5 件事：

1. 先校验查询参数
2. 再交给 service 做过滤和排序
3. 再用分页类切出当前页
4. 再把这一页的 note 序列化
5. 最后按 DRF 标准分页结构返回结果

这就是非常典型的：

- APIView
- Serializer
- Service
- DRF 内建分页

组合写法。

---

## 任务 4：把排序字段收口

今天不要让前端随便传任意字段排序。

比较好的做法是：

- 在查询参数 serializer 里限定允许值
- service 里只使用已校验过的字段

这样你就能明确控制：

- 哪些字段可排序
- 哪些字段不暴露

你今天要固定的认知是：

> 排序能力不是“前端爱传什么就传什么”，而是接口契约的一部分。

---

## 任务 5：补路由

如果你的列表接口还是：

```python
path("api/notes/", views.NoteListAPIView.as_view(), name="note-list"),
```

那今天路由本身不一定需要大改。

重点是：

- 现在这个 URL 支持更多查询参数了

例如：

- `/api/notes/?status=published`
- `/api/notes/?author_id=2`
- `/api/notes/?tag_id=3`
- `/api/notes/?ordering=-created_at`
- `/api/notes/?page=2&page_size=10`

这里最重要的认识是：

- 路由没变
- 但接口能力已经大幅提升

这就是为什么列表接口工程化往往不是“多几个路径”，而是“让同一个列表路径支持更多合法查询能力”。

---

## 任务 6：今天重点测多条件组合

今天的列表接口至少要自己手测这几种组合：

- `?status=published`
- `?keyword=django`
- `?ordering=-created_at`
- `?page=2&page_size=5`
- `?status=published&keyword=django&ordering=-updated_at`

真实项目里，列表接口的价值恰恰就体现在这种组合能力上。

你今天要主动观察这些现象：

- 校验非法查询参数时会不会直接报错
- 搜索和过滤组合时结果对不对
- 分页结构是不是统一的
- 排序能不能和筛选一起工作

---

## 任务 7：补列表相关测试

今天建议新增这些测试：

- 按 `status` 过滤
- 按 `author_id` 过滤
- 按标签过滤
- 分页结构是否有 `count/next/previous/results`

推荐最小测试示例：

```python
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Note, Tag


User = get_user_model()


class NoteListApiTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="alice", password="secret123")
        self.user2 = User.objects.create_user(username="bob", password="secret123")
        self.tag_python = Tag.objects.create(name="python")
        self.tag_django = Tag.objects.create(name="django")

        self.note1 = Note.objects.create(
            author=self.user1,
            title="Django basics",
            content="first note",
            status=Note.STATUS_PUBLISHED,
        )
        self.note2 = Note.objects.create(
            author=self.user1,
            title="Draft note",
            content="second note",
            status=Note.STATUS_DRAFT,
        )
        self.note3 = Note.objects.create(
            author=self.user2,
            title="Python tips",
            content="third note",
            status=Note.STATUS_PUBLISHED,
        )

        self.note1.tags.set([self.tag_django])
        self.note2.tags.set([self.tag_python])
        self.note3.tags.set([self.tag_python])

    def test_filter_by_status(self):
        response = self.client.get(reverse("note-list"), {"status": "published"})
        self.assertEqual(response.status_code, 200)

    def test_filter_by_author_id(self):
        response = self.client.get(reverse("note-list"), {"author_id": self.user1.id})
        self.assertEqual(response.status_code, 200)

    def test_filter_by_tag_id(self):
        response = self.client.get(reverse("note-list"), {"tag_id": self.tag_python.id})
        self.assertEqual(response.status_code, 200)

    def test_paginated_response_structure(self):
        response = self.client.get(reverse("note-list"), {"page": 1, "page_size": 2})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("count", payload)
        self.assertIn("next", payload)
        self.assertIn("previous", payload)
        self.assertIn("results", payload)
```

下面把关键点解释一下。

### 7.1 `self.client.get(reverse("note-list"), {"status": "published"})`

这里：

- `reverse("note-list")`
  按路由名找到列表接口 URL
- `{"status": "published"}`
  作为查询参数附加到 GET 请求上

最终相当于请求：

```text
/api/notes/?status=published
```

---

### 7.2 `self.note1.tags.set([self.tag_django])`

这一步的作用是：

- 给测试数据建立标签多对多关系

如果你不先把标签关系建好：

- 标签过滤测试就没有意义

---

### 7.3 `response.json()`

作用是：

- 把响应体解析成 Python 字典

这样后面就能直接检查：

- 有没有 `count`
- 有没有 `results`

---

### 7.4 `self.assertIn("count", payload)` 这类断言

这类断言的重点不是校验具体值，而是：

- 确认分页结构已经按预期返回

所以今天测试里很关键的点是：

- 不只要测“能拿到数据”
- 还要测“返回结构是不是已经工程化了”

---

### 7.5 这组测试完成了什么功能

它完成了最小的列表能力验证：

1. 能按状态过滤
2. 能按作者过滤
3. 能按标签过滤
4. 返回结构具备标准分页字段

这就是 Day 11 最该测出来的核心价值。

---

## 补充知识：为什么今天不直接切成 `ListAPIView`

因为今天你的目标是把列表做成“真实可用”，不是“为了少几行代码而换抽象”。

在当前主线里，`APIView` 已经足够表达清楚：

- 先校验查询参数
- 再调用 service
- 再套分页
- 再返回响应

这条线非常清楚，也非常像真实项目。

今天你要固定下来的判断标准是：

- 如果当前写法已经足够清楚，而且和项目边界一致
- 就没必要为了学一个新抽象强行改写

---

## 今天不做什么

- 不切到 `GenericAPIView`
- 不切到 `ViewSet`
- 不引入一堆过滤后端魔法让自己都看不懂

今天优先追求：

- 可读
- 稳定
- 贴近项目主线

---

## 今天的交付标准

- [ ] 增加查询参数 serializer
- [ ] 列表 service 支持过滤和排序
- [ ] 新建分页类
- [ ] `APIView` 接入 DRF 分页
- [ ] 列表接口支持分页参数
- [ ] 列表接口支持至少 3 个过滤条件
- [ ] 补充列表相关测试

---

## 今日复盘问题

1. 为什么查询参数也值得用 serializer 管起来？
2. 为什么列表过滤逻辑更适合继续放在 service 层？
3. 为什么就算使用 APIView，也完全可以优雅接入 DRF 分页？
4. `paginate_queryset(queryset, request, view=self)` 里这几个参数分别在做什么？
5. 为什么 `distinct()` 在标签过滤时很重要？
6. 真实项目里，列表接口为什么往往比详情接口更早变复杂？

---

## 一句总结

今天你没有换写法，而是让现有主线第一次具备了真实项目列表接口该有的工程化能力。
