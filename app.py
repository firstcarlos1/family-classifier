from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    data = request.get_json()
    members = data.get('members', [])
    relationships = data.get('relationships', {})

    family_type = "ไม่สามารถจำแนกได้"

    if relationships.get('is_teenage_family'):
        family_type = "ครอบครัววัยรุ่น"
    elif relationships.get('is_step_family'):
        family_type = "ครอบครัวผสม"
    elif relationships.get('is_same_sex_couple'):
        family_type = "ครอบครัวคู่รักเพศเดียวกัน"
    elif relationships.get('is_only_elderly'):
        family_type = "ครอบครัวที่ผู้สูงอายุอยู่ด้วยกันลำพัง"
    elif relationships.get('is_skipped_generation'):
        family_type = "ครอบครัวข้ามรุ่น"
    elif relationships.get('is_single_parent'):
        family_type = "ครอบครัวพ่อหรือแม่เลี้ยงเดี่ยว"
    else:
        generations = set()
        for m in members:
            if m['relation'] in ['child']:
                generations.add('child')
            elif m['relation'] in ['father', 'mother', 'mother-in-law']:
                generations.add('parent')
            elif m['relation'] in ['grandparent']:
                generations.add('grandparent')
            elif m['relation'] in ['husband', 'wife']:
                generations.add('couple')

        if 'grandparent' in generations and 'child' in generations:
            family_type = "ครอบครัวขยาย"
        elif len(generations) == 1 and 'couple' in generations:
            family_type = "ครอบครัวเดี่ยว"
        else:
            family_type = "ครอบครัวเดี่ยว"

    return jsonify({'family_type': family_type})

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

