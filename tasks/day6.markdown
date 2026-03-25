# Day 6 任务清单：学会写测试，补上安全意识，让接口不只是“能跑”

## 今天的目标

前 5 天你已经完成了这些事情：

- 项目能启动
- 模型和迁移已经有了
- Admin 能用
- 原生 JSON 接口已经有了
- 登录、Session 和权限也接进来了
- 列表接口也开始支持查询参数、中间件和 async 了

现在项目已经不像 demo 了，但还有一个很关键的问题：

> 你现在知道接口“现在能跑”，但你还不能确定它在以后改动之后会不会悄悄坏掉。

所以 Day 6 的目标非常明确：

> 学会用 Django 自带测试工具给项目加安全网，同时理解你当前接口里哪些安全处理只是“学习阶段的简化”，哪些在真实项目里必须认真对待。

今天结束后，你应该做到这些事：

- 知道 Django 测试的基本工作方式
- 会写模型测试和接口测试
- 会测试登录限制和作者权限
- 会测试非法 JSON 和异常输入
- 知道 `force_login()` 为什么对测试特别好用
- 理解 `csrf_exempt` 的风险边界

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 文档阅读 | 45 分钟 | 阅读测试和安全文档 |
| 测试骨架 | 45 分钟 | 搭好测试数据、测试类和基础辅助函数 |
| 编写测试 | 90 分钟 | 为模型、接口、认证和权限写测试 |
| 安全复盘 | 60 分钟 | 理解 `csrf_exempt`、权限边界和失败场景 |

---

## 今天的官方文档入口

- 测试概览：https://docs.djangoproject.com/zh-hans/6.0/topics/testing/
- 编写并运行测试：https://docs.djangoproject.com/zh-hans/6.0/topics/testing/overview/
- 安全概览：https://docs.djangoproject.com/zh-hans/6.0/topics/security/
- CSRF 保护：https://docs.djangoproject.com/zh-hans/6.0/ref/csrf/

建议阅读顺序：

1. 先看测试概览
2. 再看如何运行测试
3. 再看安全概览
4. 最后看 CSRF

今天最重要的不是把所有安全细节记全，而是建立两个意识：

- 接口不是“返回 200 就算没问题”
- 学习阶段的简化写法，到了真实项目里一定要重新审视

---

## 先看一下你当前项目状态

根据你现在的项目：

- `notes/tests.py` 还是默认空文件
- 你的接口已经有：
  - CRUD
  - 登录登出
  - `api_me`
  - 权限判断
  - 中间件
- 你的部分 JSON 接口上用了 `@csrf_exempt`

这说明 Day 6 的任务非常明确：

- 把“没有测试”的状态补上
- 开始确认你的接口是否真的符合预期
- 明确哪些安全处理只是现在为了学习方便而做的折中

---

## 今天你必须先理解的 8 个概念

## 1. 为什么测试不是“最后再补”

很多人一开始会觉得：

- 功能先写出来
- 测试以后再说

但真实情况是：

- 项目越往后，逻辑越多
- 权限分支越多
- 一次改动影响的地方越多

如果不尽早补测试，你后面每改一处都会越来越不放心。

你今天就会很明显感受到：

- 光是 Day 4 的登录和权限逻辑，就已经有不少分支了

这种时候测试就特别值钱。

## 2. Django 的测试不是跑真实生产库

这是一个非常重要的基本认知。

当你运行：

```powershell
python manage.py test
```

Django 会：

- 创建一个测试数据库
- 在测试数据库里跑迁移
- 执行测试
- 测试结束后把测试数据库清掉

所以你一般不用担心：

- 把自己真实开发数据删掉

这也是 Django 测试上手体验比较好的地方。

## 3. `TestCase` 是什么

`TestCase` 是 Django 最常用的测试基类之一。

你可以先把它理解成：

> 帮你准备好数据库隔离、测试环境和很多常用测试能力的一个基础类。

大多数入门和中小项目测试，先用它就很够了。

## 4. Django Test Client 是什么

它不是浏览器，但你可以把它先理解成：

> Django 自带的一个“模拟 HTTP 请求的工具”。

它可以帮你做这些事：

- 请求接口
- 提交 JSON
- 保留登录态
- 看响应状态码
- 看响应 JSON

它特别适合测试你现在这种后端接口。

## 5. `force_login()` 为什么特别适合测试

