from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class MenuItemResponse(BaseModel):
    id: str
    label: str
    label_fa: str
    icon_name: str
    route: str
    is_bottom_section: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "id": "patients",
                "label": "Patients",
                "label_fa": "بیماران",
                "icon_name": "FiUsers",
                "route": "/patients",
                "is_bottom_section": False,
            }
        }


@router.get("/menu", response_model=List[MenuItemResponse])
def get_navigation_menu():
    """
    Returns the navigation menu structure for the sidebar.
    This endpoint provides all menu items with their labels, icons, and routes.
    """
    menu_items = [
        MenuItemResponse(
            id="get-started",
            label="Get started",
            label_fa="شروع",
            icon_name="FiLayout",
            route="/",
            is_bottom_section=False,
        ),
        MenuItemResponse(
            id="calendar",
            label="Calendar",
            label_fa="تقویم",
            icon_name="FiCalendar",
            route="/appointments",
            is_bottom_section=False,
        ),
        MenuItemResponse(
            id="inbox",
            label="Inbox",
            label_fa="صندوق ورودی",
            icon_name="FiInbox",
            route="/inbox",
            is_bottom_section=False,
        ),
        MenuItemResponse(
            id="clients",
            label="Clients",
            label_fa="بیماران",
            icon_name="FiUsers",
            route="/patients",
            is_bottom_section=False,
        ),
        MenuItemResponse(
            id="billing",
            label="Billing",
            label_fa="صورتحساب",
            icon_name="FiDollarSign",
            route="/billing",
            is_bottom_section=False,
        ),
        MenuItemResponse(
            id="team",
            label="Your team",
            label_fa="تیم شما",
            icon_name="FiBriefcase",
            route="/team",
            is_bottom_section=False,
        ),
        MenuItemResponse(
            id="contacts",
            label="Contacts",
            label_fa="مخاطبین",
            icon_name="FiFileText",
            route="/contacts",
            is_bottom_section=False,
        ),
        MenuItemResponse(
            id="templates",
            label="Templates",
            label_fa="قالب‌ها",
            icon_name="FiFile",
            route="/templates",
            is_bottom_section=False,
        ),
        MenuItemResponse(
            id="workflows",
            label="Workflows",
            label_fa="گردش کار",
            icon_name="FiGitBranch",
            route="/workflows",
            is_bottom_section=False,
        ),
        MenuItemResponse(
            id="settings",
            label="Settings",
            label_fa="تنظیمات",
            icon_name="FiSettings",
            route="/settings",
            is_bottom_section=False,
        ),
        # Footer items
        MenuItemResponse(
            id="invite",
            label="Invite",
            label_fa="دعوت",
            icon_name="FiUserPlus",
            route="/invite",
            is_bottom_section=True,
        ),
        MenuItemResponse(
            id="help",
            label="Help",
            label_fa="راهنما",
            icon_name="FiHelpCircle",
            route="/help",
            is_bottom_section=True,
        ),
    ]
    return menu_items
