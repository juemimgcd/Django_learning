# Day 13 任务清单：学会过滤、搜索、排序和分页

## 今天的目标

到今天为止，你已经有一套结构比较完整的 DRF API 了。  
但如果一个列表接口只有“返回全部数据”，那它离真实项目还差一截。

真实 API 通常都会遇到这些需求：

- 只看已发布笔记
- 按标题搜索
- 按创建时间排序
- 分页返回，不一次性吐出所有数据

所以今天的主题很明确：

> 把 DRF 列表接口做得更像真实项目可用的列表接口。

今天学完后，你应该能做到：

- 理解 `get_queryset()` 和 DRF 过滤后端的关系
- 会做基础字段过滤
- 会做关键词搜索
- 会做排序
- 会接上分页
- 知道为什么列表优化不只是“好看”，而是接口工程化的一部分

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 50 分钟 | 阅读 Filtering 和 Pagination |
| 设计查询参数 | 30 分钟 | 规划当前 `Note` 资源需要哪些过滤能力 |
| 核心编码 | 130 分钟 | 给 ViewSet 加过滤、搜索、排序、分页 |
| 联调复盘 | 70 分钟 | 用不同查询参数验证接口行为 |

---

## 今天的官方文档入口

- Filtering  
  https://www.django-rest-framework.org/api-guide/filtering/
- Pagination  
  https://www.django-rest-framework.org/api-guide/pagination/

建议阅读顺序：

1. 先看 `Filtering`
2. 再看 `Pagination`

---

## 先把今天的“列表接口升级目标”想清楚

以你当前的 `Note` 资源为例，今天最适合加的能力是：

- `status=draft` 或 `status=published`
- `tag=python`
- `search=django`
- `ordering=-created_at`
- `page=2`

如果你把这些能力都做进去，那你的列表接口体验会一下子提升很多。

---

## 今天你必须理解的 6 个概念

## 1. 最基础的过滤，往往直接写在 `get_queryset()` 就够了

比如：

```python
def get_queryset(self):
    queryset = Note.objects.select_related("author").prefetch_related("tags").all()

    status_value = self.request.query_params.get("status")
    if status_value:
        queryset = queryset.filter(status=status_value)

    return queryset
```

这种写法的优点是：

- 直观
- 好懂
- 很适合你当前这个学习项目

所以今天不要一开始就追求过度抽象。  
先把内建能力用顺。

---

## 2. `request.query_params` 是 DRF 里更推荐的查询参数入口

前面原生 Django 里你常写的是：

```python
request.GET
```

在 DRF 里，更推荐：

```python
request.query_params
```

本质上它和查询参数有关，  
但在 DRF 语境里，这个名字更统一，也更清楚。

---

## 3. 搜索和排序通常交给 DRF 的过滤后端

DRF 已经内建了常用过滤后端，例如：

- `SearchFilter`
- `OrderingFilter`

你可以在视图上这样配置：

```python
from rest_framework.filters import SearchFilter, OrderingFilter


filter_backends = [SearchFilter, OrderingFilter]
search_fields = ["title", "content", "author__username"]
ordering_fields = ["created_at", "updated_at", "title"]
ordering = ["-created_at"]
```

这样就能支持：

- `?search=django`
- `?ordering=created_at`
- `?ordering=-created_at`

---

## 4. 分页不是“可有可无”，而是列表接口的基本能力

如果一张表以后有很多数据，  
一次把所有记录都返回出来会带来这些问题：

- 响应过大
- 查询压力变大
- 前端处理成本变大
- 用户体验变差

所以分页要尽早养成习惯。

DRF 官方最常用、也最适合入门的是：

- `PageNumberPagination`

---

## 5. 分页既可以全局配置，也可以按视图配置

比如在 `settings.py` 中全局设置：

```python
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
}
```

也可以针对某个视图单独设置 `pagination_class`。  
学习阶段我建议你先从全局配置开始，最简单。

---

## 6. 查询优化要和过滤分页一起看

今天很容易出现一个误区：

- 只顾着让查询参数生效
- 忘了继续做 `select_related()` 和 `prefetch_related()`

但真实项目里，列表接口常常是性能热点。  
所以你今天一定要把这些一起想：

- 查询条件
- 排序
- 分页
- 关联预加载

这四件事是一个整体。

---

## 今天的项目任务

今天我们重点升级 `NoteViewSet` 的列表能力。

建议完成这些事：

1. 在 `settings.py` 中加 DRF 分页配置
2. 在 `NoteViewSet` 上接入 `SearchFilter` 和 `OrderingFilter`
3. 在 `get_queryset()` 中补基础字段过滤
4. 实现按当前用户、状态、标签的过滤能力
5. 验证 `search`、`ordering`、`page` 多种组合

---

## 先补全局分页配置

在 `studynotes/settings.py` 中，把 `REST_FRAMEWORK` 配置补成类似这样：

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 5,
}
```

学习阶段把每页先设小一点，例如 `5`，  
这样你更容易观察分页效果。

---

## 给 `NoteViewSet` 加搜索和排序

在 `notes/views.py` 中：

```python
from rest_framework.filters import SearchFilter, OrderingFilter


