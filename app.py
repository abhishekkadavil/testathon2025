from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for simplicity
employees = []

# GET /employee
@app.route('/employee', methods=['GET'])
def get_employees():
    return jsonify(employees), 200

@app.route('/department', methods=['GET'])
def get_departments():
    return jsonify(["HR", "Engineering"])

@app.route('/employees/types', methods=['GET'])
def get_departments():
    return jsonify(["Contract", "Permanent"])

# POST /employee
@app.route('/employee', methods=['POST'])
def add_employee():
    data = request.get_json()
    if not data or "name" not in data or "role" not in data:
        return jsonify({"error": "Invalid input"}), 400
    
    employee = {
        "id": len(employees) + 1,
        "name": data["name"],
        "role": data["role"]
    }
    employees.append(employee)
    return jsonify(employee), 201

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

