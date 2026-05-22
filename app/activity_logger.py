from app.model import AdminActivityLog


def record_admin_activity(
    db,
    action: str,
    target_type: str = "Employee",
    target_name: str = "",
    employee_id: str = None,
    admin_name: str = "John Administrator",
    **kwargs
):
    log = AdminActivityLog(
        action=action,
        target_type=target_type,
        target_name=target_name,
        employee_id=employee_id,
        admin_name=admin_name
    )

    db.add(log)
    db.commit()