# app/routers/muster_reports.py
from datetime import datetime

from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from starlette.responses import RedirectResponse

from app import models, schemas, crud
from app.auth import has_permission

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/muster_reports", tags=["Muster Reports"])

@router.get("/submit", response_class=HTMLResponse)
async def submit_muster_form(request: Request, current_user: models.User = Depends(has_permission(["department"]))):
    async with crud.async_session() as session:
        result = await session.execute(select(models.Personnel).where(models.Personnel.department_id == current_user.department_id))
        personnel = result.scalars().all()
    return templates.TemplateResponse("muster_reports/submit_muster.html", {"request": request, "personnel": personnel, "user": current_user})

@router.post("/submit", response_model=schemas.MusterReportRead)
async def submit_muster_report(
    request: Request,
    current_user: models.User = Depends(has_permission(["department"])),
):
    form = await request.form()
    date_str = form.get("date")
    if not date_str:
        raise HTTPException(status_code=400, detail="Date is required.")
    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

    # Extract personnel statuses
    personnel_statuses = []
    for key in form.keys():
        if key.startswith("personnel_statuses-"):
            personnel_id = int(key.split("-")[1])
            status = form.get(key)
            if status not in [status.value for status in models.StatusEnum]:
                raise HTTPException(status_code=400, detail=f"Invalid status for personnel ID {personnel_id}.")
            personnel_statuses.append(models.PersonnelStatusCreate(personnel_id=personnel_id, status=status))

    report = models.MusterReportCreate(date=date_obj, personnel_statuses=personnel_statuses)
    muster_report = await models.submit_muster_report(report=report, current_user=current_user)

    # Optionally, notify HR about the new submission
    # (Ensure the `send_email` function is defined and imported)
    # async with crud.async_session() as session:
    #     hr_users = await session.execute(
    #         select(models.User).where(models.User.role == "hr")
    #     )
    #     hr_users = hr_users.scalars().all()
    #     for hr in hr_users:
    #         if hr.email:
    #             await auth.send_email(
    #                 to=hr.email,
    #                 subject="New Muster Report Submitted",
    #                 body=f"Dear {hr.username},\n\nA new muster report has been submitted by {current_user.username} for the {current_user.department.name} department.\n\nDate: {date_obj}\n\nPlease review the report at your earliest convenience.\n\nThank you!"
    #             )

    return muster_report

@router.get("/", response_class=HTMLResponse)
async def get_muster_reports(
    request: Request,
    current_user: models.User = Depends(has_permission(["department"])),
):
    async with crud.async_session() as session:
        if current_user.role == "department":
            result = await session.execute(
                select(models.MusterReport)
                .where(models.MusterReport.department_id == current_user.department_id)
                .order_by(models.MusterReport.date.desc())
                .options(selectinload(models.MusterReport.personnel_statuses))
            )
        else:
            result = await session.execute(select(models.MusterReport))
        reports = result.scalars().all()
    return templates.TemplateResponse("muster_reports/muster_reports.html", {"request": request, "reports": reports, "user": current_user})

@router.get("/pending", name="view_pending_muster_reports", response_class=HTMLResponse)
async def view_pending_muster_reports(
    request: Request,
    current_user: models.User = Depends(has_permission(["admin", "hr"]))
):
    async with crud.async_session() as session:
        reports = (await session.execute(
            select(models.MusterReport)
            .where(models.MusterReport.status == schemas.ReportStatusEnum.PENDING)
            .options(
                selectinload(models.MusterReport.department),
                selectinload(models.MusterReport.submitted_by)
            )
        )).scalars().all()
    return templates.TemplateResponse(
        "muster_reports/pending_reports.html",
        {"request": request, "reports": reports, "user": current_user},
    )

