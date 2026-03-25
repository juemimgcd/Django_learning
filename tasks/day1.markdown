# Day 1 任务清单：搭建 Django 项目骨架并跑通第一个页面

## 今天的目标

今天不是为了“写很多功能”，而是为了把 Django 项目的最小闭环跑通。

你今天完成后，应该做到这几件事：

- 知道 Django 里的 `project` 和 `app` 分别是什么
- 能在本地创建并启动一个 Django 项目
- 能写出最简单的视图函数
- 能把 URL 和视图关联起来
- 能访问这 3 个页面：
  - `/`
  - `/health/`
  - `/api/ping/`

如果你今天只完成上面这些，其实就已经很不错了，因为你已经真正把 Django “跑起来”了。

---

## 今天建议投入时间

总时长建议：`4 小时`

| 时间段 | 建议时长 | 要做什么 |
| --- | --- | --- |
| 准备环境 | 30 分钟 | 检查 Python、创建虚拟环境、安装 Django |
| 学基础概念 | 30 分钟 | 理解 `project`、`app`、`settings`、`urls`、`views` |
| 实际动手 | 2 小时 | 创建项目、创建 app、写页面、配置路由 |
| 运行和排错 | 30 分钟 | 启动服务、访问页面、修复报错 |
| 复盘总结 | 30 分钟 | 记下今天学会的概念和命令 |

---

## 先理解两个核心概念

### 1. 什么是 project

你可以把 `project` 理解成“整个网站的总配置中心”。

它通常负责这些事情：

- 整个项目的配置
- 总路由
- 数据库配置
- 中间件配置
- 已安装应用列表

简单说，`project` 决定“这个网站整体怎么运行”。

### 2. 什么是 app

你可以把 `app` 理解成“一个具体的业务模块”。

比如一个网站可能会有这些 app：

- `notes`：笔记模块
- `users`：用户模块
- `comments`：评论模块

简单说，`app` 决定“这个功能模块做什么”。

### 3. 一句话理解它们的关系

- `project` 是总工程
- `app` 是工程里的功能模块

如果你有 FastAPI 经验，可以这样类比：

- Django 的 `project` 有点像“全局配置 + 主入口”
- Django 的 `app` 有点像“按业务拆分后的模块目录”

但要注意，Django 的组织方式比 FastAPI 更强调“约定”和“内建结构”。

---

## Day 1 官方文档入口

- Django 6.0 中文文档首页：https://docs.djangoproject.com/zh-hans/6.0/
- 教程第 1 部分：https://docs.djangoproject.com/zh-hans/6.0/intro/tutorial01/
- Django 配置：https://docs.djangoproject.com/zh-hans/6.0/topics/settings/
- URL 调度器：https://docs.djangoproject.com/zh-hans/6.0/topics/http/urls/
- 编写视图：https://docs.djangoproject.com/zh-hans/6.0/topics/http/views/

今天的建议是：先快速看教程第 1 部分，再边做边查文档，不要一口气把所有文档看完。

---

## 任务 1：准备 Python 环境

### 1.1 检查 Python 版本

先在当前目录打开终端，执行：

```powershell
python --version
```

你最好看到的是 `Python 3.12` 或更高版本。

原因很简单：

- Django 6.0 对应 Python 3.12+

如果你的版本更低，也不是完全不能学，但就不要严格跟 6.0 文档走，要切到对应版本文档。

### 1.2 创建虚拟环境

在当前目录执行：

```powershell
python -m venv .venv
```

这个命令会创建一个 `.venv` 文件夹，用来隔离当前项目依赖。

这样做的好处是：

- 不污染全局 Python 环境
- 不会和别的项目的包版本打架
- 更接近真实项目开发习惯

### 1.3 激活虚拟环境

PowerShell 下执行：

```powershell
.venv\Scripts\Activate.ps1
```

如果激活成功，终端前面一般会出现类似 `(.venv)` 的提示。

### 1.4 升级 pip 并安装 Django

```powershell
python -m pip install --upgrade pip
pip install "Django>=6.0,<6.1"
```

### 1.5 检查 Django 是否安装成功

```powershell
python -m django --version
```

如果能输出 Django 版本号，就说明环境没问题。

---

## 任务 2：创建 Django 项目

### 2.1 在当前目录创建项目

在当前目录执行：

```powershell
django-admin startproject studynotes .
```

这条命令的意思是：

