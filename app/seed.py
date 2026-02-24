def seed_medicines(db):
    """从 药品数据.txt 解析并导入所有药品数据"""
    import os, re
    from .models import Medicine

    try:
        txt_path = os.path.join(os.path.dirname(__file__), '../药品数据.txt')
        if not os.path.exists(txt_path):
            print(f"Warning: 药品数据.txt not found at {txt_path}, skipping seed.")
            return

        with open(txt_path, encoding='utf-8') as f:
            content = f.read()

        blocks = re.split(r'\n\d+\.\n', content)

        def get_field(label, text):
            m = re.search(rf'{label}：(.+)', text)
            return m.group(1).strip() if m else ''

        medicines = []
        for block in blocks:
            block = block.strip()
            name = get_field('全称', block)
            if not name:
                continue
            medicines.append(Medicine(
                name=name,
                generic_name=get_field('简称', block),
                indications=get_field('适应症', block),
                dosage=get_field('用法用量', block),
                contraindications=get_field('禁忌症', block),
                side_effects=get_field('副作用', block),
                precautions=get_field('注意事项', block),
            ))

        db.session.add_all(medicines)
        db.session.commit()
        print(f"Done seeding {len(medicines)} medicines.")
    except Exception as e:
        print(f"Error seeding medicines: {e}")
