from flask import redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.reviews import reviews_bp
from app.models import Review, Product
from app.extensions import db


# ======================================================================
# ADD REVIEW
# ======================================================================

@reviews_bp.route('/add/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    """
    Handles review form submission from the product detail page.
    - Only logged-in users can submit (enforced by @login_required)
    - One review per user per product (enforced by DB unique constraint)
    - Validates rating is between 1 and 5
    - Redirects back to product detail page in all cases
    """
    product = Product.query.get_or_404(product_id)

    # ---- check if already reviewed ----------------------------------
    existing = Review.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if existing:
        flash('You have already reviewed this product.', 'warning')
        return redirect(url_for('products.detail', product_id=product_id))

    # ---- validate rating --------------------------------------------
    try:
        rating = int(request.form.get('rating', 0))
    except (ValueError, TypeError):
        rating = 0

    if rating < 1 or rating > 5:
        flash('Please select a rating between 1 and 5 stars.', 'warning')
        return redirect(url_for('products.detail', product_id=product_id))

    # ---- get optional comment ---------------------------------------
    comment = request.form.get('comment', '').strip()
    if not comment:
        comment = None

    # ---- save review ------------------------------------------------
    review = Review(
        user_id    = current_user.id,
        product_id = product_id,
        rating     = rating,
        comment    = comment,
    )
    db.session.add(review)
    db.session.commit()

    flash('Your review has been submitted. Thank you!', 'success')
    return redirect(url_for('products.detail', product_id=product_id))


# ======================================================================
# DELETE REVIEW (own review only)
# ======================================================================

@reviews_bp.route('/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    """
    Allows a user to delete their own review.
    Admins can also delete any review via the admin panel.
    """
    review = Review.query.get_or_404(review_id)

    # Only the review author or an admin can delete
    if review.user_id != current_user.id and not current_user.is_admin:
        flash('You are not allowed to delete this review.', 'danger')
        return redirect(url_for('products.detail', product_id=review.product_id))

    product_id = review.product_id
    db.session.delete(review)
    db.session.commit()

    flash('Review deleted successfully.', 'info')
    return redirect(url_for('products.detail', product_id=product_id))