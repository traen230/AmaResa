import csv
import re
from datetime import datetime

from pytrends.request import TrendReq


class GoogleTrendsCollector:
    def __init__(self, geo="JP", hl="ja-JP", tz=540):
        self.pytrends = TrendReq(
            hl=hl,
            tz=tz,
            timeout=(10, 25),
            retries=2,
            backoff_factor=0.2,
        )
        self.geo = geo

    def _normalize_keyword(self, keyword):
        if not isinstance(keyword, str):
            return ""
        kw = keyword.strip().lower()
        kw = re.sub(r"[\u3000\s/\\|,、。・\-]+", " ", kw).strip()
        return kw

    def _split_single_terms(self, keyword):
        normalized = self._normalize_keyword(keyword)
        if not normalized:
            return []

        terms = []
        for term in normalized.split():
            clean = re.sub(r"[^\wぁ-んァ-ン一-龥ー]", "", term)
            if len(clean) < 2:
                continue
            if clean.isdigit():
                continue
            terms.append(clean)
        return terms

    def _extract_raw_keywords(self):
        # 1) Daily Trends (安定)
        try:
            today = self.pytrends.today_searches(pn=self.geo)
            if hasattr(today, "tolist"):
                rows = today.tolist()
            else:
                rows = list(today)
            if rows:
                return rows
        except Exception as e:
            print(f"[WARN] GoogleTrends dailytrends 取得失敗: {e}")

        # 2) Realtime Trends (フォールバック)
        try:
            realtime = self.pytrends.realtime_trending_searches(pn=self.geo, cat="all", count=100)
            rows = []
            if "title" in realtime.columns:
                for value in realtime["title"].tolist():
                    if isinstance(value, dict):
                        title_text = value.get("query") or value.get("title") or ""
                        if title_text:
                            rows.append(title_text)
                    elif isinstance(value, str):
                        rows.append(value)
            return rows
        except Exception as e:
            print(f"[WARN] GoogleTrends realtime 取得失敗: {e}")

        return []

    def get_amazon_single_keywords(self, limit=20):
        raw_keywords = self._extract_raw_keywords()
        if not raw_keywords:
            return []

        keywords = []
        seen = set()
        for raw in raw_keywords:
            for term in self._split_single_terms(raw):
                if term in seen:
                    continue
                seen.add(term)
                keywords.append(term)
                if len(keywords) >= limit:
                    return keywords

        return keywords[:limit]

    def export_csv(self, keywords, prefix="google_trends"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{prefix}_{timestamp}.csv"

        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(["キーワード", "取得元"])
            for keyword in keywords:
                writer.writerow([keyword, "GoogleTrends"])

        print(f"✅ CSV出力完了: {path}")
        return path
