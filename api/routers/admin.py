from fastapi import APIRouter, Depends, HTTPException, status
from schemas.students import Student
from schemas.recognition_logs import RecognitionLog
from schemas.admin_users import AdminUser, AdminUserUpdate
from schemas.responses import HTTPResponse
from crud.students import get_all_students
from crud.recognition_logs import get_recognition_logs
from crud.admin_users import update_admin_user, delete_admin_user, get_all_admin_users
from crud.colleges import get_all_colleges
from crud.departments import get_all_departments
from api.dependencies import get_current_admin
from models.database import supabase
from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["👤 Admin"])

@router.get("/stats", response_model=HTTPResponse[Dict], 
            summary="Comprehensive Dashboard Stats", description="Get complete dashboard statistics (Admin only)")
async def get_admin_stats(_=Depends(get_current_admin)):
    """Retrieve comprehensive admin dashboard statistics."""
    try:
        # Get all counts
        students = await get_all_students()
        colleges = await get_all_colleges()
        departments = await get_all_departments()
        admin_users = await get_all_admin_users()
        all_logs = await get_recognition_logs()
        
        # Calculate date ranges
        seven_days_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        recent_logs = await get_recognition_logs(start_date=seven_days_ago)
        monthly_logs = await get_recognition_logs(start_date=thirty_days_ago)
        
        # Calculate success rate from recent logs
        successful_recent = sum(1 for log in recent_logs if log.success)
        success_rate = (successful_recent / len(recent_logs) * 100) if recent_logs else 0
        
        stats = {
            "total_students": len(students),
            "total_colleges": len(colleges),
            "total_departments": len(departments),
            "total_admins": len(admin_users),
            "total_recognitions": len(all_logs),
            "recent_recognitions": len(recent_logs),
            "monthly_recognitions": len(monthly_logs),
            "recognition_success_rate": round(success_rate, 2),
            "system_health": "healthy" if success_rate > 80 else "needs_attention"
        }
        
        logger.info("Comprehensive admin stats retrieved")
        return HTTPResponse(
            message="Dashboard statistics retrieved successfully",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[stats]
        )
    except Exception as e:
        logger.error(f"Error retrieving admin stats: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve stats")

@router.get("/students", response_model=HTTPResponse[Student],
            summary="List All Students (Admin)", description="Get all students for admin dashboard")
async def list_all_students(_=Depends(get_current_admin)):
    """Retrieve all students for admin."""
    result = await get_all_students()
    return HTTPResponse(
        message="All students retrieved successfully",
        status_code=status.HTTP_200_OK,
        count=len(result),
        data=result
    )

@router.get("/recognition-logs", response_model=HTTPResponse[RecognitionLog],
            summary="Get Recognition Logs", description="Get recognition logs with optional filters (Admin only)")
async def list_recognition_logs(
    student_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    _=Depends(get_current_admin)
):
    """Retrieve recognition logs with optional filters."""
    result = await get_recognition_logs(student_id, start_date, end_date)
    message = "Recognition logs retrieved successfully"
    if student_id:
        message = f"Recognition logs for student {student_id} retrieved successfully"
    
    return HTTPResponse(
        message=message,
        status_code=status.HTTP_200_OK,
        count=len(result),
        data=result
    )

@router.put("/{admin_id}", response_model=HTTPResponse[AdminUser])
async def update_admin_details(admin_id: UUID, admin: AdminUserUpdate, _=Depends(get_current_admin)):
    """Update an admin user's details."""
    result = await update_admin_user(admin_id, admin)
    return HTTPResponse(
        message="Admin user updated successfully",
        status_code=status.HTTP_200_OK,
        count=1,
        data=[result]
    )

@router.delete("/{admin_id}", response_model=HTTPResponse[None])
async def delete_admin_user_record(admin_id: UUID, _=Depends(get_current_admin)):
    """Delete an admin user by ID."""
    await delete_admin_user(admin_id)
    return HTTPResponse(
        message="Admin user deleted successfully",
        status_code=status.HTTP_204_NO_CONTENT,
        count=0,
        data=None
    )

@router.get("/analytics/registration-trends", response_model=HTTPResponse[Dict],
            summary="Registration Trends", description="Get student registration trends over time (Admin only)")
