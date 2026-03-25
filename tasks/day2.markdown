# Day 2 任务清单：学会 Django 的模型、迁移和 Admin 后台

## 今天的目标

Day 1 你已经把 Django 项目跑起来了，今天开始真正接触 Django 最核心的一块能力：

- 模型（Model）
- 迁移（Migration）
- 后台管理（Admin）

如果说 Day 1 是让 Django “能跑”，那么 Day 2 就是让 Django “开始管理真实数据”。

今天结束后，你应该做到这些事：

- 知道 Django 的模型是干什么的
- 能在 `notes/models.py` 里写出自己的数据模型
- 能执行 `makemigrations` 和 `migrate`
- 能理解“模型代码”是怎么变成“数据库表”的
- 能进入 Django Admin 后台管理数据
- 能用 ORM 做几条最基础的查询

---

## 先用一句话理解今天在干什么

今天你要学会的是这条主线：

> 我先在 Python 代码里定义数据结构，然后 Django 帮我把这份定义同步到数据库里，最后我可以通过后台和代码去操作这些数据。

这条主线是 Django 开发的核心体验之一。

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 45 分钟 | 看官方文档，先搞懂模型、迁移、Admin 各自是做什么的 |
| 设计模型 | 60 分钟 | 在 `notes/models.py` 写出项目的 3 个核心模型 |
| 迁移与验证 | 45 分钟 | 执行迁移，让数据库真正生成表结构 |
| 后台管理 | 45 分钟 | 注册 Admin，创建超级用户，录入测试数据 |
| ORM 练习与复盘 | 45 分钟 | 在 shell 中练 ORM，写下今天理解到的关键点 |

---

## 今天的官方文档入口

- 教程第 2 部分：https://docs.djangoproject.com/zh-hans/6.0/intro/tutorial02/
- 模型：https://docs.djangoproject.com/zh-hans/6.0/topics/db/models/
- 执行查询：https://docs.djangoproject.com/zh-hans/6.0/topics/db/queries/
- 迁移：https://docs.djangoproject.com/zh-hans/6.0/topics/migrations/
- Admin site：https://docs.djangoproject.com/zh-hans/6.0/ref/contrib/admin/

建议阅读顺序：

1. 先看教程第 2 部分
2. 再看模型文档
3. 写代码时回查迁移文档
4. 最后看 Admin 文档

今天不要追求把文档全部读完，重点是边做边理解。

---

## 开始前先确认这几件事

在当前项目根目录下，你应该已经有这些内容：

- `manage.py`
- `studynotes/`
- `notes/`
- `db.sqlite3`

另外，你的 `studynotes/settings.py` 里应该已经把 `notes` 加进了 `INSTALLED_APPS`。

如果这一步没做，今天后面的模型和迁移都跑不通。

---

## 先理解 3 个最重要的概念

## 1. 什么是 Model

Model 就是“用 Python 类来描述数据表”。

你可以先把它理解成：

- 你写一个 Python 类
- Django 根据这个类去创建数据库表
- 以后你就可以用 Python 操作数据库，而不需要手写很多 SQL

比如：

- 一个 `Note` 模型，通常就会对应一张“笔记表”
- 一个 `Tag` 模型，通常就会对应一张“标签表”
- 一个 `Comment` 模型，通常就会对应一张“评论表”

## 2. 什么是 Migration

Migration 可以理解成“数据库结构变更记录”。

它的作用是：

- 记录你的模型改了什么
- 告诉 Django 应该如何修改数据库表

你可以把它理解成数据库结构的“版本记录”。

最常见的两步是：

```powershell
python manage.py makemigrations
python manage.py migrate
```

它们的区别一定要记住：

- `makemigrations`：根据你的模型改动，生成迁移文件
- `migrate`：真正把迁移文件应用到数据库

## 3. 什么是 Admin

Admin 是 Django 自带的后台管理系统。

它的特点是：

