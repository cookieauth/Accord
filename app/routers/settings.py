#@router.get("/settings", name="settings", response_class=HTMLResponse)
#async def settings(request: Request, user: models.User = Depends(has_permission(["admin"]))):
#   return templates.TemplateResponse("admin/settings.html", {"request": request, "user": user})