@router.get("/review/{report_id}", name="review_muster_report", response_class=HTMLResponse)
async def review_muster_report(
    request: Request,
    report_id: int,
    current_user: models.User = Depends(has_permission(["admin", "hr"]))
):
    async with crud.async_session() as session:
        report = (await session.execute(
            select(models.MusterReport)
            .where(models.MusterReport.id == report_id)
            .options(
                selectinload(models.MusterReport.department),
                selectinload(models.MusterReport.submitted_by),
                selectinload(models.MusterReport.personnel_statuses)
                .selectinload(models.PersonnelStatus.personnel)
            )
        )).scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Muster report not found")
    return templates.TemplateResponse(
        "muster_reports/review_report.html",
        {"request": request, "user": current_user, "report": report}
    )

@router.post("/review/{report_id}", name="review_muster_report", response_class=HTMLResponse)
async def review_muster_report(
    report_id: int,
    review: schemas.ReviewMusterReport,
    current_user: models.User = Depends(has_permission(["hr"])),
):
    async with crud.async_session() as session:
        result = await session.execute(select(models.MusterReport).where(models.MusterReport.id == report_id))
        muster_report = result.scalars().first()
        if not muster_report:
            raise HTTPException(status_code=404, detail="Muster report not found.")

        if muster_report.status != models.ReportStatusEnum.PENDING:
            raise HTTPException(status_code=400, detail="Muster report already reviewed.")

        muster_report.status = review.status
        await session.commit()
        await session.refresh(muster_report)
        return muster_report

@router.post("/archive/{report_id}", name="archive_muster_report")
async def archive_muster_report(
    report_id: int,
    current_user: models.User = Depends(has_permission(["admin", "hr"]))
):
    async with crud.async_session() as session:
        report = (await session.execute(
            select(models.MusterReport).where(models.MusterReport.id == report_id)
        )).scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Muster report not found")
        report.archived = True
        report.archived_at = datetime.utcnow()
        await session.commit()
    return RedirectResponse(
        url=router.url_path_for("view_muster_reports"), status_code=303
    )

@router.get("/archived", response_class=HTMLResponse)
async def get_archived_muster_reports(
    request: Request,
    current_user: models.User = Depends(has_permission(["hr"])),
):
    async with crud.async_session() as session:
        result = await session.execute(
            select(models.MusterReport)
            .where(models.MusterReport.archived == True)
            .order_by(models.MusterReport.date.desc())
            .options(selectinload(models.MusterReport.personnel_statuses))
        )
        reports = result.scalars().all()
    return templates.TemplateResponse("muster_reports/archived_muster_reports.html", {"request": request, "reports": reports, "user": current_user})

@router.post("/review/{report_id}", name="review_muster_report")
async def process_review_muster_report(
    report_id: int,
    action: str = Form(...),  # 'approve' or 'reject'
    user: models.User = Depends(has_permission(["admin", "hr"]))
):
    async with crud.async_session() as session:
        report = (await session.execute(
            select(models.MusterReport).where(models.MusterReport.id == report_id)
        )).scalar_one_or_none()
        if not report:
            raise HTTPException(status_code=404, detail="Muster report not found")
        if action == 'approve':
            report.status = schemas.ReportStatusEnum.APPROVED
        elif action == 'reject':
            report.status = schemas.ReportStatusEnum.REJECTED
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        await session.commit()
        # Create a notification for the submitter
        notification = models.Notification(
            user_id=report.submitted_by_id,
            message=f"Your muster report dated {report.date} has been {report.status.value.lower()}."
        )
        session.add(notification)
        await session.commit()
    return RedirectResponse(
        url=router.url_path_for("view_pending_muster_reports"), status_code=303
    )

@router.get("/muster_reports", name="view_muster_reports", response_class=HTMLResponse)
async def view_muster_reports(request: Request, current_user: models.User = Depends(has_permission(["admin"]))):
    async with crud.async_session() as session:
        result = await session.execute(
            select(models.MusterReport)
            .options(selectinload(models.MusterReport.department), selectinload(models.MusterReport.submitted_by))
        )
        muster_reports = result.scalars().all()
    return templates.TemplateResponse("muster_reports/view_muster_reports.html", {"request": request, "user": current_user, "muster_reports": muster_reports})