- 创建一个项目名为 `studynotes`
- 把项目生成到当前目录，而不是额外新建一层目录

执行完后，你通常会看到这几个关键内容：

- `manage.py`
- `studynotes/`

### 2.2 先认识一下生成出来的文件

你现在先不用背全部，只要知道这几个最重要的文件：

#### `manage.py`

它是 Django 项目的命令入口。

以后你会经常用它做这些事：

- 启动开发服务器
- 执行迁移
- 创建 app
- 创建超级用户
- 跑测试

#### `studynotes/settings.py`

这是项目总配置文件。

你后面会在这里配置：

- 已安装 app
- 数据库
- 中间件
- 模板
- 静态文件

#### `studynotes/urls.py`

这是项目总路由文件。

你可以把它理解为“总入口路由表”。

#### `studynotes/asgi.py` 和 `studynotes/wsgi.py`

今天不用深挖，只要先知道：

- `wsgi.py` 更偏传统同步部署
- `asgi.py` 更偏现代异步能力

---

## 任务 3：先把项目跑起来

### 3.1 启动开发服务器

执行：

```powershell
python manage.py runserver
```

如果启动成功，你会看到类似：

```text
Starting development server at http://127.0.0.1:8000/
```

这时打开浏览器访问：

```text
http://127.0.0.1:8000/
```

如果你看到了 Django 的欢迎页面，说明项目已经跑起来了。

### 3.2 这一步为什么重要

很多人会急着写业务代码，但 Day 1 最重要的不是功能，而是确认：

- 环境没问题
- Django 能启动
- 你知道服务是怎么跑起来的

只要这一步成功，后面 6 天就有基础了。

---

## 任务 4：创建第一个 app

### 4.1 创建 `notes` app

执行：

```powershell
python manage.py startapp notes
```

执行完后，你会看到一个新的目录：

```text
notes/
```

里面会有这些文件：

- `admin.py`
- `apps.py`
- `models.py`
- `tests.py`
- `views.py`

### 4.2 为什么要建 app

因为你的项目不会永远只有一个页面。

以后你的 `StudyNotes` 项目里，至少会逐步出现这些功能：

- 笔记
- 标签
- 评论
- 用户权限

把业务放进 app，是 Django 的标准组织方式。

---

## 任务 5：把 app 注册进项目

### 5.1 修改 `studynotes/settings.py`

找到 `INSTALLED_APPS`，把 `notes` 加进去。

示例：

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "notes",
]
```

### 5.2 这一步为什么不能忘

如果你创建了 app，却没有加入 `INSTALLED_APPS`，Django 就不会真正把它当成项目的一部分。

后面你会遇到很多怪问题，比如：

- 模型不生效
- 模板不识别
- Admin 里看不到内容

所以这一步很关键。

---

## 任务 6：编写第一个视图

### 6.1 修改 `notes/views.py`

先写 3 个最简单的视图：

```python
from django.http import HttpResponse, JsonResponse


def home(request):
    return HttpResponse("Welcome to StudyNotes")


def health(request):
    return HttpResponse("OK")


def ping(request):
    return JsonResponse({"message": "pong"})
```

### 6.2 这 3 个视图分别代表什么

- `home`：最简单的普通页面响应
- `health`：一个健康检查页，很多项目里都会有
- `ping`：一个最简单的 JSON 接口

这 3 个例子很适合 Day 1，因为它们能让你同时看到：

- 文本响应
- JSON 响应
- Django 视图函数的基本结构

### 6.3 先别想太复杂

今天你暂时不用管：

- 数据库
- 模板
- 表单
- 登录
- 权限

你只要先理解一件事：

> 浏览器发请求，Django 根据 URL 找到视图，视图返回响应。

这就是今天最核心的主线。

---

## 任务 7：给 app 创建自己的路由文件

### 7.1 在 `notes` 目录下新建 `urls.py`

文件内容如下：

```python
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health, name="health"),
    path("api/ping/", views.ping, name="ping"),
]
```

### 7.2 这样设计有什么好处

这样做的好处是：

- 项目总路由只负责“分发”
- app 自己管理自己的页面

随着项目变大，这种结构会非常清晰。

你可以把它理解成：

- `studynotes/urls.py` 是总入口
- `notes/urls.py` 是 notes 模块自己的路由表

---

## 任务 8：把 app 路由接到项目总路由里

### 8.1 修改 `studynotes/urls.py`

把它改成这样：

```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("notes.urls")),
]
```

### 8.2 你现在应该理解的事情

当用户访问一个 URL 时，流程大概是：

1. 请求先进入项目总路由
2. 总路由把请求交给 `notes.urls`
3. `notes.urls` 找到对应视图函数
4. 视图函数返回响应

这是 Django 路由和视图协作的最小闭环。

---

## 任务 9：再次运行并验证页面

### 9.1 启动服务

```powershell
python manage.py runserver
```

### 9.2 访问以下地址

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health/`
- `http://127.0.0.1:8000/api/ping/`

