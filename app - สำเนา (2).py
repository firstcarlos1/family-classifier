from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    members = data.get('members', [])
    
    family_type = "ไม่สามารถจำแนกได้"
    
    # ตรวจสอบครอบครัววัยรุ่น
    if is_teenage_family(members):
        family_type = "ครอบครัววัยรุ่น"
    # ตรวจสอบครอบครัวผสม
    elif is_step_family(members):
        family_type = "ครอบครัวผสม"
    # ตรวจสอบครอบครัวพ่อหรือแม่เลี้ยงเดี่ยว
    elif is_single_parent_family(members):
        family_type = "ครอบครัวพ่อหรือแม่เลี้ยงเดี่ยว"
    # ตรวจสอบครอบครัวข้ามรุ่น
    elif is_skipped_generation_family(members):
        family_type = "ครอบครัวข้ามรุ่น"
    # ตรวจสอบครอบครัวผู้สูงอายุ
    elif is_elderly_only_family(members):
        family_type = "ครอบครัวที่ผู้สูงอายุอยู่ด้วยกันตามลำพัง"
    # ตรวจสอบครอบครัวคู่รักเพศเดียวกัน
    elif is_same_sex_couple_family(members):
        family_type = "ครอบครัวคู่รักเพศเดียวกัน"
    # ตรวจสอบครอบครัวขยาย
    elif is_extended_family(members):
        family_type = "ครอบครัวขยาย"
    # ตรวจสอบครอบครัวเดี่ยว
    elif is_nuclear_family(members):
        family_type = "ครอบครัวเดี่ยว"
    
    return jsonify({'family_type': family_type})

def is_teenage_family(members):
    """ครอบครัววัยรุ่น: สามี+ภรรยา อายุ<20, ลูก(ถ้ามี)อายุ<20"""
    husband = None
    wife = None
    children = []
    
    for member in members:
        if member['relation'] == 'husband':
            husband = member
        elif member['relation'] == 'wife':
            wife = member
        elif member['relation'] == 'child':
            children.append(member)
    
    # ต้องมีสามีและภรรยา
    if not husband or not wife:
        return False
    
    # สามีและภรรยาต้องอายุ < 20
    if husband['age'] >= 20 or wife['age'] >= 20:
        return False
    
    # ลูก(ถ้ามี)ต้องอายุ < 20
    for child in children:
        if child['age'] >= 20:
            return False
    
    return True

def is_step_family(members):
    """ครอบครัวผสม: สามีมีลูกติด และ/หรือ ภรรยามีลูกติด"""
    husband = None
    wife = None
    
    for member in members:
        if member['relation'] == 'husband':
            husband = member
        elif member['relation'] == 'wife':
            wife = member
    
    # ต้องมีสามีและภรรยา
    if not husband or not wife:
        return False
    
    # ตรวจสอบว่ามีลูกติด (ในที่นี้ใช้ attribute has_stepchild)
    return husband.get('has_stepchild', False) or wife.get('has_stepchild', False)

def is_single_parent_family(members):
    """ครอบครัวพ่อหรือแม่เลี้ยงเดี่ยว: สามีหรือภรรยา + ลูกอายุ<20"""
    parents = []
    children = []
    
    for member in members:
        if member['relation'] in ['husband', 'wife']:
            parents.append(member)
        elif member['relation'] == 'child':
            children.append(member)
    
    # ต้องมีพ่อหรือแม่คนเดียว และมีลูก
    if len(parents) != 1 or len(children) == 0:
        return False
    
    # ลูกต้องอายุ < 20
    for child in children:
        if child['age'] >= 20:
            return False
    
    return True

def is_skipped_generation_family(members):
    """ครอบครัวข้ามรุ่น: ปู่ย่าตายาย + หลาน (ไม่มีพ่อแม่)"""
    grandparents = []
    grandchildren = []
    parents = []
    
    for member in members:
        if member['relation'] == 'grandparent':
            grandparents.append(member)
        elif member['relation'] == 'child':
            grandchildren.append(member)
        elif member['relation'] in ['husband', 'wife', 'father', 'mother']:
            parents.append(member)
    
    # ต้องมีปู่ย่าตายาย และหลาน แต่ไม่มีพ่อแม่
    return len(grandparents) > 0 and len(grandchildren) > 0 and len(parents) == 0

def is_elderly_only_family(members):
    """ครอบครัวผู้สูงอายุ: สมาชิกทุกคนอายุ > 60"""
    if len(members) == 0:
        return False
    
    for member in members:
        if member['age'] <= 60:
            return False
    
    return True

def is_same_sex_couple_family(members):
    """ครอบครัวคู่รักเพศเดียวกัน: สามี+ภรรยา เพศเดียวกัน"""
    husband = None
    wife = None
    
    for member in members:
        if member['relation'] == 'husband':
            husband = member
        elif member['relation'] == 'wife':
            wife = member
    
    # ต้องมีสามีและภรรยา
    if not husband or not wife:
        return False
    
    # ต้องเป็นเพศเดียวกัน
    return husband['gender'] == wife['gender']

def is_extended_family(members):
    """ครอบครัวขยาย: สามี+ภรรยา+ลูก+ญาติพี่น้อง/พ่อแม่"""
    core_family = []
    extended_members = []
    
    for member in members:
        if member['relation'] in ['husband', 'wife', 'child']:
            core_family.append(member)
        elif member['relation'] in ['father', 'mother', 'grandparent', 'mother-in-law', 'sibling']:
            extended_members.append(member)
    
    # ต้องมีครอบครัวแกนกลาง และญาติพี่น้อง
    husband = any(m['relation'] == 'husband' for m in core_family)
    wife = any(m['relation'] == 'wife' for m in core_family)
    
    return husband and wife and len(extended_members) > 0

def is_nuclear_family(members):
    """ครอบครัวเดี่ยว: สามี+ภรรยา+ลูก"""
    husband = False
    wife = False
    has_children = False
    
    for member in members:
        if member['relation'] == 'husband':
            husband = True
        elif member['relation'] == 'wife':
            wife = True
        elif member['relation'] == 'child':
            has_children = True
        elif member['relation'] in ['grandparent', 'mother-in-law', 'father']:
            return False  # มีญาติอื่น = ไม่ใช่ครอบครัวเดี่ยว
    
    return husband and wife and has_children

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)