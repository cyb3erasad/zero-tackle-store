from datetime import datetime
from flask_login import UserMixin
from app.extensions import db, login_manager


# ======================================================================
# USER LOADER — required by Flask-Login
# ======================================================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ======================================================================
# USER
# ======================================================================

class User(db.Model, UserMixin):
    """
    Represents a registered user.
    is_admin flag separates normal users from admin panel access.
    """
    __tablename__ = 'users'

    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(80),  unique=True, nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(255), nullable=False)   # hashed
    is_admin   = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---- relationships ------------------------------------------------
    cart    = db.relationship('Cart',    backref='user', uselist=False,
                              cascade='all, delete-orphan')
    orders  = db.relationship('Order',  backref='user',
                              cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user',
                              cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


# ======================================================================
# CATEGORY
# ======================================================================

class Category(db.Model):
    """
    Product categories shown on the landing page.
    Examples: Jerseys, Footballs, Shorts, Accessories.
    slug is used in URLs e.g. /products/category/jerseys
    """
    __tablename__ = 'categories'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), unique=True, nullable=False)
    slug          = db.Column(db.String(100), unique=True, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)   # category card image

    # ---- relationships ------------------------------------------------
    products = db.relationship('Product', backref='category',
                               lazy='dynamic')

    def __repr__(self):
        return f'<Category {self.name}>'


# ======================================================================
# PRODUCT
# ======================================================================

class Product(db.Model):
    """
    Core product model.
    - has_sizes: True for jerseys/shorts (size + qty per size via ProductSize)
                 False for footballs/accessories (single stock field)
    - stock: used only when has_sizes=False
    - is_sold_out: admin can manually mark as sold out
    """
    __tablename__ = 'products'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    price       = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=True)
    stock       = db.Column(db.Integer, default=0)        # used if has_sizes=False
    has_sizes   = db.Column(db.Boolean, default=False)    # True → use ProductSize
    is_sold_out = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'),
                            nullable=False)

    # ---- relationships ------------------------------------------------
    images     = db.relationship('ProductImage', backref='product',
                                 cascade='all, delete-orphan')
    sizes      = db.relationship('ProductSize',  backref='product',
                                 cascade='all, delete-orphan')
    size_chart = db.relationship('SizeChart',    backref='product',
                                 uselist=False,
                                 cascade='all, delete-orphan')
    reviews    = db.relationship('Review',       backref='product',
                                 cascade='all, delete-orphan')
    cart_items  = db.relationship('CartItem',    backref='product')
    order_items = db.relationship('OrderItem',   backref='product')

    @property
    def primary_image(self):
        """Returns the primary image filename or None."""
        primary = ProductImage.query.filter_by(
            product_id=self.id, is_primary=True
        ).first()
        return primary.image_filename if primary else None

    @property
    def average_rating(self):
        """Calculates average rating from all reviews."""
        if not self.reviews:
            return 0
        return round(sum(r.rating for r in self.reviews) / len(self.reviews), 1)

    @property
    def total_stock(self):
        """
        Returns total available stock.
        For sized products: sum of all size quantities.
        For non-sized products: stock field directly.
        """
        if self.has_sizes:
            return sum(s.quantity for s in self.sizes)
        return self.stock

    def __repr__(self):
        return f'<Product {self.name}>'


# ======================================================================
# PRODUCT IMAGE
# ======================================================================

class ProductImage(db.Model):
    """
    A product can have multiple images.
    is_primary=True → shown as the main image on card and detail page.
    """
    __tablename__ = 'product_images'

    id             = db.Column(db.Integer, primary_key=True)
    product_id     = db.Column(db.Integer, db.ForeignKey('products.id'),
                               nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)
    is_primary     = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<ProductImage {self.image_filename}>'


# ======================================================================
# PRODUCT SIZE
# ======================================================================

class ProductSize(db.Model):
    """
    Per-size stock for products that have sizes (jerseys, shorts).
    size_label: S / M / L / XL / XXL
    Each row = one size option for a product with its own stock quantity.
    """
    __tablename__ = 'product_sizes'

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),
                           nullable=False)
    size_label = db.Column(db.String(10), nullable=False)   # S, M, L, XL, XXL
    quantity   = db.Column(db.Integer,    default=0)

    __table_args__ = (
        db.UniqueConstraint('product_id', 'size_label',
                            name='uq_product_size'),
    )

    def __repr__(self):
        return f'<ProductSize {self.size_label} qty={self.quantity}>'


# ======================================================================
# SIZE CHART
# ======================================================================

class SizeChart(db.Model):
    """
    One size chart image per product (optional).
    Shown as a popup/modal on the product detail page.
    """
    __tablename__ = 'size_charts'

    id             = db.Column(db.Integer, primary_key=True)
    product_id     = db.Column(db.Integer, db.ForeignKey('products.id'),
                               nullable=False)
    image_filename = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<SizeChart product_id={self.product_id}>'


