#@router.get("/audit_logs", name="view_audit_logs", response_class=HTMLResponse)
#async def view_audit_logs(request: Request, user: models.User = Depends(has_permission(["admin"]))):
#    async with crud.async_session() as session:
#        result = await session.execute(select(models.AuditLog))
#        audit_logs = result.scalars().all()
#    return templates.TemplateResponse("admin/audit_logs.html", {"request": request, "user": user, "audit_logs": audit_logs})
