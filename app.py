from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# PostgreSQL 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost/store_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 定义商品的数据库模型
class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, nullable=True,primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)

    def __init__(self, name, price):
        self.name = name
        self.price = price

@app.route('/')
def index():
    products = Product.query.all()  # 查询所有商品
    return render_template('index.html', products=products)

# 添加商品的路由
@app.route('/add', methods=['POST'])
def add_product():
    name = request.form['name']
    price = request.form['price']
    new_product = Product(name, price)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('index'))

# 编辑商品的路由
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', product=product)

# 删除商品的路由
@app.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)