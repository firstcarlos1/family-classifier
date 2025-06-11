from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Family classification logic
def classify_family_member(age, gender, relationship_to_you):
    """
    Classify family member based on age, gender, and relationship
    """
    classifications = []
    
    # Age-based classification
    if age < 18:
        classifications.append("เด็ก/วัยรุ่น")
    elif age < 60:
        classifications.append("ผู้ใหญ่")
    else:
        classifications.append("ผู้สูงอายุ")
    
    # Relationship-based classification
    if relationship_to_you in ["พ่อ", "แม่"]:
        classifications.append("ผู้ปกครอง")
    elif relationship_to_you in ["ลูกชาย", "ลูกสาว"]:
        classifications.append("บุตร")
    elif relationship_to_you in ["พี่ชาย", "พี่สาว", "น้องชาย", "น้องสาว"]:
        classifications.append("พี่น้อง")
    elif relationship_to_you in ["ปู่", "ย่า", "ตา", "ยาย"]:
        classifications.append("ผู้สูงอายุในครอบครัว")
    
    # Gender-based classification
    if gender == "ชาย":
        classifications.append("สมาชิกครอบครัวเพศชาย")
    else:
        classifications.append("สมาชิกครอบครัวเพศหญิง")
    
    return classifications

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    try:
        data = request.get_json()
        
        name = data.get('name', '')
        age = int(data.get('age', 0))
        gender = data.get('gender', '')
        relationship = data.get('relationship', '')
        
        # Validate input
        if not all([name, age, gender, relationship]):
            return jsonify({
                'success': False,
                'error': 'กรุณากรอกข้อมูลให้ครบถ้วน'
            })
        
        if age < 0 or age > 150:
            return jsonify({
                'success': False,
                'error': 'อายุไม่ถูกต้อง'
            })
        
        # Classify family member
        classifications = classify_family_member(age, gender, relationship)
        
        return jsonify({
            'success': True,
            'name': name,
            'age': age,
            'gender': gender,
            'relationship': relationship,
            'classifications': classifications
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'ข้อมูลอายุไม่ถูกต้อง'
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
    # For Render deployment
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting Family Classifier on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)