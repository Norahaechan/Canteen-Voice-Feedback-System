from app.schemas.text_clean import TextCleanResult
from app.utils.shop_alias import load_shop_catalog, load_standard_shop_names


def build_analysis_prompt(clean_result: TextCleanResult) -> str:
    shop_names = load_standard_shop_names()
    shop_catalog = load_shop_catalog()
    return f"""
你是食堂反馈分析助手。请根据给定文本输出严格 JSON，不要输出额外说明。

系统内可选标准商铺名称：{shop_names}
已知店铺清单（用于店铺匹配，必须优先参考）：
{shop_catalog}
原始识别文本：{clean_result.original_text}
清洗后文本：{clean_result.cleaned_text}

请输出如下 JSON 结构：
{{
  "shop_name": "标准商铺名称",
  "sentiment_label": "正面|负面|中性",
  "sentiment_scores": {{
    "positive": 0.0,
    "negative": 0.0,
    "neutral": 0.0
  }},
  "issue_categories": ["口味", "排队效率"],
  "issue_weights": {{
    "口味": 0.6,
    "排队效率": 0.4
  }},
  "urgency": "高|中|低",
  "summary": "一句简洁中文摘要",
  "summary_en": "One concise English summary sentence"
}}

约束：
1. JSON 必须合法。
2. issue_weights 的键必须与 issue_categories 对齐，且总和接近 1。
3. 若文本更偏表扬，sentiment_label 用正面；若明显投诉，用负面；否则中性。
4. shop_name 必须直接根据“原始识别文本 + 清洗后文本 + 已知店铺清单”进行匹配，并且只能从“系统内可选标准商铺名称”中选择；禁止返回列表之外的新名称。
5. 不要依赖规则候选。即使用户输入存在语音识别错误、英文近音、拼写错误、空格拆分、同义表达或简称，也要结合已知店铺清单自主判断最接近的标准商铺。
6. 若文本里出现英文店铺名近义说法或误识别变体，例如 tripe/stomach/belly chicken、yuan jn/yuan ji、lan zhou/lanzhou、yi ming/yiming、gu ming/guming，需主动归并到最接近的标准商铺。
7. 只有在确实无法从文本中判断到任何已知店铺时，才返回“未知商铺”。
8. summary 必须是自然简洁的中文；summary_en 必须是与 summary 语义一致的自然英文。
9. issue_categories 只能从以下集合中选择：["口味", "价格", "卫生", "服务态度", "排队效率", "分量", "食材新鲜度", "出餐速度", "其他"]。
10. 对英文表扬类文本，若出现 delicious、tasty、yummy、flavor 等词，优先归为“口味”；若出现 fast、quick、wait、queue 等词，优先归为“排队效率”或“出餐速度”；只有确实无法归类时才用“其他”。
11. 你的首要任务之一是从已知店铺清单中完成店铺归属匹配，必须尽量提高召回，不要因为轻微拼写误差就返回“未知商铺”。
""".strip()
