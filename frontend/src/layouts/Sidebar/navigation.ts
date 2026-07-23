import {
    LayoutDashboard,
    Building2,
    Boxes,
    AlertTriangle,
    Wrench,
    FileText,
    Package,
    PieChart,
    Settings,
    Shield,
    Users,
    ClipboardList,
    Database,
    Network
} from "lucide-react";

import type { SidebarSection } from "./types";

/**
 * Enterprise Sidebar Navigation
 * SIRMS v1.0
 */

export const navigation: SidebarSection[] = [

    /* ---------------------------------------------------------
       Dashboard
    ----------------------------------------------------------*/

    {
        id: "dashboard",
        label: "Dashboard",
        icon: LayoutDashboard,
        path: "/"
    },

    /* ---------------------------------------------------------
       Infrastructure
    ----------------------------------------------------------*/

    {
        id: "infrastructure",
        label: "Infrastructure",
        icon: Building2,
        path: "/infrastructure"

    },

    /* ---------------------------------------------------------
       Assets
    ----------------------------------------------------------*/

    {
        id: "assets",

        label: "Assets",

        icon: Boxes,
        path: "/assets"


    },

    /* ---------------------------------------------------------
       Incidents
    ----------------------------------------------------------*/

    {
        id: "incidents",

        label: "Incidents",

        icon: AlertTriangle,
        path: "/incidents"

    },

    /* ---------------------------------------------------------
       Maintenance
    ----------------------------------------------------------*/

    {
        id: "maintenance",

        label: "Maintenance",

        icon: Wrench,

        path: "/Maintenance",

    
    },

    /* ---------------------------------------------------------
       Daily Work
    ----------------------------------------------------------*/

    {
        id: "daily-work",

        label: "Daily Work Log",

        icon: ClipboardList,

        path: "/daily-work-log"
    },


    /* ---------------------------------------------------------
       Reports
    ----------------------------------------------------------*/

    {
        id: "reports",

        label: "Reports",

        icon: PieChart,

        path: "/reports"
    },

    /* ---------------------------------------------------------
       Security
    ----------------------------------------------------------*/

    {
        id: "security",

        label: "Security",

        icon: Shield,

        permission: "security:view",

        children: [

            {
                id: "users",

                label: "Users",

                path: "/security/users"
            },

            {
                id: "roles",

                label: "Roles",

                path: "/security/roles"
            },

            {
                id: "audit",

                label: "Login History",

                path: "/security/audit"
            }

        ]
    },

    /* ---------------------------------------------------------
       Administration
    ----------------------------------------------------------*/

    {
        id: "administration",

        label: "Administration",

        icon: Settings,

        children: [

            {
                id: "master-data",

                label: "Master Data",

                path: "/master"
            },

            {
                id: "asset-specifications",

                label: "Specifications",

                path: "/master/specifications"
            },

            {
                id: "position-templates",

                label: "Position Templates",

                path: "/master/position-templates"
            },



        ]
    }

];