在真实业务里，用户登录通常会走：

- 用户名
- 密码
- Session

但在测试里，如果你每次都先调登录接口，会很啰嗦，也会让测试关注点变散。

所以 Django 提供了 `force_login()`：

> 直接让这个测试客户端处于“已登录某个用户”的状态。

它的价值在于：

- 写测试更快
- 测试目标更纯粹
- 不需要每个测试都先走一遍登录流程

## 6. 为什么权限测试一定要分“未登录”和“非作者”

这是 Day 6 特别值得练的地方。

因为这两种失败不是一回事：

- 未登录：应该是 `401`
- 已登录但不是作者：应该是 `403`

如果你不测，很容易以后改着改着把这两个情况混掉。

## 7. 什么叫“失败测试”

很多初学者只写“成功时返回 200”。

但真实项目里，更有价值的往往是这些测试：

- 非法 JSON
- 主键不存在
- 未登录访问
- 权限不足
- 参数类型错误

因为现实里的 bug，很多都出在这些边界场景里。

## 8. `csrf_exempt` 为什么值得今天专门复盘

你前面为了学习 JSON 接口处理流程，使用了 `@csrf_exempt`。

这在学习阶段是合理的，因为它帮你先绕开了一个干扰点。

但今天你必须知道：

- 它不是“推荐长期这么用”
- 它只是“为了先把主线跑通”

尤其如果你用的是：

- Session 登录
- 浏览器环境
- 会自动带 Cookie 的客户端

那 CSRF 就绝对不能长期忽略。

---

## 今天建议先写哪些测试

今天建议你至少写 6 类测试：

- 模型测试
- 列表接口测试
- 创建接口测试
- 登录限制测试
- 作者权限测试
- 非法 JSON 测试

这 6 类已经能覆盖你当前项目最关键的风险点。

---

## 任务 1：先把 `notes/tests.py` 变成真正的测试文件

### 1.1 当前现状

你现在的 `notes/tests.py` 还是默认空文件。

今天建议你先在这个文件里按功能分成两大块：

- 模型测试
- 接口测试

你现在还不一定需要立刻拆成 `tests/` 目录包。

先在一个文件里写清楚，学习成本最低。

### 1.2 建议先导入这些内容

```python
import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Note, Tag
```

### 1.3 为什么这里要导入 `reverse`

因为测试里尽量不要把 URL 硬编码成字符串。

比如相比这样：

```python
"/api/notes/"
```

更推荐这样：

```python
reverse("api_note_list")
```

这样以后如果你改了路由路径，但名字没改，测试代码就不用到处改。

---

## 任务 2：先写测试数据准备逻辑

今天最省力的方式，是先在测试类里一次性准备好常用数据。

### 2.1 推荐结构

```python
class BaseApiTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.author = User.objects.create_user(
            username="author",
            password="password123",
        )
        cls.other_user = User.objects.create_user(
            username="other",
            password="password123",
        )

        cls.tag_python = Tag.objects.create(name="Python")
        cls.tag_django = Tag.objects.create(name="Django")

        cls.note = Note.objects.create(
            author=cls.author,
            title="First Note",
            content="This is the first note.",
            status=Note.STATUS_PUBLISHED,
        )
        cls.note.tags.set([cls.tag_python, cls.tag_django])

    def setUp(self):
        self.client = Client()
```

### 2.2 这里你要看懂什么

#### `setUpTestData`

是“类级别”的初始化。

适合放那些：

- 所有测试都能共用
- 不需要每个测试都重新建一次

这样测试跑起来会更省时间。

#### `setUp`

是“每个测试方法执行前”都会跑一次。

这里很适合放：

- `self.client = Client()`

---

## 任务 3：先写模型测试

模型测试不需要写很多，但至少写一点“最值得保护”的行为。

### 3.1 建议先测什么

- `__str__` 是否符合预期
- 默认状态是否生效
- 关系字段是否正常

### 3.2 推荐测试示例

```python
class NoteModelTests(BaseApiTestCase):
    def test_note_str_returns_title(self):
        self.assertEqual(str(self.note), "First Note")

    def test_note_default_status_is_draft(self):
        note = Note.objects.create(
            author=self.author,
            title="Draft Note",
            content="Draft content",
        )
        self.assertEqual(note.status, Note.STATUS_DRAFT)

    def test_note_can_have_tags(self):
        self.assertEqual(self.note.tags.count(), 2)
```

