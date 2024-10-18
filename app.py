from flask import Flask, jsonify   
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  

app = Flask(__name__)   

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f"mssql+pyodbc://sa:<CK6d/ehm>@94.241.174.143:1433/analytics?driver=ODBC+Driver+17+for+SQL+Server"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Organization(db.Model): 
    __tablename__ = 'Organizations'  

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    OrganizationName = db.Column(db.String(255), nullable=False)
    Website = db.Column(db.String(255))
    IKS = db.Column(db.Numeric(10, 2))
    BacklinksCount = db.Column(db.Integer)
    Accreditation = db.Column(db.String(100)) 

class Service(db.Model):
    __tablename__ = 'Services'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrganizationID = db.Column(db.Integer, db.ForeignKey('Organizations.ID'), nullable=False)
    ServiceName = db.Column(db.String(255), nullable=False)
    Pricing = db.Column(db.Numeric(10, 2))

@app.route('/analytics/<int:id>', methods=['GET'])  
def get_organization_with_services(id):
    try:
        results = db.session.execute(
            text("""
            SELECT 
                o.ID AS organization_id, 
                o.OrganizationName, 
                o.Website, 
                o.IKS, 
                o.BacklinksCount, 
                o.Accreditation,
                o.Email,
                o.PhoneNumber,
                s.ID as service_id,
                s.ServiceName,
                s.Pricing
            FROM 
                Organizations o
            LEFT JOIN 
                Services s ON o.ID = s.OrganizationID
            WHERE 
                o.ID = :id
            """), {'id': id}
        ).fetchall()

        if not results: 
            return jsonify({'error': 'Organization not found'}), 404

        organization_data = {
            'id': results[0].organization_id,
            'name': results[0].OrganizationName,
            'website': results[0].Website,
            'E-mail': results[0].Email,
            'PhoneNumber': results[0].PhoneNumber,
            'iks': results[0].IKS,
            'backlinks_count': results[0].BacklinksCount,
            'accreditation': results[0].Accreditation,
            'services': []
        }

        for row in results:
            if row.service_id is not None:
                service_data = {
                    'name': row.ServiceName,
                    'pricing': row.Pricing
                }
                organization_data['services'].append(service_data)

        return jsonify(organization_data), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
