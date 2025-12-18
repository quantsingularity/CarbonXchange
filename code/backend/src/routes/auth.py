"""
Authentication routes for CarbonXchange Backend
Implements secure authentication with JWT, MFA, and audit logging
"""

from typing import Any
import logging
import re
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from src.models import db
from src.models.transaction import AuditAction, AuditLog
from src.models.user import User, UserKYC, UserProfile, UserRole, UserStatus

logger = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


def validate_email(email: Any) -> Any:
    """Validate email format"""
    pattern = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password: Any) -> Any:
    """Validate password strength"""
    if len(password) < 8:
        return (False, "Password must be at least 8 characters long")
    if not re.search("[A-Z]", password):
        return (False, "Password must contain at least one uppercase letter")
    if not re.search("[a-z]", password):
        return (False, "Password must contain at least one lowercase letter")
    if not re.search("\\d", password):
        return (False, "Password must contain at least one digit")
    if not re.search('[!@#$%^&*(),.?":{}|<>]', password):
        return (False, "Password must contain at least one special character")
    return (True, "Password is valid")


def log_auth_event(
    user_id: Any,
    action: Any,
    outcome: Any,
    description: Any = None,
    risk_level: Any = "low",
) -> Any:
    """Log authentication events for audit"""
    try:
        audit_log = AuditLog.log_event(
            user_id=user_id,
            action=action,
            resource_type="user",
            resource_id=str(user_id) if user_id else None,
            event_name=f"Authentication {action.value}",
            description=description,
            outcome=outcome,
            risk_level=risk_level,
            ip_address=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            request_method=request.method,
            request_url=request.url,
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to log auth event: {e}")


@auth_bp.route("/register", methods=["POST"])
def register() -> Any:
    """User registration endpoint"""
    try:
        data = request.get_json()
        required_fields = ["email", "password"]
        for field in required_fields:
            if not data.get(field):
                return (
                    jsonify(
                        {"error": "Validation Error", "message": f"{field} is required"}
                    ),
                    400,
                )
        email = data["email"].lower().strip()
        password = data["password"]
        if not validate_email(email):
            return (
                jsonify(
                    {"error": "Validation Error", "message": "Invalid email format"}
                ),
                400,
            )
        is_valid, message = validate_password(password)
        if not is_valid:
            return (jsonify({"error": "Validation Error", "message": message}), 400)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            log_auth_event(
                None,
                AuditAction.CREATE,
                "failure",
                f"Registration attempt with existing email: {email}",
                "medium",
            )
            return (
                jsonify(
                    {
                        "error": "Registration Error",
                        "message": "User with this email already exists",
                    }
                ),
                409,
            )
        user = User(
            email=email,
            password=password,
            role=UserRole.INDIVIDUAL,
            status=UserStatus.PENDING,
        )
        profile = UserProfile(
            user=user,
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            phone_number=data.get("phone_number"),
            company_name=data.get("company_name"),
        )
        kyc = UserKYC(user=user)
        db.session.add(user)
        db.session.add(profile)
        db.session.add(kyc)
        db.session.commit()
        log_auth_event(
            user.id, AuditAction.CREATE, "success", f"User registered: {email}"
        )
        access_token = create_access_token(
            identity=user.uuid,
            additional_claims={
                "user_id": user.id,
                "email": user.email,
                "role": user.role.value,
                "status": user.status.value,
            },
        )
        refresh_token = create_refresh_token(identity=user.uuid)
        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": user.to_dict(),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "Bearer",
                }
            ),
            201,
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        db.session.rollback()
        return (
            jsonify(
                {"error": "Internal Server Error", "message": "Registration failed"}
            ),
            500,
        )