- 开箱即用
- 非常适合内部管理数据
- 不需要你自己从零写一套管理界面

它并不是给普通用户看的前台页面，而更像一个“开发期和运营期都很实用的后台工具”。

---

## 今天要做的小项目数据设计

今天我们围绕 `StudyNotes` 这个项目，建立 3 个最基础的模型：

- `Tag`：标签
- `Note`：笔记
- `Comment`：评论

### 为什么这样设计

因为这 3 个模型刚好能覆盖 Django 中最常见的关系：

- `ForeignKey`：外键，一对多
- `ManyToManyField`：多对多

具体关系如下：

- 一个用户可以写很多篇笔记
- 一篇笔记可以有多个标签
- 一篇笔记可以有很多评论

这套设计不复杂，但足够你练会 Day 2 的核心内容。

---

## 任务 1：在 `notes/models.py` 里编写 3 个模型

### 1.1 先想清楚每个模型要存什么

#### `Tag`

标签不需要太复杂，先放这些字段：

- `name`：标签名
- `created_at`：创建时间

#### `Note`

笔记是核心模型，建议先放这些字段：

- `author`：作者
- `title`：标题
- `content`：正文
- `status`：状态，草稿或已发布
- `tags`：标签
- `created_at`：创建时间
- `updated_at`：更新时间

#### `Comment`

评论先做最基础版本：

- `note`：属于哪篇笔记
- `author_name`：评论者名字
- `content`：评论内容
- `created_at`：创建时间

### 1.2 为什么 `Note.author` 推荐写成 `settings.AUTH_USER_MODEL`

因为这样更稳妥。

你可以先把它理解成：

- 不要把用户模型写死为 Django 默认 `User`
- 优先通过 Django 的配置拿到“当前项目的用户模型”

这样即使以后你自定义用户模型，也不容易返工。

### 1.3 推荐代码

把 `notes/models.py` 改成下面这样：

```python
from django.conf import settings
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Note(models.Model):
    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    tags = models.ManyToManyField(Tag, related_name="notes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author_name = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author_name} - {self.note.title}"
```

### 1.4 这段代码你要看懂什么

你今天不需要背所有字段类型，但至少要看懂下面这些：

#### `CharField`

存短文本，比如标题、标签名、用户名。

#### `TextField`

存长文本，比如笔记正文、评论内容。

#### `DateTimeField`

存时间。

- `auto_now_add=True`：创建时自动填时间
- `auto_now=True`：每次保存时自动更新时间

#### `ForeignKey`

表示一对多关系。

比如：

- 一个 `Note` 属于一个作者
- 一个 `Comment` 属于一篇 `Note`

#### `ManyToManyField`

表示多对多关系。

比如：

- 一篇笔记可以有多个标签
- 一个标签也可以属于多篇笔记

#### `__str__`

这是给后台和 shell 看的人类可读展示。

如果你不写，后台里很可能只会看到：

```text
Tag object (1)
Note object (1)
```

这样非常不方便。

---

## 任务 2：生成迁移文件

模型写完以后，不代表数据库已经有对应表了。

你还需要告诉 Django：

“我刚刚修改了模型，请帮我生成数据库变更记录。”

### 2.1 执行 `makemigrations`

```powershell
python manage.py makemigrations
```

如果成功，你通常会看到类似：

```text
Migrations for 'notes':
  notes\migrations\0001_initial.py
```

### 2.2 这一步做了什么

这一步不会直接改数据库。

它做的是：

- 比较你现在的模型定义
- 自动生成一个迁移文件
- 告诉 Django“下一步该怎么改数据库”

### 2.3 去看看迁移文件

你可以打开：

```text
notes/migrations/0001_initial.py
```

先不用完全看懂，但你要知道：

- 这不是随便生成的垃圾文件
- 它是数据库结构变更记录
- 后续你改模型，新的迁移文件会继续往下加

---

## 任务 3：把迁移真正应用到数据库

