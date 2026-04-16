from flask import render_template, request
from app.products import products_bp
from app.models import Category, Product


# ======================================================================
# LANDING PAGE — categories grid
# ======================================================================

@products_bp.route('/')
def index():
    """
    Landing page — shows all categories as clickable cards.
    """
    categories = Category.query.all()
    return render_template('products/index.html', categories=categories)


# ======================================================================
# CATEGORY PAGE — all products in a category
# ======================================================================

@products_bp.route('/category/<slug>')
def category(slug):
    """
    Shows all products belonging to a category.
    Uses slug for clean URLs e.g. /products/category/jerseys
    """
    cat = Category.query.filter_by(slug=slug).first_or_404()

    products = Product.query.filter_by(
        category_id=cat.id
    ).order_by(Product.created_at.desc()).all()

    return render_template(
        'products/category.html',
        category=cat,
        products=products
    )


# ======================================================================
# SEARCH
# ======================================================================

@products_bp.route('/search')
def search():
    """
    Search products by name or description.
    Query param: ?q=searchterm
    """
    query = request.args.get('q', '').strip()
    results = []

    if query:
        results = Product.query.filter(
            Product.name.ilike(f'%{query}%') |
            Product.description.ilike(f'%{query}%')
        ).order_by(Product.created_at.desc()).all()

    return render_template(
        'products/search.html',
        query=query,
        results=results
    )