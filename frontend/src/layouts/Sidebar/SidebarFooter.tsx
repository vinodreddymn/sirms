import React from "react";
import {
    Settings,
    HelpCircle,
    LogOut
} from "lucide-react";

import SidebarUser from "./SidebarUser";
import type { SidebarUser as SidebarUserModel } from "./types";

interface SidebarFooterProps {

    collapsed: boolean;

    user: SidebarUserModel;

    onSettings: () => void;

    onHelp: () => void;

    onLogout: () => void;

}

const SidebarFooter: React.FC<SidebarFooterProps> = ({

    collapsed,

    user,

    onSettings,

    onHelp,

    onLogout

}) => {

    return (

        <footer className="sidebar-footer">

            <SidebarUser
                user={user}
                collapsed={collapsed}
            />

            <div className="sidebar-footer-actions">

                {/* SETTINGS */}

                <button

                    type="button"

                    className="footer-button"

                    onClick={onSettings}

                    title={collapsed ? "Settings" : ""}

                >

                    <Settings size={18} />

                    {

                        !collapsed &&

                        <span>

                            Settings

                        </span>

                    }

                </button>

                {/* HELP */}

                <button

                    type="button"

                    className="footer-button"

                    onClick={onHelp}

                    title={collapsed ? "Help" : ""}

                >

                    <HelpCircle size={18} />

                    {

                        !collapsed &&

                        <span>

                            Help

                        </span>

                    }

                </button>

                {/* LOGOUT */}

                <button

                    type="button"

                    className="footer-button logout"

                    onClick={onLogout}

                    title={collapsed ? "Logout" : ""}

                >

                    <LogOut size={18} />

                    {

                        !collapsed &&

                        <span>

                            Logout

                        </span>

                    }

                </button>

            </div>

        </footer>

    );

};

export default SidebarFooter;