### 3.3 为什么模型测试不能省

因为模型看起来稳定，但实际上只要你以后改：

- 默认值
- 关系字段
- `__str__`
- 排序

就很容易影响：

- Admin 显示
- 查询逻辑
- 接口返回

所以模型测试虽然简单，但很值得有。

---

## 任务 4：写列表接口测试

列表接口是整个系统最基础的读接口，很适合作为第一类 API 测试。

### 4.1 推荐测试示例

```python
class NoteApiTests(BaseApiTestCase):
    def test_note_list_returns_200(self):
        response = self.client.get(reverse("api_note_list"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("results", payload)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["title"], "First Note")
```

### 4.2 这里你要看什么

不要只看：

- 返回是不是 200

还要看：

- JSON 结构对不对
- 关键字段在不在
- 数据内容是不是你预期的

这才叫真正意义上的接口测试。

---

## 任务 5：写创建接口测试

创建接口现在已经有登录限制，所以它非常适合同时测试：

- 正常创建
- 未登录失败
- 数据是否真的写进数据库

### 5.1 推荐成功测试

```python
    def test_logged_in_user_can_create_note(self):
        self.client.force_login(self.author)

        payload = {
            "title": "New Note",
            "content": "New content",
            "status": "published",
            "tag_ids": [self.tag_python.id],
        }

        response = self.client.post(
            reverse("api_note_create"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Note.objects.count(), 2)

        new_note = Note.objects.get(title="New Note")
        self.assertEqual(new_note.author, self.author)
```

### 5.2 这里最值得观察的一点

你不仅要测：

- 接口返回成功

更要测：

- 数据是否真的落库
- 作者是不是自动绑定成当前登录用户

这正好能验证 Day 4 做的权限逻辑有没有真的生效。

---

## 任务 6：写“未登录不能创建”的测试

这类测试非常重要，因为它验证的是“保护逻辑”。

### 6.1 推荐测试示例

```python
    def test_create_note_requires_login(self):
        payload = {
            "title": "Unauthorized Note",
            "content": "Should fail",
            "status": "published",
            "tag_ids": [self.tag_python.id],
        }

        response = self.client.post(
            reverse("api_note_create"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "authentication required")
```

### 6.2 为什么这个测试很值钱

因为这种“保护逻辑”最容易在重构时被不小心打破。

比如以后你改了辅助函数、改了装饰器、改了接口流程，这种测试能第一时间提醒你：

- 权限门没了

---

## 任务 7：写作者权限测试

这是今天最关键的一组测试之一。

你要验证：

- 作者本人可以修改
- 非作者不能修改
- 作者本人可以删除
- 非作者不能删除

### 7.1 推荐测试示例：非作者不能修改

```python
    def test_non_owner_cannot_update_note(self):
        self.client.force_login(self.other_user)

        payload = {
            "title": "Hacked Title"
        }

        response = self.client.patch(
            reverse("api_note_update", kwargs={"pk": self.note.pk}),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "First Note")
```

### 7.2 推荐测试示例：作者本人可以修改

```python
    def test_owner_can_update_note(self):
        self.client.force_login(self.author)

        payload = {
            "title": "Updated Title"
        }

        response = self.client.patch(
            reverse("api_note_update", kwargs={"pk": self.note.pk}),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Updated Title")
```

### 7.3 这里你要理解的事情

权限测试的重点不是“接口返回了什么话术”，而是：

- 不该改的数据有没有真的被改掉

所以像 `refresh_from_db()` 这种动作很重要。

它能帮你确认：

- 数据库里的真实状态有没有变化

---

## 任务 8：写非法 JSON 测试

这是 Day 6 特别值得加的一类测试，因为它能验证你的接口是不是对异常输入足够稳。

### 8.1 推荐测试示例

```python
    def test_create_note_with_invalid_json_returns_400(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse("api_note_create"),
            data="{invalid json}",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "invalid json")
```

### 8.2 为什么这类测试非常有价值

因为现实中客户端不一定永远按你预期发请求。

有时是：

- 格式错了
- 字段少了
- 内容不是合法 JSON

如果你只测成功路径，那你根本不知道接口面对脏输入时会不会炸掉。

---

## 任务 9：给登录接口和 `api_me` 也补一点测试