class NoteViewSet(ModelViewSet):
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "content", "author__username"]
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]
```

这样你就已经获得了两种能力：

- `?search=xxx`
- `?ordering=xxx`

---

## 再在 `get_queryset()` 中补基础过滤

今天建议你支持这些查询参数：

- `status`
- `author_id`
- `mine`
- `tag`

例如：

```python
def get_queryset(self):
    queryset = (
        Note.objects.select_related("author")
        .prefetch_related("tags", "comments")
        .all()
        .order_by("-created_at")
    )

    status_value = self.request.query_params.get("status")
    if status_value:
        queryset = queryset.filter(status=status_value)

    author_id = self.request.query_params.get("author_id")
    if author_id:
        queryset = queryset.filter(author_id=author_id)

    tag_name = self.request.query_params.get("tag")
    if tag_name:
        queryset = queryset.filter(tags__name__iexact=tag_name)

    mine = self.request.query_params.get("mine")
    if mine == "1" and self.request.user.is_authenticated:
        queryset = queryset.filter(author=self.request.user)

    return queryset.distinct()
```

这里你要注意：

- 通过标签筛选时，通常最好加 `distinct()`
- 因为多表关联可能产生重复行

---

## 今天建议你额外体验一个自定义分页类

如果你想对分页再有一点感觉，可以在 `notes/pagination.py` 中新建：

```python
from rest_framework.pagination import PageNumberPagination


class NotePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20
```

然后在 `ViewSet` 上挂：

```python
pagination_class = NotePagination
```

这样你就能支持：

- `?page=2`
- `?page_size=10`

这个不是今天必须做，但很值得体验一下。

---

## 今天推荐你主动观察的 7 个现象

## 1. 列表接口真正开始像“可用 API”了

尤其是加上：

- 过滤
- 搜索
- 排序
- 分页

之后，接口实用性会提升很多。

## 2. `query_params` 比你直接到处用 `request.GET` 更统一

这会让你的 DRF 代码风格更稳定。

## 3. `SearchFilter` 很适合快速上手，但不是万能搜索方案

它适合入门和中小规模接口，  
但以后复杂搜索你可能还会接：

- 更复杂的字段规则
- 全文检索
- 第三方搜索方案

今天先不用想那么远。

## 4. `OrderingFilter` 会让接口更灵活，但也要控制可排序字段

不要把所有字段都随便放开。  
只开放你明确允许的字段。

## 5. 分页返回结构和前几天不一样了

你会看到类似：

```json
{
  "count": 12,
  "next": "...",
  "previous": null,
  "results": [...]
}
```

这说明 DRF 正在给你统一的列表分页结构。

## 6. 多条件组合时，接口行为更接近真实产品需求

比如：

- `?status=published&search=django&ordering=-created_at&page=2`

你今天就应该主动试试这种组合。

## 7. 查询优化的价值会更明显

当列表接口越来越复杂时，  
你会更理解为什么前面一直强调：

- `select_related`
- `prefetch_related`

---

## 今天怎么测试

启动服务：

```powershell
python manage.py runserver
```

### 1. 只按状态过滤

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/?status=published" -Method Get
```

### 2. 关键词搜索

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/?search=django" -Method Get
```

### 3. 排序

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/?ordering=created_at" -Method Get
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/?ordering=-created_at" -Method Get
```

### 4. 分页

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/?page=1" -Method Get
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/?page=2" -Method Get
```

### 5. 多条件组合

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/drf/v4/notes/?status=published&search=python&ordering=-updated_at&page=1" -Method Get
```

今天一定要多测组合场景，  
因为真实项目的列表接口价值恰恰就在这里。

---

## 今天的易错点

## 1. 把所有过滤都写成后端魔法，结果自己都看不懂

今天优先追求“清楚”和“可读”。  
基础过滤直接写在 `get_queryset()` 里完全没问题。

## 2. 只记得加搜索排序，忘了分页

分页不是装饰品。  
它是列表接口的基本能力。

## 3. 只顾筛选，忘了 `distinct()`

尤其是标签这种多对多筛选，  
不注意就可能出现重复结果。

## 4. 排序字段放得太随意

尽量明确控制在：

- `created_at`
- `updated_at`
- `title`

这类你清楚知道意义的字段上。

## 5. 忘记给匿名和登录用户分别考虑 `mine=1`

如果匿名用户传了 `mine=1`，  
你要么忽略它，要么有清晰逻辑，不要让行为混乱。

---

## 今天结束后的验收标准

- 你能区分基础过滤、搜索、排序、分页分别负责什么
- 你会用 `request.query_params`
- 你能在 `ViewSet` 上接入 `SearchFilter` 和 `OrderingFilter`
- 你能给列表接口接上分页
- 你能测试多条件组合查询
- 你能解释为什么列表接口是 API 工程化里非常重要的一环

---

## 今天的复盘问题

建议你写下这 3 个问题的答案：

1. 为什么分页应该尽早接入，而不是等数据量大了再说？
2. 哪些过滤更适合写在 `get_queryset()`，哪些更适合交给 DRF 过滤后端？
3. 你现在的列表接口，和 Day 8 那版相比，最大的工程化提升是什么？

---

## 明天会学什么

明天我们要做 DRF 这一阶段的收尾：

- 异常处理
- API 测试
- Schema / OpenAPI 基础认识
- 项目收尾与总结

也就是说，明天会把这套 DRF 学习线从“功能实现”推进到：

> “更像一个真正可维护、可验证、可说明的 API 项目。”
