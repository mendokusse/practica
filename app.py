from flask import Flask, render_template, request, jsonify, Response
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
    Email = db.Column(db.String(255))
    PhoneNumber = db.Column(db.String(20))

class Service(db.Model):
    __tablename__ = 'Services'

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrganizationID = db.Column(db.Integer, db.ForeignKey('Organizations.ID'), nullable=False)
    ServiceName = db.Column(db.String(255), nullable=False)
    Pricing = db.Column(db.Numeric(10, 2))

# Главная страница с формой выбора компании
@app.route('/analytics')
def analytics_form():
    companies = Organization.query.all()  # Получаем все компании для выбора в форме
    return render_template('index.html', companies=companies)

# Возвращаем информацию о компании в формате JSON
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
            'email': results[0].Email,
            'phone': results[0].PhoneNumber,
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
    
@app.route('/analytics/download', methods=['GET'])
def download_company_info():
    company_id = request.args.get('id')
    
    if not company_id:
        return render_template('index.html', error="Компания не выбрана")

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
                s.ServiceName,
                s.Pricing
            FROM 
                Organizations o
            LEFT JOIN 
                Services s ON o.ID = s.OrganizationID
            WHERE 
                o.ID = :id
            """), {'id': company_id}
        ).fetchall()

        if not results:
            return render_template('index.html', error="Компания не найдена")

        # Формируем текст для файла
        organization_data = f"Информация о компании {results[0].OrganizationName}:\n"
        if results[0].Website:
            organization_data += f"Вебсайт: {results[0].Website}\n"
        if results[0].IKS:
            organization_data += f"ИКС: {results[0].IKS}\n"
        if results[0].BacklinksCount:
            organization_data += f"Количество обратных ссылок: {results[0].BacklinksCount}\n"
        if results[0].Accreditation:
            organization_data += f"Аккредитация: {results[0].Accreditation}\n"
        if results[0].Email:
            organization_data += f"Email: {results[0].Email}\n"
        if results[0].PhoneNumber:
            organization_data += f"Телефон: {results[0].PhoneNumber}\n"

        services_data = ""
        for row in results:
            if row.ServiceName:
                service_info = f"- Услуга: {row.ServiceName}"
                if row.Pricing is not None:
                    service_info += f", Цена: {row.Pricing} руб."
                services_data += service_info + "\n"

        if services_data:
            organization_data += "\nУслуги:\n" + services_data

        # Возвращаем текстовый файл
        return Response(organization_data, mimetype='text/plain',
                        headers={"Content-Disposition": f"attachment;filename=company_{company_id}.txt"})

    except Exception as e:
        return render_template('index.html', error=f"Ошибка: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