既然你已经有认证逻辑，那今天至少补一两条最基础的测试。

### 9.1 推荐测试：登录成功

```python
    def test_login_success(self):
        response = self.client.post(
            reverse("api_login"),
            data=json.dumps({
                "username": "author",
                "password": "password123",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["username"], "author")
```

### 9.2 推荐测试：未登录访问 `api_me`

```python
    def test_api_me_requires_login(self):
        response = self.client.get(reverse("api_me"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "authentication required")
```

---

## 任务 10：把这些测试组织成比较清楚的结构

今天建议你的 `notes/tests.py` 最终至少长成这样：

```python
import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Note, Tag


class BaseApiTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        ...

    def setUp(self):
        self.client = Client()


class NoteModelTests(BaseApiTestCase):
    ...


class NoteApiTests(BaseApiTestCase):
    ...
```

### 为什么这样组织比较好

因为你以后测试会越来越多。

如果从一开始就按：

- 基础测试数据
- 模型测试
- 接口测试

这种结构拆开，后面维护起来会轻松很多。

---

## 任务 11：运行测试并学会看结果

运行命令：

```powershell
python manage.py test notes
```

如果你只想跑单个 app，这样已经够了。

### 你今天要学会观察什么

- 一共跑了多少条测试
- 有没有失败
- 哪一条失败
- 失败是断言失败，还是代码抛异常

如果某条测试失败，不要只看“失败了”，要看：

- 断言期望值是什么
- 实际拿到的值是什么

这就是测试真正开始发挥价值的地方。

---

## 任务 12：今天必须把 CSRF 讲明白

前面几天你为了快速跑通 JSON 接口，很多视图上用了：

```python
@csrf_exempt
```

这是可以理解的，但今天你必须知道这意味着什么。

## 12.1 什么是 CSRF

你可以先用非常朴素的方式理解：

> 一个恶意网站诱导用户在“已经登录你的网站”的情况下，替用户偷偷发起危险请求。

比如：

- 删除数据
- 修改资料
- 发起转账

这类问题通常和：

- 浏览器自动带 Cookie

关系特别大。

## 12.2 为什么你现在的项目值得认真想这件事

因为你目前的认证方式是：

- Django Session

而 Session 通常配合 Cookie 使用。

这就意味着：

- 如果以后你的接口真的被浏览器前端直接调用
- 那么 `csrf_exempt` 就不能长期随便保留

## 12.3 那为什么前几天又暂时用了它

因为学习阶段，你先要理解：

- 请求怎么进来
- JSON 怎么解析
- `request.user` 怎么工作

如果一上来就被 CSRF 卡住，主线会断掉。

所以 Day 3 和 Day 4 的 `csrf_exempt` 是一种“教学上的减负”，不是长期推荐方案。

---

## 任务 13：理解 Django 测试客户端和 CSRF 的一个关键细节

这是 Day 6 很容易被忽略，但特别值得知道的一点：

> Django 测试客户端默认不会严格执行 CSRF 检查。

也就是说：

- 你写的测试能通过
- 不代表真实浏览器环境下就没有 CSRF 问题

如果你真的想测试 CSRF，可以显式这样创建客户端：

```python
client = Client(enforce_csrf_checks=True)
```

今天你不用把 CSRF 测试写得很深，但一定要知道这个细节，否则很容易对自己的安全状况产生误判。

---

## 任务 14：今天建议你重点复盘哪些安全问题

至少思考下面这些点：

- 哪些接口是读接口，哪些是改数据接口
- 哪些接口当前用了 `csrf_exempt`
- 如果这些接口未来由浏览器前端直接调用，会有什么风险
- 当前权限逻辑有没有可能被越权
- 当前错误信息是不是足够明确，但又没有泄露太多内部细节

你今天不一定要一次性把所有安全问题都修完，但你必须开始有这个意识。

---

## 今天你必须真正理解的 5 条测试/安全链路

## 1. 成功链路测试

- 正常请求
- 正常返回
- 数据真的写入或更新

## 2. 未登录链路测试

- 不登录
- 请求受保护接口
- 返回 `401`

## 3. 权限不足链路测试

- 登录为其他用户
- 操作不属于自己的资源
- 返回 `403`

## 4. 脏输入链路测试

- 非法 JSON
- 缺失字段
- 参数类型错误
- 返回 `400`

