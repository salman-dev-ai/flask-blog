<p align="center">
  <a href="README.md">🌐 Language: English (الإنجليزية)</a>
</p>

<h1 align="center">
  📘 FaceBlog — تطبيق التدوين الاجتماعي المستوحى من فيسبوك
</h1>

<p align="center">
  <strong>منصة تدوين اجتماعي بجودة إنتاجية مبنية بااستخدام Python 3 و Flask و SQLite.</strong>
  <br />
  صُمِّم كمورد تعليمي شامل لإتقان تطوير تطبيقات الويب الكاملة
  بإطار العمل Flask، مع واجهة مستخدم مخصّصة مستوحاة من تصميم فيسبوك.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask 3.0" />
  <img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Pytest-100%25_Code_Coverage-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest 100% Coverage" />
  <img src="https://img.shields.io/badge/Waitress-Production_WSGI-4B0082?style=for-the-badge&logo=python&logoColor=white" alt="Waitress WSGI" />
  <img src="https://img.shields.io/badge/Flit-Modern_Packaging-FFD43B?style=for-the-badge&logo=python&logoColor=black" alt="Flit Packaging" />
</p>

<hr />

## 📑 جدول المحتويات

- [🚀 الميزات الأساسية](#-الميزات-الأساسية)
- [🧠 خريطة التعلم الشاملة](#-خريطة-التعلم-الشاملة)
- [⚙️ تحديات الهندسة وتصحيح الأخطاء الحقيقية](#️-تحديات-الهندسة-وتصحيح-الأخطاء-الحقيقية)
- [📸 معرض الصور التوضيحية](#-معرض-الصور-التوضيحية)
- [⚡ دليل التثبيت والتشغيل السريع](#-دليل-التثبيت-والتشغيل-السريع)
- [📂 هيكل المشروع](#-هيكل-المشروع)
- [👨‍💻 المؤلف والترخيص](#-المؤلف-والترخيص)

<hr />

## 🚀 الميزات الأساسية

يقدّم FaceBlog **ستة أركان أساسية** من هندسة تطبيقات الويب الحديثة:

### 1. 🏭 نمط مصنع التطبيقات وهيكلة البلوبرينت (Blueprint Architecture)

يتم بناء التطبيق باستخدام نمط **مصنع التطبيقات** (`create_app()` في `flaskr/__init__.py`)، والذي يقوم بتكوين وإرجاع نسخة Flask كاملة التهيئة ديناميكيًا. يتيح هذا النمط:

- **تكوين مرن حسب البيئة** — التبديل بين سياقات التطوير والاختبار والإنتاج عن طريق تمرير خرائط تهيئة مختلفة.
- **عزل مجلد المثيل** — الإعدادات الحساسة (مثل `SECRET_KEY`) تكون مخزنة في `instance/config.py`، مستبعدة من نظام التحكم بالإصدارات.
- **هيكل بلوبرينت معياري** — بلوبرينتان منفصلان ينظّمان قاعدة الكود:
  - بلوبرينت `auth` (بالبادئة `/auth`) — يدير التسجيل، تسجيل الدخول، تسجيل الخروج، وإدارة الجلسات.
  - بلوبرينت `blog` (بدون بادئة) — يعمل كصفحة الهبوط الرئيسية مع إنشاء وتحرير وحذف المشاركات.

```python
# flaskr/__init__.py — نواة مصنع التطبيق
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)  # تحميل أسرار الإنتاج
    else:
        app.config.from_mapping(test_config)               # تحميل تجاوزات الاختبار

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    app.register_blueprint(auth.bp)   # تسجيل مسارات المصادقة
    app.register_blueprint(blog.bp)   # تسجيل مسارات المدونة
    app.add_url_rule("/", endpoint="index")  # ربط مسار الجذر بنقطة النهاية 'index'

    return app
```

### 2. 🔐 نظام المصادقة الآمن

تم تنفيذ المصادقة باستخدام **ممارسات أمان قياسية في الصناعة**:

- **تجزئة كلمات المرور** عبر Werkzeug بوظائف `generate_password_hash()` و `check_password_hash()` — باستخدام خوارزمية (PBKDF2-SHA256) الافتراضية.
- **مصادقة قائمة على الجلسة** — يتم تخزين معرف المستخدم في ملف تعريف الارتباط (Cookie) المشفر الخاص بفلاسك بعد تسجيل الدخول الناجح.
- **الوسيط `@login_required`** — برنامج وسيط مخصص يعترض الطلبات غير الموثّقة ويعيد توجيهها إلى صفحة تسجيل الدخول.
- **`@bp.before_app_request`** — يقوم تلقائيًا بتحميل بيانات المستخدم الموثّق في كائن `g` العام قبل *كل* طلب، مما يجعل `g.user` متاحًا عالميًا عبر جميع البلوبرينتات.

```python
# flaskr/auth.py — إنشاء جلسة الدخول
@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()

        user = db.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()

        if user is None:
            error = "اسم المستخدم غير صحيح."
        elif not check_password_hash(user["password"], password):
            error = "كلمة المرور غير صحيحة."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)
    return render_template("auth/login.html")
```

### 3. ✍️ وظائف المدونة الكاملة (CRUD)

إمكانيات كاملة **لإنشاء وقراءة وتحديث وحذف** منشورات المدونة:

- **صفحة الفهرس** — تعرض جميع المنشورات مع أسماء المؤلفين، مرتبة حسب تاريخ الإنشاء (الأحدث أولاً)، باستخدام استعلام JOIN.
- **الإنشاء** — محمي بالوسيط `@login_required`، يتحقق من صحة العنوان، ويستخدم استعلامات INSERT مع باراميترات آمنة.
- **التحديث** — يستخدم المساعد `get_post()` لجلب المنشور والتحقق من الملكية وعرض نموذج التحرير.
- **الحذف** — مسار POST فقط يتحقق من الملكية ثم يزيل المنشور نهائيًا.

```python
# flaskr/blog.py — جلب جميع المنشورات مع معلومات المؤلف
@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username "
        "FROM post p JOIN user u ON p.author_id = u.id "
        "ORDER BY created DESC"
    ).fetchall()
    return render_template("blog/index.html", posts=posts)
```

### 4. 🛡️ حماية ملكية المؤلف

ميزة أمنية حرجة تضمن **التحكم الصارم بصلاحيات الوصول للمؤلف**:

- تُستخدم وظيفة `get_post(id, check_author=True)` في عمليتي التحديث والحذف.
- تقبل باراميتر `check_author` (القيمة الافتراضية `True`). عند التفعيل، تتحقق مما إذا كان `post["author_id"] == g.user["id"]`.
- إذا حاول مستخدم تعديل أو حذف منشور لمؤلف آخر: يتم رفع **HTTP 403 Forbidden**.
- إذا كان معرف المنشور غير موجود: يتم رفع **HTTP 404 Not Found**.

```python
# flaskr/blog.py — التحقق من الملكية
def get_post(id, check_author=True):
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"المعرف {id} غير موجود.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)  # ممنوع — ليس منشورك

    return post
```

### 5. 🎨 واجهة مستخدم مستوحاة من فيسبوك

الواجهة الأمامية مصممة بالكامل باستخدام **جماليات فيسبوك الحديثة المخصصة**:

- **خصائص CSS المخصصة (متغيرات)** — الألوان مثل `--fb-blue: #1877F2`، والخطوط، والتباعد محددة عالميًا لتناسق التصميم.
- **شريط تنقل لاصق (Sticky Nav)** — يثبت شريط التنقل العلوي أثناء التمرير باستخدام `position: sticky; top: 0; z-index: 100`.
- **تصميم بطاقات التغذية** — تُعرض المنشورات كبطاقات بيضاء فردية مع ظلال خفيفة وزوايا دائرية وتباعد مناسب — تحاكي تصميم صفحة أخبار فيسبوك.
- **حالات التفاعل** — تأثيرات التمرير على الأزرار، حلقات التركيز على حقول النماذج، وانتقالات سلسة لجميع العناصر التفاعلية.
- **تصميم متجاوب** — حاوية بعرض أقصى (960px للشريط، 680px للتغذية) تضمن عرض التطبيق بشكل جميل على سطح المكتب مع البقاء متوافقًا مع الأجهزة المحمولة.

### 6. ✅ تغطية اختبارية آلية بنسبة 100%

حزمة الاختبار تحقق **تغطية كود بنسبة 100%** عبر التطبيق بأكمله:

- **`test_factory.py`** — يتحقق من أن مصنع التطبيق ينشئ النسخ بشكل صحيح (تبديل وضع الاختبار، صفحة الترحيب).
- **`test_db.py`** — يتحقق من تهيئة قاعدة البيانات، إعادة استخدام الاتصال، وتنفيذ الاستعلامات.
- **`test_auth.py`** — يختبر التسجيل (ناجح + مكرر + تحقق)، تسجيل الدخول (بيانات صحيحة + غير صحيحة)، وتسجيل الخروج (مسح الجلسة).
- **`test_blog.py`** — تغطية شاملة لعرض الفهرس، حماية تسجيل الدخول، تطبيق ملكية المؤلف، معالجة المنشورات غير الموجودة، عمليات الإنشاء/التحديث/الحذف، والتحقق من صحة الإدخال.

```python
# tests/conftest.py — تجهيزات الاختبار مع قاعدة بيانات مؤقتة
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)
    yield app
    os.close(db_fd)
    os.unlink(db_path)
```

<hr />

## 🧠 خريطة التعلم الشاملة

هذا المشروع يُعد **موردًا تعليميًا شاملًا** لمطوري الويب المبتدئين والمتوسطين بلغة Python. إليك بالضبط ما ستتعلمه:

### 📐 هندسة MVC في سياق Flask

| المفهوم | التطبيق في Flask |
|---------|-----------------|
| **النموذج (Model)** | طبقة قاعدة بيانات SQLite (`db.py`) مع `get_db()` لإدارة الاتصالات |
| **العرض (View)** | قوالب Jinja2 (`templates/`) لتقديم HTML ببيانات ديناميكية |
| **التحكم (Controller)** | دوال المسارات في `auth.py` و `blog.py` لمعالجة طلبات HTTP |
| **التوجيه (Router)** | تسجيل البلوبرينت و `app.add_url_rule()` لربط المسارات بنقاط النهاية |
| **الوسيط (Middleware)** | مصمم `@login_required` وخطاف `before_app_request` |
| **المزوّد (Provider)** | مصنع التطبيق لتوفير التهيئة، قاعدة البيانات، وسياق القوالب |

### 🗄️ هندسة قواعد البيانات مع SQLite

- **تصميم المخطط** — جدولان (`user` و `post`) بعلاقة مفتاح خارجي (`author_id` يشير إلى `user.id`).
- **استعلامات آمنة بالباراميترات** — جميع استعلامات SQL تستخدم العناصر النائبة `?` مع ربط tuple لمنع هجمات حقن SQL.
- **إدارة دورة الحياة** — يتم إنشاء الاتصالات لكل طلب، تخزينها في كائن `g` الخاص بـ Flask، وإغلاقها تلقائيًا عبر `app.teardown_appcontext(close_db)`.
- **تهيئة المخطط** — أمر CLI `init-db` يقرأ `schema.sql`، يحذف الجداول الموجودة، يعيد إنشائها، ويملأ قاعدة البيانات — كل ذلك عبر أمر Click واحد.
- **معالجة الطابع الزمني** — محول مخصص مسجل: `sql.register_converter('timestamp', lambda v: datetime.fromisoformat(v.decode()))`.

```sql
-- flaskr/schema.sql — مخطط قاعدة البيانات
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
```

### 🎨 توريث قوالب Jinja2

- **`base.html`** — القالب الهيكلي الذي يعرّف بنية HTML، شريط التنقل، نظام الرسائل الوامضة (flash messages)، و**عناصر نائبة للكتل** (`{% block title %}`, `{% block header %}`, `{% block content %}`).
- **القوالب الفرعية** — كل صفحة (تسجيل الدخول، التسجيل، الفهرس، الإنشاء، التحديث) تمدّد `base.html` وتتجاوز كتلًا محددة.
- **العرض الشرطي** — شريط التنقل يعرض ديناميكيًا "تسجيل الدخول" / "التسجيل" للمستخدمين المجهولين، و"تسجيل الخروج" مع اسم المستخدم للمستخدمين الموثّقين: `{% if g.user %} ... {% else %} ... {% endif %}`.
- **سياق الحلقة المحدود (Scoped Loop)** — تحافظ حلقة `for` في Jinja2 على نطاقها الخاص، مما يمنع تسرب المتغيرات بين التكرارات — وهو مصدر شائع للأخطاء للمبتدئين.

```html
<!-- flaskr/templates/base.html — قالب التخطيط الأصلي -->
<!doctype html>
<html lang="ar" dir="rtl">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{% block title %}{% endblock %}- FaceBlog</title>
    <link rel="stylesheet" href="{{url_for('static',filename='style.css')}}" />
    <link rel="icon" type="image/x-icon" sizes="any" href="{{ url_for('static', filename='favicon.ico') }}">
  </head>
  <body>
    <nav>
      <h1>FaceBlog</h1>
      <ul>
        {% if g.user %}
        <li><span>{{ g.user['username'] }}</span></li>
        <li><a href="{{ url_for('auth.logout') }}">تسجيل الخروج</a></li>
        {% else %}
        <li><a href="{{ url_for('auth.register') }}">التسجيل</a></li>
        <li><a href="{{ url_for('auth.login') }}">تسجيل الدخول</a></li>
        {% endif %}
      </ul>
    </nav>
    <section class="content">
      <header>{% block header %}{% endblock %}</header>
      {% for message in get_flashed_messages() %}
      <div class="flash">{{ message }}</div>
      {% endfor %}
      {% block content %}{% endblock %}
    </section>
  </body>
</html>
```

### 📦 التغليف الحديث لبايثون باستخدام Flit

- **`pyproject.toml`** — معيار التغليف الحديث لبايثون، الذي يحل محل نهج `setup.py` التقليدي.
- **Flit كخلفية بناء** — أداة تغليف خفيفة وسريعة تعمل بسلاسة مع تطبيقات Flask.
- **ربط اسم الوحدة** — قسم `[tool.flit.module]` يربط بشكل صريح المجلد الداخلي `flaskr` باسم الحزمة العامة `faceblog` — وهو رابط حاسم يغفل عنه المبتدئون غالبًا.

```toml
# pyproject.toml — تهيئة التغليف الحديثة لبايثون
[project]
name = "faceblog"                   # اسم الحزمة العامة على PyPI
version = "1.0.0"
description = "تطبيق تدوين اجتماعي مستوحى من فيسبوك مبني بـ Python و Flask."
dependencies = [
    "flask",                         # إطار الويب الأساسي
    "waitress",                      # خادم WSGI للإنتاج
]

[build-system]
requires = ["flit_core<4"]
build-backend = "flit_core.buildapi"

[tool.flit.module]
name = "flaskr"  # ⚡ يربط المجلد الداخلي `flaskr` بحزمة `faceblog`

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.coverage.run]
branch = true
source = ["flaskr"]
```

<hr />

## ⚙️ تحديات الهندسة وتصحيح الأخطاء الحقيقية

يوثّق هذا القسم **أربعة أخطاء حقيقية** تمت مواجهتها أثناء التطوير، كل منها يمثل مطبًا كلاسيكيًا في تطوير Python/Flask. فهمها سيوفر لك ساعات من التصحيح.

### 🔥 الخطأ رقم 1: المسافات المفقودة في سلاسل SQL متعددة الأسطر

**العَرَض:** يرفع SQLite خطأ `OperationalError: near "WHERE" syntax error` عند تنفيذ استعلام UPDATE.

**السبب الجذري:** دمج السلاسل النصية الضمني في Python (`"string1" "string2"`) **لا** يدرج مسافة بين الأجزاء المدمجة. الكود الأصلي:

```python
# ❌ خطأ: مسافة مفقودة قبل 'WHERE'
db.execute(
    "UPDATE post SET title = ?, body = ?" "WHERE id = ?", 
    (title, body, id)
)
```

هذا يُجمّع إلى: `UPDATE post SET title = ?, body = ?WHERE id = ?` — مما ينتج SQL غير صالح.

**✅ الإصلاح:** أضف مسافة بادئة قبل `WHERE`:

```python
# ✅ تم الإصلاح: مسافة قبل 'WHERE'
db.execute(
    "UPDATE post SET title = ?, body = ?" " WHERE id = ?",  # لاحظ المسافة!
    (title, body, id)
)
```

**📚 الدرس:** يدمج Python السلاسل النصية المتجاورة بدون أي فاصل. تأكد دائمًا من تركيب سلاسل SQL عند استخدام تنسيق متعدد الأسطر.

---

### 🔥 الخطأ رقم 2: تعارض نقطة النهاية (KeyError: 'index')

**العَرَض:** بعد تسجيل كل من بلوبرينتي `auth` و `blog`، يؤدي استدعاء `url_for("index")` إلى رفع `KeyError: 'index'`.

**السبب الجذري:** دوال `login()` و `logout()` في بلوبرينت `auth` تستدعي داخليًا `url_for("index")`، متوقعة أن يشير إلى مسار الجذر `/`. لكن مسار الفهرس في بلوبرينت `blog` (`@bp.route("/")`) ينشئ نقطة نهاية باسم `blog.index`، وليس `index`. بدون اسم مستعار صريح، لا توجد نقطة نهاية مسجلة تحت الاسم البسيط `index`.

```python
# ❌ خطأ: url_for("index") يفشل لأنه لا يوجد مسار باسم 'index'
app.register_blueprint(auth.bp)
app.register_blueprint(blog.bp)  # ينشئ نقطة نهاية 'blog.index'، وليس 'index'
```

**✅ الإصلاح:** سجل مسار الجذر مع باراميتر `endpoint` صريح:

```python
# ✅ تم الإصلاح: ربط مسار الجذر باسم نقطة النهاية 'index'
app.add_url_rule("/", endpoint="index")
```

**📚 الدرس:** ترتيب `register_blueprint()` و `add_url_rule()` مهم. عند تسجيل بلوبرينت، تكون مساراته ضمن نطاق اسمي (`blog.index`). لإنشاء اسم مستعار غير مُسمّى، استخدم `app.add_url_rule()` *بعد* تسجيل جميع البلوبرينتات.

---

### 🔥 الخطأ رقم 3: خطأ تغليف Flit — لم يتم العثور على ملف/مجلد للوحدة

**العَرَض:** يفشل تشغيل `flit install` أو `pip install -e .` مع الخطأ `ValueError: No file/folder found for module 'faceblog'`.

**السبب الجذري:** افتراضيًا، يبحث Flit عن دليل أو ملف على المستوى الأعلى يطابق `[project].name` (`faceblog`). لكن كود المصدر الفعلي موجود داخل دليل `flaskr/`، وليس `faceblog/`. لا يستطيع Flit حل هذا الربط تلقائيًا.

```toml
# ❌ خطأ: Flit يبحث عن مجلد 'faceblog/' غير موجود
[project]
name = "faceblog"    # Flit يبحث عن ./faceblog/ — غير موجود!
```

**✅ الإصلاح:** أخبر Flit صراحةً أي دليل وحدة سيتم تغليفه:

```toml
# ✅ تم الإصلاح: تعريف اسم الوحدة بشكل صريح
[tool.flit.module]
name = "flaskr"  # يخبر Flit: "احزم مجلد 'flaskr/'، وانشر كـ 'faceblog'"
```

**📚 الدرس:** يعمل قسم `[tool.flit.module]` كـ**رابط هيكلي** بين هيكل المجلدات الداخلي واسم الحزمة العامة. قم دائمًا بتكوين هذا عندما يختلف اسم دليل المصدر عن اسم الحزمة.

---

### 🔥 الخطأ رقم 4: التخزين المؤقت العدواني لأيقونة الموقع (Favicon) في المتصفح

**العَرَض:** بعد استبدال ملف الأيقونة، يعرض المتصفح بعناد الأيقونة القديمة على الرغم من عدة عمليات تحديث. تظهر الأيقونة الجديدة فقط بعد مسح ذاكرة التخزين المؤقت بالكامل.

**السبب الجذري:** تخزّن المتصفحات أيقونات المواقع (favicon) بعدوانية شديدة، متجاهلة غالبًا رؤوس التحكم في التخزين المؤقت القياسية. بالإضافة إلى ذلك، تتطلب أيقونات SVG سمات `<link>` محددة لعرضها بشكل صحيح عبر المتصفحات المختلفة.

```html
<!-- ❌ خطأ: المتصفح يخزّن الأيقونة القديمة بعناد -->
<link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">
```

**✅ الإصلاح:** أضف السمة `sizes="any"`، التي تخبر المتصفحات بمعاملة الأيقونة كخيار احتياطي لجميع الأحجام، مما يتجاوز أقفال التخزين المؤقت:

```html
<!-- ✅ تم الإصلاح: sizes="any" تجبر المتصفحات على إعادة قراءة الأيقونة -->
<link rel="icon" type="image/x-icon" sizes="any" href="{{ url_for('static', filename='favicon.ico') }}">
```

**استراتيجيات التحديث القسري:**
- **Chrome/Edge:** `Ctrl + Shift + R` (ويندوز) أو `Cmd + Shift + R` (ماك)
- **Firefox:** `Ctrl + F5` (ويندوز) أو `Cmd + Shift + R` (ماك)
- **أدوات المطور:** انقر بزر الماوس الأيمن على زر التحديث → "Empty Cache and Hard Reload"

**📚 الدرس:** التخزين المؤقت للأيقونات هو أحد أكثر آليات التخزين المؤقت عدوانية في المتصفحات الحديثة. السمة `sizes="any"` تعمل كإشارة لاختراق التخزين المؤقت. لأيقونات SVG تحديدًا، تأكد دائمًا من تضمين `type="image/svg+xml"` و `sizes="any"` لضمان التوافق عبر المتصفحات.

<hr />

## 📸 معرض الصور التوضيحية

> **ملاحظة:** يتم التقاط لقطات الشاشة تلقائيًا وتخزينها في دليل `flaskr/static/img/`.
> استبدل أسماء الملفات المؤقتة أدناه بلقطات الشاشة الفعلية الخاصة بك.

### 📰 صفحة التغذية الرئيسية
تصميم التغذية القائم على البطاقات المستوحى من فيسبوك يعرض جميع منشورات المدونة مع معلومات المؤلف والتواريخ.

<p align="center">
  <img src="flaskr/static/img/img (1).png" alt="التغذية الرئيسية لـ FaceBlog — تخطيط البطاقات" width="80%" />
</p>

### 🔑 صفحة تسجيل الدخول / التسجيل
واجهة المصادقة بتصميم نموذج نظيف ومركزي متسق مع ثيم فيسبوك.

<p align="center">
  <img src="flaskr/static/img/img (2).png" alt="صفحة تسجيل الدخول لـ FaceBlog — نموذج مصادقة بثيم فيسبوك" width="80%" />
</p>

### ✏️ واجهات إنشاء وتحرير المشاركات
نماذج إنشاء المحتوى وتحريره، مع حقول إدخال وأزرار إجراءات بتصميم فيسبوك.

<p align="center">
  <img src="flaskr/static/img/img (3).png" alt="إنشاء/تحرير المشاركات في FaceBlog — نماذج إدارة المحتوى" width="80%" />
</p>

### 🧪 تقرير تغطية Pytest بنسبة 100%
مجموعة الاختبارات الآلية تحقق تغطية كاملة للكود عبر التطبيق بأكمله.

<p align="center">
  <img src="flaskr/static/img/img (4).png" alt="تقرير تغطية Pytest — التحقق من تغطية كود بنسبة 100%" width="80%" />
</p>

<hr />

## ⚡ دليل التثبيت والتشغيل السريع

اتبع هذه الخطوات لإعداد وتشغيل FaceBlog على جهازك المحلي.

### المتطلبات الأساسية

- **Python 3.9+** مثبت على نظامك
- **Git** (اختياري، لاستنساخ المستودع)
- **pip** (مدير حزم Python)

### الخطوة 1: استنساخ المستودع

```bash
# استنساخ من GitHub (أو نسخ مجلد المشروع يدويًا)
git clone https://github.com/salman-dev-ai/flask-blog.git
cd flask-blog
```

### الخطوة 2: إنشاء بيئة افتراضية

```bash
# إنشاء بيئة Python معزولة لهذا المشروع
# ويندوز:
python -m venv venv

# macOS / Linux:
python3 -m venv venv

# تفعيل البيئة الافتراضية
# ويندوز:
venv\Scripts\activate

# macOS / Linux:
source venv/bin/activate
```

### الخطوة 3: تثبيت الحزمة (وضع التحرير)

```bash
# تثبيت المشروع وتبعياته في وضع التحرير/التطوير.
# العلامة '-e .' تخبر pip باستخدام ملف pyproject.toml في الدليل الحالي.
# وضع التحرير يعني أن تغييرات الكود تسري فورًا دون إعادة التثبيت.
pip install -e .
```

### الخطوة 4: إنشاء مفتاح سري

```bash
# إنشاء دليل المثيل وملف التهيئة لأسرار الإنتاج
# المفتاح السري (SECRET_KEY) يستخدمه Flask لتوقيع ملفات تعريف الارتباط للجلسة تشفيريًا.

# لويندوز (Command Prompt):
mkdir instance
echo SECRET_KEY='your-production-secret-key-here' > instance\config.py

# لـ macOS / Linux:
mkdir -p instance
echo "SECRET_KEY='your-production-secret-key-here'" > instance/config.py

# 🔐 هام: أنشئ مفتاحًا قويًا باستخدام Python:
# python -c "import secrets; print(secrets.token_hex(32))"
```

### الخطوة 5: تهيئة قاعدة البيانات

```bash
# إنشاء قاعدة بيانات SQLite وتطبيق المخطط المعرّف في flaskr/schema.sql.
# هذا الأمر يسجّل أمر CLI 'init-db' عبر Click، كما هو معرّف في db.py.
flask --app flaskr init-db
```

### الخطوة 6: تشغيل مجموعة الاختبارات الآلية

```bash
# تنفيذ جميع الاختبارات مع تحليل تغطية الكود
# العلامة '--branch' تقيس تغطية الفروع (مسارات if/else).
# إعداد 'source = ["flaskr"]' في pyproject.toml يحدد التغطية لكود التطبيق فقط.

# تشغيل pytest مع التغطية:
coverage run -m pytest

# عرض تقرير التغطية في الطرفية:
coverage report

# إنشاء تقرير تغطية HTML (يفتح في المتصفح):
coverage html
# ثم افتح: htmlcov/index.html

# للتشغيل السريع للاختبارات بدون تغطية:
pytest -v
```

### الخطوة 7: تشغيل خادم WSGI للإنتاج

```bash
# تشغيل التطبيق باستخدام Waitress، خادم WSGI بجودة إنتاجية.
# العلامة '--call' تخبر Waitress باستدعاء flaskr:create_app() كدالة مصنع.
# هذا أقوى بكثير من خادم التطوير المدمج في Flask.

waitress-serve --call "flaskr:create_app"
```

### الخطوة 8: الوصول إلى التطبيق

```
افتح متصفح الويب وانتقل إلى:

    👉 http://localhost:8080

ستظهر لك صفحة FaceBlog الرئيسية بواجهة مستخدم بثيم فيسبوك!
```

### 🐍 بداية سريعة (سطر واحد للتطوير)

```bash
# لأغراض التطوير فقط (ليس للإنتاج):
flask --app flaskr --debug run
```

<hr />

## 📂 هيكل المشروع

```
faceblog/                              # جذر المشروع (منشور باسم 'faceblog')
│
├── pyproject.toml                     # تهيئة التغليف الحديثة لبايثون (Flit)
├── MANIFEST.in                        # قواعد الإدراج للتوزيع المصدر
├── hello.py                           # نص اختبار سريع
├── info                               # ملاحظات / بيانات وصفية للمشروع
├── .gitignore                         # قواعد استثناء Git
├── .coverage                          # ملف بيانات التغطية (منشأ بواسطة pytest-cov)
│
├── flaskr/                            # حزمة التطبيق الرئيسية (الاسم الداخلي)
│   ├── __init__.py                    # مصنع التطبيق: create_app()
│   ├── auth.py                        # بلوبرينت المصادقة (تسجيل/دخول/خروج)
│   ├── blog.py                        # بلوبرينت المدونة (فهرس/إنشاء/تحديث/حذف)
│   ├── db.py                          # طبقة قاعدة البيانات (get_db, init_db, close_db, CLI)
│   ├── schema.sql                     # مخطط SQL (جداول المستخدم + المنشور)
│   │
│   ├── templates/                     # قوالب Jinja2 HTML
│   │   ├── base.html                  # التخطيط الأساسي مع التنقل، الكتل، الرسائل الوامضة
│   │   ├── auth/
│   │   │   ├── register.html          # نموذج تسجيل المستخدم
│   │   │   └── login.html             # نموذج تسجيل الدخول
│   │   └── blog/
│   │       ├── index.html             # التغذية الرئيسية — تعرض جميع المنشورات
│   │       ├── create.html            # نموذج إنشاء منشور جديد
│   │       └── update.html            # نموذج تعديل المنشور
│   │
│   ├── static/                        # الأصول الثابتة (CSS، صور، أيقونة)
│   │   ├── style.css                  # ثيم مستوحى من فيسبوك (خصائص FB مخصصة)
│   │   ├── favicon.ico                # أيقونة تبويب المتصفح
│   │   └── img/                       # دليل لقطات شاشة التطبيق
│   │       ├── img (1).png            # لقطة شاشة للتغذية الرئيسية
│   │       ├── img (2).png            # لقطة شاشة للمصادقة
│   │       ├── img (3).png            # لقطة شاشة لإدارة المحتوى
│   │       └── img (4).png            # لقطة شاشة لتغطية الاختبارات
│
├── instance/                          # مجلد المثيل (مستبعد من نظام التحكم بالإصدارات)
│   └── config.py                      # المفتاح السري للإنتاج (يتم تحميله تلقائيًا بواسطة المصنع)
│
└── tests/                             # مجموعة الاختبارات الآلية (Pytest)
    ├── conftest.py                    # التجهيزات: app, client, runner, auth
    ├── data.sql                       # بيانات اختبارية (مستخدمين ومنشورات وهمية)
    ├── test_factory.py                # اختبارات إنشاء المصنع وصفحة الترحيب
    ├── test_db.py                     # اختبارات تهيئة قاعدة البيانات والاستعلامات
    ├── test_auth.py                   # اختبارات تدفق المصادقة (تسجيل، دخول، خروج، تحقق)
    └── test_blog.py                   # اختبارات CRUD للمدونة (صلاحيات، تحقق، عمليات)
```

<hr />

## 👨‍💻 المؤلف والترخيص

تم تطوير وتوثيق **FaceBlog** بواسطة **مهندس سلمان سوفت (Salman Soft)** — مهندس برمجيات شغوف ومرشد تقني مكرس لصنع موارد تعليمية بجودة إنتاجية لمجتمع Python و Flask.

| التفاصيل | المعلومات |
|----------|-----------|
| **المؤلف** | مهندس سلمان سوفت (Salman Soft) |
| **الدور** | مهندس رئيسي ومرشد Full-Stack |
| **الترخيص** | رخصة MIT — مجاني للاستخدام الشخصي والتجاري |
| **المستودع** | [github.com/salman-dev-ai/flask-blog](https://github.com/salman-dev-ai/flask-blog) |
| **بُني بـ** | ❤️ Python 3, Flask 3.0, SQLite, Waitress, Pytest, Flit |

---

<p align="center">
  <strong>⭐ إذا وجدت هذا المشروع تعليميًا، فضلاً أعطه نجمة على GitHub!</strong>
  <br />
  <em>"أفضل طريقة للتعلم هي البناء. أفضل طريقة للتدريس هي إظهار المعاناة."</em>
  <br />
  — مهندس سلمان سوفت
</p>