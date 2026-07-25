from collections import Counter
import re


def statistics(pdf, text):

    words = text.split()

    print("=" * 40)
    print("📄 صفحات:", len(pdf))
    print("📝 کلمات:", len(words))
    print("🔤 کاراکتر:", len(text))
    print("⏱️ زمان مطالعه:", round(len(words) / 200, 2), "دقیقه")
    print("=" * 40)