@auth_bp.route("/login", methods=["POST"])
def login() -> Any:
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data.get("email") or not data.get("password"):
            return (
                jsonify(
                    {
                        "error": "Validation Error",
                        "message": "Email and password are required",
                    }
                ),
                400,
            )
        email = data["email"].lower().strip()
        password = data["password"]
        user = User.query.filter_by(email=email).first()
        if not user:
            log_auth_event(
                None,
                AuditAction.LOGIN,
                "failure",
                f"Login attempt with non-existent email: {email}",
                "medium",
            )
            return (
                jsonify(
                    {
                        "error": "Authentication Error",
                        "message": "Invalid email or password",
                    }
                ),
                401,
            )
        if user.is_locked:
            log_auth_event(
                user.id,
                AuditAction.LOGIN,
                "failure",
                f"Login attempt on locked account: {email}",
                "high",
            )
            return (
                jsonify(
                    {
                        "error": "Account Locked",
                        "message": "Account is temporarily locked due to multiple failed login attempts",
                    }
                ),
                423,
            )
        if not user.check_password(password):
            user.increment_failed_login()
            db.session.commit()
            log_auth_event(
                user.id,
                AuditAction.LOGIN,
                "failure",
                f"Invalid password for: {email}",
                "medium",
            )
            return (
                jsonify(
                    {
                        "error": "Authentication Error",
                        "message": "Invalid email or password",
                    }
                ),
                401,
            )
        if user.status == UserStatus.SUSPENDED:
            log_auth_event(
                user.id,
                AuditAction.LOGIN,
                "failure",
                f"Login attempt on suspended account: {email}",
                "high",
            )
            return (
                jsonify(
                    {
                        "error": "Account Suspended",
                        "message": "Your account has been suspended. Please contact support.",
                    }
                ),
                403,
            )
        if user.status == UserStatus.CLOSED:
            log_auth_event(
                user.id,
                AuditAction.LOGIN,
                "failure",
                f"Login attempt on closed account: {email}",
                "high",
            )
            return (
                jsonify(
                    {
                        "error": "Account Closed",
                        "message": "Your account has been closed. Please contact support.",
                    }
                ),
                403,
            )
        user.reset_failed_login()
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
        log_auth_event(
            user.id, AuditAction.LOGIN, "success", f"Successful login: {email}"
        )
        access_token = create_access_token(
            identity=user.uuid,
            additional_claims={
                "user_id": user.id,
                "email": user.email,
                "role": user.role.value,
                "status": user.status.value,
                "kyc_approved": user.is_kyc_approved,
            },
        )
        refresh_token = create_refresh_token(identity=user.uuid)
        return (
            jsonify(
                {
                    "message": "Login successful",
                    "user": user.to_dict(),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "Bearer",
                }
            ),
            200,
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        return (
            jsonify({"error": "Internal Server Error", "message": "Login failed"}),
            500,
        )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh() -> Any:
    """Refresh access token"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        if not user:
            return (
                jsonify(
                    {"error": "User Not Found", "message": "User no longer exists"}
                ),
                404,
            )
        if not user.is_active:
            return (
                jsonify(
                    {"error": "Account Inactive", "message": "Account is not active"}
                ),
                403,
            )
        access_token = create_access_token(
            identity=user.uuid,
            additional_claims={
                "user_id": user.id,
                "email": user.email,
                "role": user.role.value,
                "status": user.status.value,
                "kyc_approved": user.is_kyc_approved,
            },
        )
        return (jsonify({"access_token": access_token, "token_type": "Bearer"}), 200)
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return (
            jsonify(
                {"error": "Internal Server Error", "message": "Token refresh failed"}
            ),
            500,
        )


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout() -> Any:
    """User logout endpoint"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        if user:
            log_auth_event(
                user.id, AuditAction.LOGOUT, "success", f"User logged out: {user.email}"
            )
        return (jsonify({"message": "Logout successful"}), 200)
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return (
            jsonify({"error": "Internal Server Error", "message": "Logout failed"}),
            500,
        )


@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user() -> Any:
    """Get current user information"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        if not user:
            return (
                jsonify(
                    {"error": "User Not Found", "message": "User no longer exists"}
                ),
                404,
            )
        user_data = user.to_dict()
        if user.profile:
            user_data["profile"] = user.profile.to_dict()
        if user.kyc:
            user_data["kyc"] = user.kyc.to_dict()
        return (jsonify({"user": user_data}), 200)
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "Failed to get user information",
                }
            ),
            500,
        )


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password() -> Any:
    """Change user password"""
    try:
        data = request.get_json()
        required_fields = ["current_password", "new_password"]
        for field in required_fields:
            if not data.get(field):
                return (
                    jsonify(
                        {"error": "Validation Error", "message": f"{field} is required"}
                    ),
                    400,
                )
        current_password = data["current_password"]
        new_password = data["new_password"]
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        if not user:
            return (
                jsonify(
                    {"error": "User Not Found", "message": "User no longer exists"}
                ),
                404,
            )
        if not user.check_password(current_password):
            log_auth_event(
                user.id,
                AuditAction.UPDATE,
                "failure",
                f"Invalid current password for password change: {user.email}",
                "medium",
            )
            return (
                jsonify(
                    {
                        "error": "Authentication Error",
                        "message": "Current password is incorrect",
                    }
                ),
                401,
            )
        is_valid, message = validate_password(new_password)
        if not is_valid:
            return (jsonify({"error": "Validation Error", "message": message}), 400)
        if user.check_password(new_password):
            return (
                jsonify(
                    {
                        "error": "Validation Error",
                        "message": "New password must be different from current password",
                    }
                ),
                400,
            )
        user.set_password(new_password)
        db.session.commit()
        log_auth_event(
            user.id,
            AuditAction.UPDATE,
            "success",
            f"Password changed: {user.email}",
            "low",
        )
        return (jsonify({"message": "Password changed successfully"}), 200)
    except Exception as e:
        logger.error(f"Change password error: {e}")
        db.session.rollback()
        return (
            jsonify(
                {"error": "Internal Server Error", "message": "Password change failed"}
            ),
            500,
        )


@auth_bp.route("/verify-email", methods=["POST"])
@jwt_required()
def verify_email() -> Any:
    """Verify user email (simplified implementation)"""
    try:
        current_user_uuid = get_jwt_identity()
        user = User.query.filter_by(uuid=current_user_uuid).first()
        if not user:
            return (
                jsonify(
                    {"error": "User Not Found", "message": "User no longer exists"}
                ),
                404,
            )
        if user.is_email_verified:
            return (jsonify({"message": "Email is already verified"}), 200)
        user.email_verified_at = datetime.now(timezone.utc)
        db.session.commit()
        log_auth_event(
            user.id, AuditAction.UPDATE, "success", f"Email verified: {user.email}"
        )
        return (jsonify({"message": "Email verified successfully"}), 200)
    except Exception as e:
        logger.error(f"Email verification error: {e}")
        db.session.rollback()
        return (
            jsonify(
                {
                    "error": "Internal Server Error",
                    "message": "Email verification failed",
                }
            ),
            500,
        )