## 5. 安全边界复盘链路

- 看当前是否使用了简化方案
- 判断这些方案是不是只适合学习阶段
- 标记哪些地方以后必须升级

如果你把这 5 条链路理解透了，Day 6 的核心就基本稳了。

---

## 今天不需要做什么

为了让 Day 6 聚焦，你今天先不要展开这些内容：

- 不需要上 pytest 插件生态
- 不需要做覆盖率报表
- 不需要一次性做很复杂的集成测试
- 不需要马上把所有 `csrf_exempt` 全删掉
- 不需要上 DRF 的测试工具

今天最重要的是：

- 先学会用 Django 自带能力把核心逻辑测起来

---

## 常见报错和排查方法

## 1. 测试里明明登录了，接口还是返回 `401`

通常说明：

- 你忘了 `force_login()`
- 或测试客户端不是同一个实例

先检查：

- `self.client.force_login(self.author)` 有没有写
- 请求是不是用 `self.client` 发的

## 2. PATCH/DELETE 测试怎么写总是怪怪的

通常说明：

- 你忘了传 `content_type="application/json"`
- 或数据没先 `json.dumps(...)`

## 3. 测试数据互相污染

如果你发现：

- 前一个测试创建的数据影响了后一个测试

先不要慌，通常是你对测试生命周期理解还不够。

`TestCase` 本身会帮你做数据库隔离。  
大多数情况下，问题更可能是：

- 你用了类级数据，但没意识到哪些测试会修改它

这时可以用：

```python
self.note.refresh_from_db()
```

来确认数据库中的真实状态。

## 4. 你觉得测试很啰嗦

这是非常正常的感觉。

因为测试一开始确实会让你觉得：

- 写得比业务代码还慢

但只要你经历过一次“改了代码，测试第一时间告诉你哪里坏了”，你就会马上感受到它的价值。

---

## 今天的交付标准

今天结束前，你至少应该完成这些事：

- [ ] 在 `notes/tests.py` 中建立基础测试结构
- [ ] 写至少 1 条模型测试
- [ ] 写列表接口测试
- [ ] 写创建接口测试
- [ ] 写未登录访问受保护接口测试
- [ ] 写非作者修改资源测试
- [ ] 写非法 JSON 测试
- [ ] 运行 `python manage.py test notes`
- [ ] 至少修掉 1 个你在测试中暴露出来的问题
- [ ] 说清楚 `csrf_exempt` 在当前项目里为什么只是学习阶段的简化

只要这些都完成，Day 6 就算达标。

---

## 今天结束后，项目里通常会改动哪些位置

今天最核心的文件会是：

```text
notes/
└─ tests.py
```

如果你顺手根据测试结果修了代码，也可能会碰到：

```text
notes/
├─ views.py
└─ utils.py
```

但 Day 6 的核心战场，一定是测试文件。

---

## 今日复盘问题

今天结束后，试着不用看文档，自己回答下面这些问题：

1. Django `TestCase` 和普通 Python 单元测试最大的区别是什么？
2. `force_login()` 为什么特别适合测试受保护接口？
3. 为什么测试不能只测成功情况？
4. `401` 和 `403` 的测试逻辑有什么不同？
5. 为什么 `csrf_exempt` 在学习阶段可以用，但真实项目里要谨慎？
6. 为什么“测试通过”不等于“已经完全安全”？

如果你能比较顺畅地回答这些问题，说明你已经开始从“会写功能”进化到“会保护功能”了。

---

## 可选加分任务

如果你今天状态不错，可以多做两个增强：

### 加分任务 1：给列表接口的过滤和分页写测试

比如：

- `status=published`
- `page=1&page_size=1`

这会帮你把 Day 5 的成果也稳住。

### 加分任务 2：尝试写一个开启 CSRF 检查的测试客户端

例如：

```python
client = Client(enforce_csrf_checks=True)
```

然后观察：

- 你的 `csrf_exempt` 到底绕过了什么

这会让你对 Django 的安全机制理解得更深。

---

## 一句总结今天学了什么

今天你真正学会的不是“多写了几条断言”，而是：

> 你开始给自己的 Django 后端加安全网了，也第一次认真区分了“为了学习方便能先这么写”和“真实项目里必须认真对待”的边界。

这一关打通之后，Day 7 去看部署和优化，你会更像是在完成一个真正可交付的后端项目。