async def get_registration_trends(_=Depends(get_current_admin)):
    """Get student registration trends for charts."""
    try:
        students = await get_all_students()
        
        # Group students by registration date (by month)
        monthly_counts = defaultdict(int)
        daily_counts = defaultdict(int)
        
        for student in students:
            if student.created_at:
                # Parse the datetime string
                created_date = datetime.fromisoformat(student.created_at.replace('Z', '+00:00'))
                month_key = created_date.strftime('%Y-%m')
                day_key = created_date.strftime('%Y-%m-%d')
                monthly_counts[month_key] += 1
                daily_counts[day_key] += 1
        
        # Get last 12 months and last 30 days
        monthly_data = dict(sorted(monthly_counts.items())[-12:])
        daily_data = dict(sorted(daily_counts.items())[-30:])
        
        trends = {
            "monthly_registrations": monthly_data,
            "daily_registrations": daily_data,
            "total_students": len(students),
            "avg_monthly_registrations": sum(monthly_data.values()) / max(len(monthly_data), 1)
        }
        
        return HTTPResponse(
            message="Registration trends retrieved successfully",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[trends]
        )
    except Exception as e:
        logger.error(f"Error retrieving registration trends: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve trends")

@router.get("/analytics/college-distribution", response_model=HTTPResponse[Dict],
            summary="College Distribution", description="Get student distribution by college (Admin only)")
async def get_college_distribution(_=Depends(get_current_admin)):
    """Get student distribution across colleges for pie chart."""
    try:
        students = await get_all_students()
        colleges = await get_all_colleges()
        
        # Create college name mapping
        college_names = {str(college.id): college.name for college in colleges}
        
        # Count students by college
        college_counts = Counter()
        for student in students:
            college_id = str(student.college_id)
            college_name = college_names.get(college_id, f"Unknown College ({college_id[:8]})")
            college_counts[college_name] += 1
        
        # Calculate percentages
        total_students = len(students)
        distribution = []
        for college_name, count in college_counts.items():
            percentage = (count / total_students * 100) if total_students > 0 else 0
            distribution.append({
                "college_name": college_name,
                "student_count": count,
                "percentage": round(percentage, 2)
            })
        
        # Sort by count descending
        distribution.sort(key=lambda x: x["student_count"], reverse=True)
        
        result = {
            "college_distribution": distribution,
            "total_students": total_students,
            "total_colleges": len(colleges),
            "colleges_with_students": len([d for d in distribution if d["student_count"] > 0])
        }
        
        return HTTPResponse(
            message="College distribution retrieved successfully",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[result]
        )
    except Exception as e:
        logger.error(f"Error retrieving college distribution: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve distribution")

@router.get("/analytics/department-enrollment", response_model=HTTPResponse[Dict],
            summary="Department Enrollment", description="Get student enrollment by department (Admin only)")
async def get_department_enrollment(_=Depends(get_current_admin)):
    """Get student enrollment across departments for bar chart."""
    try:
        students = await get_all_students()
        departments = await get_all_departments()
        
        # Create department name mapping with college info
        dept_info = {}
        for dept in departments:
            dept_info[str(dept.id)] = {
                "name": dept.name,
                "college_name": dept.college_name or "Unknown College"
            }
        
        # Count students by department
        dept_counts = Counter()
        for student in students:
            if student.department_id:
                dept_id = str(student.department_id)
                dept_data = dept_info.get(dept_id)
                if dept_data:
                    dept_key = f"{dept_data['name']} ({dept_data['college_name']})"
                    dept_counts[dept_key] += 1
        
        # Prepare enrollment data
        enrollment = []
        for dept_name, count in dept_counts.items():
            enrollment.append({
                "department_name": dept_name,
                "student_count": count,
                "enrollment_rate": round((count / len(students) * 100), 2) if students else 0
            })
        
        # Sort by enrollment descending
        enrollment.sort(key=lambda x: x["student_count"], reverse=True)
        
        result = {
            "department_enrollment": enrollment,
            "total_students": len(students),
            "total_departments": len(departments),
            "departments_with_students": len(enrollment),
            "avg_enrollment_per_dept": len(students) / max(len(departments), 1)
        }
        
        return HTTPResponse(
            message="Department enrollment retrieved successfully",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[result]
        )
    except Exception as e:
        logger.error(f"Error retrieving department enrollment: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve enrollment")