# ======================================================================
# CART
# ======================================================================

class Cart(db.Model):
    """
    One cart per user (one-to-one with User).
    Created automatically when a user first adds something to cart.
    """
    __tablename__ = 'carts'

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        nullable=False, unique=True)

    # ---- relationships ------------------------------------------------
    items = db.relationship('CartItem', backref='cart',
                            cascade='all, delete-orphan')

    @property
    def subtotal(self):
        """Sum of (price × quantity) for all items in cart."""
        return sum(item.line_total for item in self.items)

    @property
    def item_count(self):
        """Total number of individual items in cart."""
        return sum(item.quantity for item in self.items)

    def __repr__(self):
        return f'<Cart user_id={self.user_id}>'


# ======================================================================
# CART ITEM
# ======================================================================

class CartItem(db.Model):
    """
    Each row = one product + size combination in a user's cart.
    size_label is None for products without sizes (footballs, etc.)
    """
    __tablename__ = 'cart_items'

    id         = db.Column(db.Integer, primary_key=True)
    cart_id    = db.Column(db.Integer, db.ForeignKey('carts.id'),
                           nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),
                           nullable=False)
    size_label = db.Column(db.String(10), nullable=True)   # None if no sizes
    quantity   = db.Column(db.Integer, default=1)

    @property
    def line_total(self):
        """Price × quantity for this cart item."""
        return self.product.price * self.quantity

    def __repr__(self):
        return (f'<CartItem product_id={self.product_id} '
                f'size={self.size_label} qty={self.quantity}>')


# ======================================================================
# ORDER
# ======================================================================

class Order(db.Model):
    """
    Created when a user confirms checkout.
    Stores a snapshot of shipping info and totals.
    cod_fee is always Rs 250 (fixed).
    status flow: pending → processing → shipped → delivered / cancelled
    """
    __tablename__ = 'orders'

    # Order status choices
    STATUS_PENDING    = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_SHIPPED    = 'shipped'
    STATUS_DELIVERED  = 'delivered'
    STATUS_CANCELLED  = 'cancelled'

    STATUS_CHOICES = [
        STATUS_PENDING,
        STATUS_PROCESSING,
        STATUS_SHIPPED,
        STATUS_DELIVERED,
        STATUS_CANCELLED,
    ]

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=False)
    status     = db.Column(db.String(20), default=STATUS_PENDING,
                           nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---- pricing snapshot --------------------------------------------
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    cod_fee  = db.Column(db.Numeric(10, 2), default=250.00, nullable=False)
    total    = db.Column(db.Numeric(10, 2), nullable=False)

    # ---- shipping info snapshot (stored at time of order) ------------
    first_name   = db.Column(db.String(80),  nullable=False)
    last_name    = db.Column(db.String(80),  nullable=False)
    email        = db.Column(db.String(120), nullable=False)
    phone        = db.Column(db.String(20),  nullable=False)
    country      = db.Column(db.String(100), nullable=False)
    street       = db.Column(db.String(255), nullable=False)
    apartment    = db.Column(db.String(255), nullable=True)
    city         = db.Column(db.String(100), nullable=False)
    state        = db.Column(db.String(100), nullable=False)

    # ---- relationships -----------------------------------------------
    items = db.relationship('OrderItem', backref='order',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order #{self.id} status={self.status}>'


# ======================================================================
# ORDER ITEM
# ======================================================================

class OrderItem(db.Model):
    """
    Snapshot of each product purchased in an order.
    price_at_purchase stores the price at time of order
    so future price changes don't affect old orders.
    """
    __tablename__ = 'order_items'

    id                = db.Column(db.Integer, primary_key=True)
    order_id          = db.Column(db.Integer, db.ForeignKey('orders.id'),
                                  nullable=False)
    product_id        = db.Column(db.Integer, db.ForeignKey('products.id'),
                                  nullable=False)
    size_label        = db.Column(db.String(10),    nullable=True)
    quantity          = db.Column(db.Integer,        nullable=False)
    price_at_purchase = db.Column(db.Numeric(10, 2), nullable=False)

    @property
    def line_total(self):
        """Price at purchase × quantity."""
        return self.price_at_purchase * self.quantity

    def __repr__(self):
        return (f'<OrderItem order_id={self.order_id} '
                f'product_id={self.product_id} qty={self.quantity}>')


# ======================================================================
# REVIEW
# ======================================================================

class Review(db.Model):
    """
    Product review left by a logged-in user.
    rating: 1–5 stars.
    One user can only review a product once (unique constraint).
    """
    __tablename__ = 'reviews'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'),
                           nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'),
                           nullable=False)
    rating     = db.Column(db.Integer, nullable=False)    # 1 to 5
    comment    = db.Column(db.Text,    nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'product_id',
                            name='uq_user_product_review'),
    )

    def __repr__(self):
        return f'<Review user_id={self.user_id} rating={self.rating}>'