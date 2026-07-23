import React, { useEffect, useState } from "react";

import SidebarHeader from "./SidebarHeader";
import SidebarMenu from "./SidebarMenu";
import SidebarFooter from "./SidebarFooter";
import LogoutDialog from "./LogoutDialog";

import type { SidebarUser } from "./types";

import "./Sidebar.css";

interface SidebarProps {
    user?: SidebarUser;
    onLogout?: () => Promise<void> | void;
    onSettings?: () => void;
    onHelp?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({
    user,
    onLogout,
    onSettings,
    onHelp
}) => {

    const [collapsed, setCollapsed] = useState(
        localStorage.getItem("sidebarCollapsed") === "true"
    );

    const [logoutOpen, setLogoutOpen] = useState(false);

    const [loggingOut, setLoggingOut] = useState(false);



    useEffect(() => {
        localStorage.setItem(
            "sidebarCollapsed",
            collapsed.toString()
        );
    }, [collapsed]);

    /**
     * Collapse / Expand
     */
    const toggleSidebar = () => {
        setCollapsed(prev => !prev);
    };

    /**
     * Logout
     */
    const confirmLogout = async () => {

        try {

            setLoggingOut(true);

            if (onLogout) {

                await onLogout();

            } else {

                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
                sessionStorage.clear();

                window.location.href = "/login";

            }

        } finally {

            setLoggingOut(false);
            setLogoutOpen(false);

        }

    };

    return (
        <>

            <aside
                className={`sidebar ${collapsed ? "collapsed" : ""}`}
            >

                <SidebarHeader
                    collapsed={collapsed}
                    onToggle={toggleSidebar}
                />

                <SidebarMenu
                    collapsed={collapsed}
                />



            </aside>


        </>
    );
};

export default Sidebar;