### 3.1 执行 `migrate`

```powershell
python manage.py migrate
```

### 3.2 这一步做了什么

这一步会真正修改数据库。

换句话说：

- `makemigrations` 是“写施工图”
- `migrate` 是“按施工图开工”

### 3.3 完成后你应该理解

从今天开始，你的数据库里就不只是 Django 自带的那些表了，还会有你 `notes` app 对应的表。

这说明你的业务模型已经真正进入数据库系统了。

---

## 任务 4：创建超级用户，准备进入后台

### 4.1 创建管理员账号

执行：

```powershell
python manage.py createsuperuser
```

然后按提示输入：

- 用户名
- 邮箱
- 密码

如果你只是本地学习，密码简单一点也行，但不要在真实项目里这么做。

### 4.2 为什么今天就要建超级用户

因为你接下来要体验 Django 最方便的一块：

- 不写后台页面
- 直接通过 Admin 管理数据

这对学习 Django 特别重要，因为它能让你很快看到模型的价值。

---

## 任务 5：把模型注册到 Django Admin

### 5.1 修改 `notes/admin.py`

把文件改成下面这样：

```python
from django.contrib import admin

from .models import Comment, Note, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "status", "created_at")
    list_filter = ("status", "created_at", "tags")
    search_fields = ("title", "content")
    filter_horizontal = ("tags",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author_name", "note", "created_at")
    search_fields = ("author_name", "content")
```

### 5.2 为什么不只写 `admin.site.register(...)`

你当然可以只注册模型，但今天建议你直接学一点最常用的后台增强：

- `list_display`
- `search_fields`
- `list_filter`

这样你进后台时能明显感受到：

- 数据更好看了
- 查找更方便了
- Django Admin 不是“只能凑合用”，而是真的很实用

### 5.3 这几个配置分别是什么意思

#### `list_display`

决定后台列表页显示哪些列。

#### `search_fields`

决定后台搜索框可以搜哪些字段。

#### `list_filter`

决定右侧筛选栏有哪些筛选条件。

#### `filter_horizontal`

适合多对多字段，在后台编辑时体验更好。

---

## 任务 6：启动后台并录入第一批数据

### 6.1 启动服务

```powershell
python manage.py runserver
```

### 6.2 打开后台

浏览器访问：

```text
http://127.0.0.1:8000/admin/
```

然后使用刚刚创建的超级用户登录。

### 6.3 你现在应该能看到

除了 Django 自带的用户、组之外，还应该能看到：

- Tags
- Notes
- Comments

### 6.4 手动录入一些测试数据

建议先手动创建：

- 2 个标签
- 1 篇笔记
- 2 条评论

你录入后，可以观察这些事情：

- `Note.author` 会不会正常关联用户
- `Note.tags` 的多对多选择框能不能用
- 列表页展示是不是比默认更清晰

---

## 任务 7：用 Django shell 练习最基础的 ORM 查询

Admin 是图形界面，shell 是代码视角。

这两者都要会一点。

### 7.1 进入 shell

```powershell
python manage.py shell
```

### 7.2 先导入模型

```python
from django.contrib.auth import get_user_model
from notes.models import Comment, Note, Tag
```

### 7.3 看看现有数据

```python
Tag.objects.all()
Note.objects.all()
Comment.objects.all()
```

### 7.4 如果你已经创建了超级用户，可以这样拿到用户

```python
User = get_user_model()
user = User.objects.first()
user
```

### 7.5 如果你想在 shell 里创建一篇笔记

```python
note = Note.objects.create(
    author=user,
    title="My first Django note",
    content="Today I learned models, migrations and admin.",
    status="published",
)
```

### 7.6 创建标签并关联到笔记

```python
python_tag = Tag.objects.create(name="Python")
django_tag = Tag.objects.create(name="Django")

note.tags.add(python_tag, django_tag)
```

### 7.7 创建评论

