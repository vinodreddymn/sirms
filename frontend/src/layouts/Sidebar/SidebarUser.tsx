import React from "react";
import { Mail } from "lucide-react";

import type { SidebarUser as SidebarUserModel } from "./types";


interface SidebarUserProps {
    user: SidebarUserModel;
    collapsed: boolean;
}

const SidebarUser: React.FC<SidebarUserProps> = ({
    user,
    collapsed,
}) => {

    /**
     * User initials
     */
    const initials = user.name
        .split(" ")
        .map(name => name.charAt(0))
        .slice(0, 2)
        .join("")
        .toUpperCase();

    return (

        <div
            className="sidebar-user"
            title={collapsed ? user.name : ""}
        >

            {/* Avatar */}

            {

                user.avatar ? (

                    <img
                        src={user.avatar}
                        alt={user.name}
                        className="sidebar-avatar"
                    />

                ) : (

                    <div className="sidebar-avatar-placeholder">

                        {initials}

                    </div>

                )

            }

            {/* User Details */}

            {

                !collapsed && (

                    <div className="sidebar-user-details">

                        <div className="sidebar-user-header">

                            <span className="sidebar-user-name">

                                {user.name}

                            </span>

                            <span
                                className="sidebar-online-indicator"
                                title="Online"
                            />

                        </div>

                        <div className="sidebar-user-designation">

                            {user.designation}

                        </div>

                        <div className="sidebar-user-email">

                            <Mail size={13} />

                            <span>

                                {user.email}

                            </span>

                        </div>

                    </div>

                )

            }

        </div>

    );

};

export default SidebarUser;