@router.get("/analytics/system-health", response_model=HTTPResponse[Dict],
            summary="System Health Metrics", description="Get system performance and health metrics (Admin only)")
async def get_system_health(_=Depends(get_current_admin)):
    """Get system health and performance metrics."""
    try:
        students = await get_all_students()
        colleges = await get_all_colleges()
        departments = await get_all_departments()
        
        # Get recognition logs for different time periods
        now = datetime.utcnow()
        one_day_ago = (now - timedelta(days=1)).isoformat()
        seven_days_ago = (now - timedelta(days=7)).isoformat()
        thirty_days_ago = (now - timedelta(days=30)).isoformat()
        
        daily_logs = await get_recognition_logs(start_date=one_day_ago)
        weekly_logs = await get_recognition_logs(start_date=seven_days_ago)
        monthly_logs = await get_recognition_logs(start_date=thirty_days_ago)
        
        # Calculate success rates
        daily_success = sum(1 for log in daily_logs if log.success)
        weekly_success = sum(1 for log in weekly_logs if log.success)
        monthly_success = sum(1 for log in monthly_logs if log.success)
        
        daily_success_rate = (daily_success / len(daily_logs) * 100) if daily_logs else 0
        weekly_success_rate = (weekly_success / len(weekly_logs) * 100) if weekly_logs else 0
        monthly_success_rate = (monthly_success / len(monthly_logs) * 100) if monthly_logs else 0
        
        # Calculate coverage rates
        college_coverage = len(colleges) / max(len(colleges), 1) * 100  # All colleges exist
        department_coverage = len(departments) / max(len(departments), 1) * 100  # All departments exist
        
        # Calculate activity levels
        daily_activity = len(daily_logs)
        weekly_activity = len(weekly_logs) / 7  # avg per day
        monthly_activity = len(monthly_logs) / 30  # avg per day
        
        # Determine overall health status
        avg_success_rate = (daily_success_rate + weekly_success_rate + monthly_success_rate) / 3
        health_status = "excellent" if avg_success_rate > 90 else \
                       "good" if avg_success_rate > 80 else \
                       "fair" if avg_success_rate > 60 else "poor"
        
        health_metrics = {
            "overall_health": health_status,
            "success_rates": {
                "daily": round(daily_success_rate, 2),
                "weekly": round(weekly_success_rate, 2),
                "monthly": round(monthly_success_rate, 2),
                "average": round(avg_success_rate, 2)
            },
            "activity_levels": {
                "daily_recognitions": daily_activity,
                "avg_weekly_daily": round(weekly_activity, 2),
                "avg_monthly_daily": round(monthly_activity, 2)
            },
            "coverage_metrics": {
                "college_coverage": round(college_coverage, 2),
                "department_coverage": round(department_coverage, 2),
                "student_registration_rate": len(students)  # Could be compared to expected
            },
            "system_utilization": {
                "total_students": len(students),
                "active_colleges": len(colleges),
                "active_departments": len(departments),
                "recognition_events": len(monthly_logs)
            }
        }
        
        return HTTPResponse(
            message="System health metrics retrieved successfully",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[health_metrics]
        )
    except Exception as e:
        logger.error(f"Error retrieving system health: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve health metrics")

@router.get("/users/count", response_model=HTTPResponse[Dict],
            summary="Admin User Count", description="Get total number of admin users (Admin only)")
async def get_admin_count(_=Depends(get_current_admin)):
    """Get total count of admin users."""
    try:
        admin_users = await get_all_admin_users()
        verified_admins = sum(1 for admin in admin_users if admin.is_verified)
        
        count_data = {
            "total_admins": len(admin_users),
            "verified_admins": verified_admins,
            "unverified_admins": len(admin_users) - verified_admins
        }
        
        return HTTPResponse(
            message="Admin count retrieved successfully",
            status_code=status.HTTP_200_OK,
            count=1,
            data=[count_data]
        )
    except Exception as e:
        logger.error(f"Error retrieving admin count: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve admin count")