### 9.3 你应该看到什么

- `/`：显示 `Welcome to StudyNotes`
- `/health/`：显示 `OK`
- `/api/ping/`：显示一段 JSON，比如 `{"message": "pong"}`

如果这 3 个页面都能正常访问，说明 Day 1 的主线已经跑通。

---

## 今天必须搞明白的文件

请你至少把下面 5 个文件的作用说清楚：

### `manage.py`

用来执行 Django 项目命令。

### `studynotes/settings.py`

项目配置中心。

### `studynotes/urls.py`

项目总路由入口。

### `notes/urls.py`

业务模块自己的路由表。

### `notes/views.py`

视图函数所在位置，也就是处理请求并返回响应的地方。

---

## 常见报错和排查方法

### 1. `django-admin` 找不到

原因通常是：

- Django 没装成功
- 虚拟环境没激活

解决方法：

- 重新激活 `.venv`
- 执行 `python -m django --version`

### 2. PowerShell 不允许激活脚本

有时会遇到执行策略限制。

可以临时执行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

然后再执行：

```powershell
.venv\Scripts\Activate.ps1
```

### 3. 页面返回 404

通常说明：

- 路由没配对
- `include("notes.urls")` 没写
- `notes/urls.py` 里的路径写错了

排查顺序建议：

1. 先看 `studynotes/urls.py`
2. 再看 `notes/urls.py`
3. 再看 `notes/views.py`

### 4. 提示 `ModuleNotFoundError`

通常说明：

- app 名拼错
- 导入路径写错

先检查：

- `INSTALLED_APPS` 里是不是 `notes`
- `include("notes.urls")` 是不是拼写正确

---

## 今天的交付标准

你今天结束前，至少要完成这些事：

- [ ] 创建虚拟环境并安装 Django
- [ ] 创建项目 `studynotes`
- [ ] 创建 app `notes`
- [ ] 把 `notes` 加入 `INSTALLED_APPS`
- [ ] 写出 3 个视图：`home`、`health`、`ping`
- [ ] 创建 `notes/urls.py`
- [ ] 在项目总路由中 `include("notes.urls")`
- [ ] 成功访问 `/`
- [ ] 成功访问 `/health/`
- [ ] 成功访问 `/api/ping/`

如果这些都完成，Day 1 就算达标。

---

## 今日复盘问题

今天结束后，你可以用下面这些问题检查自己是不是真的懂了：

1. Django 中 `project` 和 `app` 的区别是什么？
2. `manage.py` 是做什么用的？
3. 为什么创建 app 之后还要把它加入 `INSTALLED_APPS`？
4. URL 是怎么找到视图函数的？
5. `HttpResponse` 和 `JsonResponse` 有什么区别？
6. 如果访问页面报 404，你会先检查哪个文件？

只要你能比较顺畅地回答这 6 个问题，说明 Day 1 的基础已经打稳了。

---

## 今天结束后你应该拥有的目录结构

你至少应该看到类似这样的结构：

```text
Django_learning_note/
├─ .venv/
├─ manage.py
├─ studynotes/
│  ├─ __init__.py
│  ├─ asgi.py
│  ├─ settings.py
│  ├─ urls.py
│  └─ wsgi.py
├─ notes/
│  ├─ __init__.py
│  ├─ admin.py
│  ├─ apps.py
│  ├─ models.py
│  ├─ tests.py
│  ├─ urls.py
│  └─ views.py
└─ tasks/
   └─ day1.markdown
```

---

## 一句总结今天学了什么

今天你真正学会的不是“写了 3 个页面”，而是：

> 你已经成功搭起了一个 Django 项目，并理解了“请求 -> 路由 -> 视图 -> 响应”这条最核心的主线。

这一步一旦打通，后面的模型、表单、登录、Admin、测试和部署，都会顺着这条主线往上长出来。
