from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

def classify_family_type(members):
    """
    จำแนกประเภทครอบครัวตามสมาชิก
    """
    # ตรวจสอบสมาชิกแต่ละประเภท
    spouses = [m for m in members if m['relation'] in ['husband', 'wife']]
    children = [m for m in members if m['relation'] == 'child']
    parents = [m for m in members if m['relation'] in ['father', 'mother']]
    grandparents = [m for m in members if m['relation'] == 'grandparent']
    others = [m for m in members if m['relation'] in ['sibling', 'mother-in-law']]
    
    # มีลูกติดจากความสัมพันธ์เดิม
    has_stepchildren = any(m.get('has_stepchild', False) for m in members)
    
    # ตรวจสอบอายุ
    all_ages = [m['age'] for m in members]
    spouse_ages = [m['age'] for m in spouses]
    
    # 1. ครอบครัววัยรุ่น
    if spouses and all(age < 20 for age in spouse_ages):
        if not children or all(m['age'] < 20 for m in children):
            return "ครอบครัววัยรุ่น"
    
    # 2. ครอบครัวผสม
    if has_stepchildren:
        return "ครอบครัวผสม"
    
    # 3. ครอบครัวพ่อแม่เลี้ยงเดี่ยว
    if len(spouses) == 1 and children and any(m['age'] < 20 for m in children):
        return "ครอบครัวพ่อแม่เลี้ยงเดี่ยว"
    
    # 4. ครอบครัวข้ามรุ่น (ปู่ย่ากับหลาน)
    if grandparents and children and not spouses and not parents:
        return "ครอบครัวข้ามรุ่น"
    
    # 5. ครอบครัวผู้สูงอายุ
    if all(age > 60 for age in all_ages):
        return "ครอบครัวผู้สูงอายุ"
    
    # 6. ครอบครัวคู่รักเพศเดียวกัน
    if len(spouses) == 2:
        spouse_genders = [m['gender'] for m in spouses]
        if spouse_genders[0] == spouse_genders[1]:
            return "ครอบครัวคู่รักเพศเดียวกัน"
    
    # 7. ครอบครัวขยาย
    if spouses and children and (parents or grandparents or others):
        return "ครอบครัวขยาย"
    
    # 8. ครอบครัวเดี่ยว
    if spouses and children and not parents and not grandparents and not others:
        return "ครอบครัวเดี่ยว"
    
    # 9. ครอบครัวคู่รัก (ไม่มีลูก)
    if spouses and not children:
        return "ครอบครัวคู่รัก"
    
    # กรณีอื่นๆ
    return "ครอบครัวแบบอื่นๆ"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    try:
        data = request.get_json()
        members = data.get('members', [])
        
        if not members:
            return jsonify({
                'success': False,
                'error': 'กรุณาเพิ่มสมาชิกในครอบครัวก่อน'
            })
        
        # ตรวจสอบข้อมูลของสมาชิกแต่ละคน
        for member in members:
            if not all(key in member for key in ['relation', 'age', 'gender']):
                return jsonify({
                    'success': False,
                    'error': 'ข้อมูลสมาชิกไม่ครบถ้วน'
                })
            
            if member['age'] < 0 or member['age'] > 150:
                return jsonify({
                    'success': False,
                    'error': 'อายุไม่ถูกต้อง'
                })
        
        # จำแนกประเภทครอบครัว
        family_type = classify_family_type(members)
        
        return jsonify({
            'success': True,
            'family_type': family_type,
            'member_count': len(members)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'เกิดข้อผิดพลาด: {str(e)}'
        })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # สำหรับ Render deployment
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Family Classifier on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
