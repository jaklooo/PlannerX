"""Contacts routes."""
from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, g

from app import db
from app.auth.firebase import require_auth
from app.models.contact import Contact

bp = Blueprint("contacts", __name__)


@bp.route("/")
@require_auth
def list_contacts():
    """List all contacts for current user."""
    user = g.current_user
    
    contacts = Contact.query.filter_by(user_id=user.id).order_by(Contact.name.asc()).all()
    
    if request.headers.get("Accept") == "application/json":
        return jsonify([contact.to_dict() for contact in contacts])
    
    return render_template("contacts.html", contacts=contacts)


@bp.route("/create", methods=["POST"])
@require_auth
def create_contact():
    """Create a new contact."""
    user = g.current_user
    data = request.get_json() if request.is_json else request.form
    
    contact = Contact(
        user_id=user.id,
        name=data.get("name"),
        email=data.get("email", ""),
        phone=data.get("phone", ""),
        notes=data.get("notes", ""),
    )
    
    # Parse birthday
    birthday_str = data.get("birthday_date")
    if birthday_str:
        try:
            contact.birthday_date = date.fromisoformat(birthday_str)
        except (ValueError, AttributeError):
            pass
    
    # Parse name day
    nameday_str = data.get("name_day_date")
    if nameday_str:
        try:
            contact.name_day_date = date.fromisoformat(nameday_str)
        except (ValueError, AttributeError):
            pass
    
    db.session.add(contact)
    db.session.commit()
    
    if request.is_json:
        return jsonify(contact.to_dict()), 201
    
    return jsonify({"success": True, "id": contact.id})


@bp.route("/<int:contact_id>", methods=["GET"])
@require_auth
def get_contact(contact_id):
    """Get a specific contact."""
    user = g.current_user
    contact = Contact.query.filter_by(id=contact_id, user_id=user.id).first_or_404()
    
    return jsonify(contact.to_dict())


@bp.route("/<int:contact_id>", methods=["PUT", "PATCH"])
@require_auth
def update_contact(contact_id):
    """Update a contact."""
    user = g.current_user
    contact = Contact.query.filter_by(id=contact_id, user_id=user.id).first_or_404()
    
    data = request.get_json() if request.is_json else request.form
    
    if "name" in data:
        contact.name = data["name"]
    if "email" in data:
        contact.email = data["email"]
    if "phone" in data:
        contact.phone = data["phone"]
    if "notes" in data:
        contact.notes = data["notes"]
    
    if "birthday_date" in data:
        birthday_str = data["birthday_date"]
        if birthday_str:
            try:
                contact.birthday_date = date.fromisoformat(birthday_str)
            except (ValueError, AttributeError):
                pass
        else:
            contact.birthday_date = None
    
    if "name_day_date" in data:
        nameday_str = data["name_day_date"]
        if nameday_str:
            try:
                contact.name_day_date = date.fromisoformat(nameday_str)
            except (ValueError, AttributeError):
                pass
        else:
            contact.name_day_date = None
    
    db.session.commit()
    
    return jsonify(contact.to_dict())


@bp.route("/<int:contact_id>", methods=["DELETE"])
@require_auth
def delete_contact(contact_id):
    """Delete a contact."""
    user = g.current_user
    contact = Contact.query.filter_by(id=contact_id, user_id=user.id).first_or_404()
    
    db.session.delete(contact)
    db.session.commit()
    
    return jsonify({"success": True})
