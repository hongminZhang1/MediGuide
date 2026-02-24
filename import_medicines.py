"""
从 药品数据.txt 解析药品信息，清除旧数据，批量导入新数据
"""
import re
import os
import sys

# 确保在项目根目录运行
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.extensions import db
from app.models import Medicine

def parse_medicines(filepath):
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # 按编号分割每条药品记录
    # 匹配 "数字.\n全称：..." 的块
    blocks = re.split(r'\n\d+\.\n', content)
    # 第一块是分类标题，不含药品，跳过空/标题块

    medicines = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue

        def get_field(label, text):
            m = re.search(rf'{label}：(.+)', text)
            return m.group(1).strip() if m else ''

        name      = get_field('全称', block)
        if not name:
            continue

        medicines.append({
            'name':              name,
            'generic_name':      get_field('简称', block),
            'indications':       get_field('适应症', block),
            'dosage':            get_field('用法用量', block),
            'contraindications': get_field('禁忌症', block),
            'side_effects':      get_field('副作用', block),
            'precautions':       get_field('注意事项', block),
        })

    return medicines


def main():
    app = create_app()
    with app.app_context():
        # 1. 删除所有旧药品
        old_count = Medicine.query.count()
        Medicine.query.delete()
        db.session.commit()
        print(f"已删除 {old_count} 条旧药品数据")

        # 2. 解析 txt 文件
        txt_path = os.path.join(os.path.dirname(__file__), '药品数据.txt')
        medicines_data = parse_medicines(txt_path)
        print(f"解析到 {len(medicines_data)} 条新药品数据")

        # 3. 批量插入
        for d in medicines_data:
            m = Medicine(**d)
            db.session.add(m)
        db.session.commit()

        print(f"✅ 成功导入 {len(medicines_data)} 条药品数据")
        # 打印前5条验证
        for m in Medicine.query.limit(5).all():
            print(f"  [{m.id}] {m.name} / {m.generic_name}")


if __name__ == '__main__':
    main()