```python
Comment.objects.create(
    note=note,
    author_name="Alice",
    content="Great note!",
)
```

### 7.8 再查一遍

```python
Note.objects.all()
note.tags.all()
note.comments.all()
```

### 7.9 你今天至少要看懂这些 ORM 操作

- `.all()`
- `.create()`
- `.first()`
- 多对多的 `.add()`
- 反向关系的 `.comments.all()`

这已经够 Day 2 使用了，不需要一口气学太多。

---

## 今天你必须搞懂的一条链路

请你反复看懂这条链路：

1. 我在 `models.py` 里写模型
2. 我执行 `makemigrations`
3. Django 生成迁移文件
4. 我执行 `migrate`
5. 数据库生成或更新表
6. 我可以在 Admin 和 ORM 里操作这些数据

只要你把这 6 步理解透了，Django 的数据层就算真正入门了。

---

## 常见错误和排查方法

### 1. `No changes detected`

通常说明：

- 你改的模型没保存
- `notes` 没有加入 `INSTALLED_APPS`
- 你修改的不是正确的 `models.py`

排查顺序：

1. 看 `notes/models.py` 是否真的改了
2. 看 `studynotes/settings.py` 里是否有 `notes`
3. 再运行一次 `makemigrations`

### 2. `no such table`

通常说明：

- 你写了模型，但没有执行 `migrate`

解决方法：

```powershell
python manage.py migrate
```

### 3. 后台里看不到你的模型

通常说明：

- 没有在 `admin.py` 注册模型

先检查：

- `notes/admin.py` 是否导入了模型
- 是否写了注册代码

### 4. 创建 `Note` 时提示作者不能为空

说明你的 `author` 是必填字段。

解决方法：

- 先创建用户
- 再把用户赋给 `Note.author`

### 5. 多对多字段不能直接在 `create()` 里像普通字段一样赋值

这很常见。

建议记住一个简单规则：

- 先创建对象
- 再用 `.add()` 绑定多对多关系

---

## 今天的交付标准

今天结束前，你至少应该完成这些事：

- [ ] 在 `notes/models.py` 中写出 `Tag`、`Note`、`Comment`
- [ ] 理解 `ForeignKey` 和 `ManyToManyField` 的基本含义
- [ ] 成功执行 `python manage.py makemigrations`
- [ ] 成功执行 `python manage.py migrate`
- [ ] 成功创建超级用户
- [ ] 在 `notes/admin.py` 中注册模型
- [ ] 能登录 `/admin/`
- [ ] 能在后台创建标签、笔记、评论
- [ ] 能在 shell 中完成一次最基础的查询

只要这些都完成，Day 2 就算达标。

---

## 今天结束后你应该看到的文件变化

今天完成后，项目里通常会新增或变化这些位置：

```text
notes/
├─ admin.py
├─ models.py
└─ migrations/
   └─ 0001_initial.py
```

数据库文件 `db.sqlite3` 也会发生变化，因为你真的往里面写入了表结构。

---

## 今日复盘问题

今天结束后，试着不用看文档，自己回答下面这些问题：

1. Django Model 和数据库表是什么关系？
2. `makemigrations` 和 `migrate` 到底有什么区别？
3. 为什么 `Note.author` 推荐写成 `settings.AUTH_USER_MODEL`？
4. `ForeignKey` 和 `ManyToManyField` 分别适合什么场景？
5. 为什么注册 Admin 之后就能在后台管理数据？
6. 如果模型改了但是数据库没变，你该先检查什么？

如果你能比较顺畅地回答这些问题，Day 2 的核心就已经吃透了。

---

## 一句总结今天学了什么

今天你真正学会的不是“创建了几张表”，而是：

> 你已经掌握了 Django 最核心的数据开发流程：写模型、生成迁移、同步数据库、通过 Admin 和 ORM 操作数据。

从今天开始，这个项目才真正进入“有业务数据”的阶段。
