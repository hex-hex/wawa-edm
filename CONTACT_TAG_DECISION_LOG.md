# wawa-edm Contact Tag — 决策档案 (2026-07-12)

## 决定(2026-07-12)
**暂不改 schema。** 等用户重新发起"动 tag"指令再做。

## 现状(直接来自代码 + DB,2026-07-12 14:32+12 验证)

### Contact 的所有字段
| 字段 | 类型 | 备注 |
|---|---|---|
| id | UUID PK | |
| company | FK → Company | |
| first_name / middle_name / last_name | CharField, optional | |
| email | EmailField, optional | |
| role | CharField(63), optional | |
| phone | CharField(63), optional | |
| priority | CharField enum | hot / warm / cold |
| gender | CharField enum | male / female / other |
| subscribed | Boolean, default True | |
| **behavior** | TextField, optional, blank | **存在但未被任何代码读** |
| story | TextField, blank | |
| created_at / updated_at | DateTimeField | |

### 没有的东西
- ❌ `tags` 字段 / M2M 关系
- ❌ `ContactTag` 表
- ❌ `ContactSerializer.tags` 字段
- ❌ `ContactFilter.tags` 过滤
- ❌ Contact admin 里 tag list_filter / filter_horizontal

### 现有的 tag 系统
- ✅ `KnowledgeTag(name)` — 58 条左右,挂在 `Knowledge.tags` M2M 上
- ✅ `KnowledgeSerializer.tag_names` read-only + `tags` writable
- ✅ `/api/knowledge-tags/` ViewSet
- ✅ `?tags=` / `?tags__name=` 过滤在 Knowledge 上可用

### 65 个 contact 待 tag 的现状
- API count `?has_email_draft=false` = 65
- 用 cron 实际 `sensitive_filter.py v8.8` 跑 = sensitives=65, non_sensitives=0, 无 FP
- 分布:
  - edu (school/tutor/academy/ECE/driving school): ~30
  - finance (CA / bookkeeper / financial adviser / wealth mgmt): ~21
  - legal (K3 Legal ×4 + Simpsons): 5
  - immigration (Target Language Academy + ProVisas): ~5
  - insurance (Primesure + Insurely): 2
- 真分桶在 `/tmp/_check_65.py` 跑出的 65 行(待精确取)

## 三种实施方案(代价 + 风险)

### A. 复用 `KnowledgeTag` 表 + M2M 到 Contact
- 新代码: ~30 行
- 新迁移: 1 个 (~6 行)
- API: `Contact.tags` + `Contact.tag_names` 新增,既有 GET 客户端无破坏(只是字段多了)
- 优点: 复用现有 tag 系统, 5 min 工作
- 缺点: 同一字符串 tag 同时挂在 Knowledge 和 Contact 上,语义略混

### B. 新建 `ContactTag` + M2M
- 新代码: ~150 行(model + serializer + viewset + filter + admin + url)
- 新迁移: 2 个
- 优点: 语义干净, 完全独立
- 缺点: 工作量大, 改动 admin 测试面

### C. 软标记: 写 `behavior` 字段字符串
- 新代码: 0
- 迁移: 0
- 优点: 立即可做
- 缺点: 无法结构化查询, 只能 grep `behavior__icontains="sensitive-regulated"`

## 推荐(等用户拍板时直接做)

**选 A**,精确代码改动:

```python
# core/models/contact.py — +6 行
from .knowledge import KnowledgeTag

class Contact(models.Model):
    # ... 既有字段 ...
    tags = models.ManyToManyField(
        KnowledgeTag,
        related_name="contacts",
        blank=True,
    )
```

```python
# core/serializers/contact.py — +8 行
from ..models import Contact, KnowledgeTag

class ContactSerializer(serializers.ModelSerializer):
    # ... 既有 ...
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=KnowledgeTag.objects.all(), required=False,
    )
    tag_names = serializers.SlugRelatedField(
        many=True, read_only=True, source="tags", slug_field="name",
    )
    class Meta:
        fields = [..., "tags", "tag_names", ...]
```

```python
# core/views/contact.py — +1 行
search_fields = [..., "tags__name"]

# core/filters.py — 给 ContactFilter +tags / tags__name 字段

# core/admin.py — ContactAdmin 加 filter_horizontal = ("tags",)
```

```bash
python manage.py makemigrations
python manage.py migrate
```

## 一旦 schema 改完,下一步(用户触发时再做)

1. POST 5 个 KnowledgeTag:
   - `legal` / `accounting` / `education` / `immigration` / `financial-advice` / `insurance-broker`
2. PATCH 65 个 contact 把 tag 挂上去
3. cron `email_draft_writing_1by1` 可以用 `?tags__name=education` 等筛选
4. 复活 cron:走 task `c22533f1-d724-4548-aeed-74ab9ba79651` (Wāwā Assistant · Regulated) 而不是 62344806

## 决定历史
- 2026-07-12 14:32 — 用户问 "contact 有 tag 吗?",回答: 没有。提议 3 方案。
- 2026-07-12 14:50 — 用户问 "是不是另一个 task 写?",发现 task c22533f1 已预备好(0 drafts)
- 2026-07-12 14:55 — 用户决定: "先增加 tag 标记,不用后续处理"
- 2026-07-12 15:05 — 用户澄清问实施范围,超时未回应
- 2026-07-12 15:05 — 默认 "现在不动", 把档案写到这里

## 下次用户说 "做" 的时候
按"推荐 A" 一气做完。